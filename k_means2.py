import sys
import numpy as np 
from time import sleep
import re as regex
import matplotlib.pyplot as plt 
import cv2

filename = sys.argv[1]
proj_dir = sys.argv[2]
full_path = f'{proj_dir}/images/{filename}'
img_num = regex.findall(r'\d+', filename)[0]
original_image = np.load(full_path)
gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
pixel_values = gray_image.reshape((-1, 1))
pixel_values = np.float32(pixel_values)

# define stopping criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)

# number of clusters (K)
k = 5
_, labels, (centers) = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

# convert back to 8 bit values
centers = np.uint8(centers)

# flatten the labels array
labels = labels.flatten()

# convert all pixels to the color of the centroids
segmented_image = centers[labels.flatten()]
# reshape back to the original image dimension
segmented_image = segmented_image.reshape(gray_image.shape)

val = np.unique(segmented_image)
adj_segmented_image1 = np.where(segmented_image == val[3],val[4],segmented_image)
adj_segmented_image2 = np.where(segmented_image == val[2],val[0],adj_segmented_image1)
adj_segmented_image3 = np.where(segmented_image == val[1],val[0],adj_segmented_image2)
ret,th = cv2.threshold(adj_segmented_image3,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)  

h,w = th.shape[:2]

top_platen = 0
while(np.count_nonzero(th[top_platen,:] == 255) == 0):
    top_platen += 1
    #print(f'count from top {np.count_nonzero(th[top_platen,:] == 255)}')
bottom_platen = h-1
while(np.count_nonzero(th[bottom_platen-1,:] == 255) == 0):
    bottom_platen -= 1
    #print(f'count from top {np.count_nonzero(th[top_platen,:] == 255)}')

th = cv2.bitwise_not(th)
contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

screened_list = []
for ctr in contours:
    if (cv2.contourArea(ctr) > 1000000):  
        screened_list.append(ctr)


#print(f'top_platen={top_platen} bottom_platen = {bottom_platen}')
if len(screened_list) > 0:
    profile = np.squeeze(screened_list[0])
    #print(profile.shape)
    y_values = profile[:,1]
    below_platen = np.where(y_values > bottom_platen)
    profile = np.delete(profile,below_platen,axis = 0)
    y_values = profile[:,1]
    above_platen = np.where(y_values < top_platen)
    profile = np.delete(profile,above_platen,axis = 0)

    cv2.drawContours(original_image, [profile], -1, (255, 0, 0), 5)
cv2.line(original_image,(0,top_platen),(w-1,top_platen),(255,0,0),10)
cv2.line(original_image,(0,bottom_platen),(w-1,bottom_platen),(255,0,0),10)
filename = f'{proj_dir}/images/image-{img_num}.jpeg'
cv2.imwrite(filename,original_image)