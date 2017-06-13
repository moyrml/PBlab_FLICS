from __future__ import division

import numpy as np
from scipy import misc
from matplotlib import pyplot as plt

t_line = input('How long does it take to scan a row? ')
f_line = 1/t_line

im_name = input('What is the image name? ("copy pathname: /.../file_name.png") ')
#image name = file_name.png

im = misc.imread(im_name , flatten=True)

l = input('What is the distance between two columns? ([,,,]) ')
