import cv2
import numpy as np
from matplotlib import pyplot as plt  
import matplotlib
from time import sleep

def find_peaks(vals,zeros,fraction):
    
    white_shift = np.max(vals)*fraction
    black_shift = np.min(vals)*fraction
    current_index = 0 
    offset = 0 
    shrink = 0 
    peaks = []
    while True:
        vals = vals[shrink:]
        direction = 1
        #print(f'next whiteshift= { np.argmax(vals > white_shift)} next bkaj shift {np.argmax(vals <  black_shift)}')
        if (np.argmax(vals > white_shift) < np.argmax(vals <  black_shift)):
            temp = np.argmax(vals > white_shift)
            if (temp != 0): 
                current_index = np.argmax(vals > white_shift)
                direction = 1
            else:
                current_index = np.argmax(vals < black_shift)
                direction = -1 
        else:
            temp = np.argmax(vals < black_shift)
            if (temp != 0): 
                current_index = np.argmax(vals < black_shift)
                direction = -1
            else:
                current_index = np.argmax(vals > white_shift)
                dreiction = 1
        #print(f'current index is ={current_index}')
        if (current_index != 0):
            peaks.append((offset + current_index)*direction)
        shrink = zeros[np.argmax(zeros > current_index+offset)] - offset
        offset += shrink
        #print(f'advance current_index to = {offset}')

        if (np.argmax(vals > white_shift) == np.argmax(vals <  black_shift)):
            break
    return peaks

j = 8
file = f'test_{j}.tiff'
img = cv2.imread(file)
img_h, img_w = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
sum_rows = thresh.sum(axis=1)
rows_diff = np.gradient(sum_rows,1)
rows_diff_zeros = np.nonzero(rows_diff == 0)[0]
y_boundaries = find_peaks(rows_diff,rows_diff_zeros,0.05)
y_sample_top = None 
for i in range(0,len(y_boundaries)):
    if (y_boundaries[i] < 0 ):
        y_top_platen = abs(y_boundaries[i-1])
        if (i < len(y_boundaries)-1 and y_boundaries[i+1] < 0):
            y_sample_top = abs(y_boundaries[i])
            y_bottom_platen = abs(y_boundaries[i+1])
            crop_top = int((y_sample_top + y_top_platen)/2)
        else:    
            y_bottom_platen = abs(y_boundaries[i])
            crop_top = y_top_platen
        break
    else:
        continue 
height_padding = int((y_bottom_platen - y_top_platen)*0.15)
thresh_cropped = thresh[crop_top:y_bottom_platen,0:img_w]
sum_cols = thresh_cropped.sum(axis=0)
cols_diff = np.gradient(sum_cols,1)
cols_diff_zeros = np.nonzero(cols_diff == 0)[0]
x_boundaries = find_peaks(cols_diff,cols_diff_zeros,0.5)
x_boundaries = [ x * -1 for x in x_boundaries]
#print(x_boundaries)
left_boundary = abs(x_boundaries[0])
right_boundary = abs(x_boundaries[1])
width_padding = int((right_boundary - left_boundary)*0.10)
#print(width_padding)
final_crop = thresh[crop_top:y_bottom_platen,left_boundary-width_padding:right_boundary+width_padding]
img_canny = cv2.Canny(thresh_cropped, 10, 150)
contours, _ = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.line(img, (left_boundary, y_top_platen), (right_boundary, y_top_platen), (153, 204, 255), 5)
cv2.line(img, (left_boundary, y_bottom_platen), (right_boundary, y_bottom_platen), (153, 204, 255), 5)
if (y_sample_top != None):
    cv2.line(img, (left_boundary, y_sample_top), (right_boundary, y_sample_top), (255, 0, 160), 5)
cv2.drawContours(img, contours, -1, (0, 0, 255), 10, offset = (0,crop_top))
cv2.imwrite(f'test_{j}_processed.tiff',img)
