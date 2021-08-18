import cv2
import numpy as np 
import re as regex
import sys
import os

from numpy.core.numeric import full 


filename = sys.argv[1]
proj_dir = sys.argv[2]
full_path = f'{proj_dir}/images/{filename}'
filename = os.path.splitext(filename)[0]
original_image = np.load(full_path)
gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
img_num = regex.findall(r'[0-9]+', filename)[0]
full_path = f'{proj_dir}/images/{filename}.jpeg'
cv2.imwrite(full_path,gray_image)