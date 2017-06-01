import numpy as np
import math
from scipy import misc
from matplotlib import pyplot as plt

im = misc.imread('./samples/sample_input_2.jpg', flatten=True)

# im.shape = (y,x)
# artificialy setting image parameters
dx = 0.08e-6
gamma = 0
fline = 1400
Tline = 1.0/fline

#integrates over two column
def g2(x,l,tau,im):
    if x+l >= im.shape[1]:
        return False
    #compute average colum intensity
    avg_x = np.average(im[:,x])
    avg_xl = np.average(im[:,x+l])
    
    df12 = []    
    for i in range(im[:,x].shape[0]):
        if i+tau >= im.shape[0]:
            continue
        
        df1 = im[i,x] - avg_x
        df2 = im[i+tau,x+l] - avg_xl
        
        df12.append(df1*df2)
        
    if not df12:
        return False
        
    N = sum(df12)/len(df12)
    D = avg_x*avg_xl
    return N/D

#integrates over all columns ang returns Gij average
def g_op(im,l,tau):

    g2_values = []
    for i in range(im.shape[1]):
        temp = g2(i,l,tau,im)
        if temp == False:
            continue
        g2_values.append(temp)
    if len(g2_values)==0:
        return 0
    return sum(g2_values)/float(len(g2_values))

#drive the g_op function and output plot matrix
#tau is the vertical time delay between two pixels
# we expect the connetcion between tau and pixel number to be:
# tau = L* t_time_per_pixel + N * t_time_per_line
# N being the distance on the y axis
# L being the distance on the x axis
# t_time_per_pixel is typically us and t_time_per_line is typically ms
# L* t_time_per_pixel is negligable
def G_driver(im,l):
    global Tline
    out_x = []
    out_y = []
    for N in range(1,25):
        temp = g_op(im,l,N)
        if not temp:
            continue
        out_x.append(N*Tline)
        out_y.append(temp)
    return out_x, out_y

# this is function that gives something nice to look at.
def plot_results():
    sets = [[10,"-+"],[30,"-o"],[60,"-."],[90,"-x"],[120,"-s"],[150,"-d"]]
    #sets = [[50,"x"]]
    plots = []
    for set_ in sets:
        data_x,data_y = G_driver(im,set_[0])
    #    for obj in data:
    #        plt.scatter(obj[0],obj[1], marker=set_[1])
        line, = plt.plot(data_x,data_y, set_[1], label=str(set_[0]))
        plots.append(line)
    plt.legend(handles=plots)

## CALCULATE VELOCITY
# V get two lists of results and a distance (I-J)
# and outputs a |V| according to eqn 4
# for now, tau_0_max will just be the maximum of the y list

# note that speeds below 100 um/s are considered very low.
# the article uses D = 0 for analysis. for gamma=60deg, the 
# error in velocity is ~30%. for gamma=0deg the error reduces to ~3%.
# it is predicted that for D=0, the speeds obtained will be higher than 
# in reality.

def V(x,y,l):
    print dx, gamma, Tline
    tau_max = x[y.index(max(y))]

    # this is where we could get wierd behaviour due to 
    # python being limited with accuracy by default.
    # It may be necessary to increase the accuracy down the road,
    # or use precision calculation libraries.

    # setting some helper variables
    a = l*dx*math.cos(gamma)
    b = dx/Tline
    c = math.sin(gamma)
    d = math.cos(gamma)
    
    A = a+2*c*b*tau_max
    delta = (A)**2-4*(tau_max**2)*(b**2)
    
    v1 = (A+math.sqrt(delta))/(2*tau_max)
    v2 = (A-math.sqrt(delta))/(2*tau_max)

    ### V0 uncertainty according to S.41, S.42
    ddeltadtaumax = 4*b*c*(2*b*c*tau_max+a) -8*tau_max*(b**2)
    in_sigma1 = ((-1*(2*a+math.sqrt(delta)-tau_max*delta*ddeltadtaumax)/(4*tau_max**2))**2)*((Tline/2)**2)
    in_sigma2 = ((-1*(2*a-math.sqrt(delta)+tau_max*delta*ddeltadtaumax)/(4*tau_max**2))**2)*((Tline/2)**2)
    dv1 = math.sqrt(in_sigma1)
    dv2 = math.sqrt(in_sigma2)
    ## TO DO: 
    # 3. find out how to dismiss one of the v's
    # 4. find out why the ridiculusly small v gets the better error...

    return v1,dv1, v2,dv2

def VG_driver(im,l):
    x, y = G_driver(im, l)
    try:
        v1,dv1 ,v2,dv2 = V(x,y,l)
    except ValueError as e:
        print e
        return
    
    print v1,dv1, v2,dv2
