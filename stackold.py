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
        print(f'next whiteshift= { np.argmax(vals > white_shift)} next bkaj shift {np.argmax(vals <  black_shift)}')
        if (np.argmax(vals > white_shift) < np.argmax(vals <  black_shift)):
            temp = np.argmax(vals > white_shift)
            if (temp != 0): 
                current_index = np.argmax(vals > white_shift)
            else:
                current_index = np.argmax(vals < black_shift)
        else:
            temp = np.argmax(vals < black_shift)
            if (temp != 0): 
                current_index = np.argmax(vals < black_shift)
            else:
                current_index = np.argmax(vals > white_shift)
        print(f'current index is ={current_index}')
        if (current_index != 0):
            peaks.append(offset + current_index)
        shrink = zeros[np.argmax(zeros > current_index+offset)] - offset
        offset += shrink
        print(f'advance current_index to = {offset}')

        if (np.argmax(vals > white_shift) == np.argmax(vals <  black_shift)):
            break
    return peaks

fig,a= plt.subplots(4,1,squeeze=False)
i = 7 
file = f'test_{i}.tiff'
img = cv2.imread(file)
img_h, img_w = img.shape[:2]
x_1 = np.arange(0, img_w,1)
x_2 = np.arange(0, img_h,1)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
sum_rows = thresh.sum(axis=1)
rows_diff = np.gradient(sum_rows,1)
rows_diff_zeros = np.nonzero(rows_diff == 0)[0]
boundaries = find_peaks(rows_diff,rows_diff_zeros,0.05)
print(boundaries)
a[0][0].plot(x_2,rows_diff)
a[0][0].set_title(f'full image {i} row diff')
#find max transition to white 
rows_diff_max = np.max(rows_diff)
print(f'max difference to white = {rows_diff_max}')
# find first instance where transition to white is 5% of max
y1 = np.argmax(rows_diff > rows_diff_max*0.20)
#find max transion to black 
rows_diff_min = np.min(rows_diff)
rows_diff_avg = np.mean(rows_diff)
print(f'the mean value is {rows_diff_avg}')
print(f'max difference to black = {rows_diff_min}')
# find first instance where transtion to black is 5% of max 
y2 = np.argmax(rows_diff < rows_diff_min*0.20)
height_padding = int((y2 - y1)*0.15)
print(f'y1={y1} y2={y2}')
thresh = thresh[y1- height_padding:y2+height_padding,0:img_w]
sum_cols = thresh.sum(axis=0)
cols_diff = np.gradient(sum_cols,1)
a[1][0].plot(x_1,cols_diff)
a[1][0].set_title(f'full image {i} col diff')
cols_diff_max = np.max(cols_diff)
cols_diff_min = np.min(cols_diff)
print(f'max difference to white = {cols_diff_max} max diffrernce to black ={cols_diff_min}')
x1 = np.argmax(cols_diff < cols_diff_min*0.20)
x2 = np.argmax(cols_diff > cols_diff_max*0.20)
print(f'x1={x1} x2={x2}')
width_padding = int((x2-x1)*0.15)
h,w = thresh.shape[:2]
thresh = thresh[0:h,x1-width_padding:x2+width_padding]
h,w = thresh.shape[:2]
x_1 = np.arange(0, w,1)
x_2 = np.arange(0, h,1)
sum_cols = thresh.sum(axis=0)
cols_diff = np.gradient(sum_cols,1)
a[2][0].plot(x_1,cols_diff)
a[2][0].set_title('Cropped image col diff')

sum_rows = thresh.sum(axis=1)
rows_diff = np.gradient(sum_rows,1)
a[3][0].plot(x_2,rows_diff)
a[3][0].set_title('Cropped image row diff')

print(f'max difference to white = {cols_diff_max} max diffrernce to black ={cols_diff_min}')
plt.show()
cv2.imwrite(f'test_{i}_processed.tiff',thresh)
