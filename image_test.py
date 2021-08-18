from pypylon import pylon
import cv2
import sys
import numpy as np
from scipy.interpolate import interp2d
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from freespin import Ui_FreeSpin
from PyQt5.QtWidgets import QApplication
import asyncio 
import inspect
from PyQt5.QtCore import QRect
from time import sleep 
import math

def find_nearest_index2(center,points):
    distance = np.array(list(map(abs,(points[:,0] - center))))
    index = np.argmin(distance,axis = 0)
    rows = points.shape[0]
    value = points[index][:]
    return np.reshape(np.delete(points,[index*2,index*2+1]),(rows-1,2)),value

def remove_bottom_node(contour):
    index = np.argmax(contour,axis = 0)[1]
    rows = contour.shape[0]
    return np.reshape(np.delete(contour,[index*2,index*2+1]),(rows-1,2))

def get_vertical_distance(contour):
    high_val = contour[np.argmax(contour,axis=0)[1],1]
    low_val = contour[np.argmin(contour,axis=0)[1],1]
    return high_val - low_val

img = cv2.imread('Image__2021-05-13__01-38-30.tiff')
im = 255-img # invert    
im = im.astype(np.float32)    
imh, imw = im.shape[:2]    
im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)    

p4 = np.zeros((imh,imw,3), np.uint8)    
p4 = img


################################################################3    
#               Extracting features from image     
##################################################################    
kernel_size = 3    
im_blur = cv2.GaussianBlur(im_gray,(kernel_size, kernel_size),0).astype('uint8')    
th, img_th = cv2.threshold(im_blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)    
cv2.imwrite('fullsize.tiff',img_th)
p1 = np.zeros((imh,imw,3), np.uint8)    
p1 = img_th    
low_threshold = 250    
high_threshold = 350    
contours, hierarchy =  cv2.findContours(img_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)    
screened_contours = []    
valid_area_low_limit =  1000 #float(self.parent.ui.tb_LOWLIMIT.text()) 
valid_area_high_limit = 100E6 #float(self.parent.ui.tb_HIGHLIMIT.text())
for i in range(0,len(contours)):
    cnt = contours[i]
    if valid_area_low_limit <= cv2.contourArea(cnt) and cv2.contourArea(cnt)<= valid_area_high_limit:
        screened_contours.append(cnt)
        p2 = np.zeros((imh,imw,3), np.uint8)
        p3 = np.zeros((imh,imw,3), np.uint8)
        poly_count = 0  
        area = 0 
# convert countours to polygons 
for i in range(0,len(screened_contours)):
    poly_count += 1
    cnt = screened_contours[i]
    if (cv2.contourArea(cnt) > area):
        shape = cnt
        area = cv2.contourArea(cnt) 
        peri = cv2.arcLength(cnt,True)
        found_poly = cv2.approxPolyDP(cnt,0.005*peri,True)      
        M = cv2.moments(found_poly)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        color = np.random.randint(0, 255, size=(3, ))
        color = ( int (color [ 0 ]), int (color [ 1 ]), int (color [ 2 ]))
        #cv2.drawContours(p2, [shape], 0, tuple(color), -1)
        cv2.fillPoly(p2,[found_poly],tuple(color))
        #cv2.polylines(p2,[shape],True,tuple(color),10)
        for j in range(0,len(found_poly)):
            spot = found_poly[j]
            x_y = (spot[0][0],spot[0][1])
            cv2.circle(p2, tuple(x_y), radius=20, color=(0, 0, 255), thickness=-1)
# font
font = cv2.FONT_HERSHEY_SIMPLEX
# org
org = (300, 750)
# fontScale
fontScale = 7
# Blue color in BGR
color = (255, 0, 0)
# Line thickness of 2 px
thickness = 40
image_label = str(poly_count) + ' Polygons Detected' 
p2 = cv2.putText(p2,image_label, org, font,fontScale, color, thickness, cv2.LINE_AA)

#######################################################################
# creating focused image on sample 
#######################################################################
### Calculating crop
found_poly = np.squeeze(found_poly,1)
close_points = []

if found_poly != []:
    center_line = float (imw /2)
    for j in range (0,4):
        #rows = found_poly.shape[0]
        #close_index = find_nearest_index(center_line,found_poly)
        found_poly,close_point = find_nearest_index2(center_line,found_poly)
        close_points.append(close_point)
        #close_points.append(found_poly[close_index][:])
        #found_poly = np.reshape(np.delete(found_poly,[close_index*2,close_index*2+1]),(rows-1,2))
    close_points = np.asarray(close_points)
    top_left_x = np.argmin(close_points[:,0])
    top_left_y = np.argmin(close_points[:,1])
    bottom_right_x = np.argmax(close_points[:,0])
    bottom_right_y = np.argmax(close_points[:,1])
    top_left_x = int(close_points[top_left_x,0])
    top_left_y = int(close_points[top_left_y,1])
    bottom_right_x = int(close_points[bottom_right_x,0])
    bottom_right_y = int(close_points[bottom_right_y,1])
    width = bottom_right_x - top_left_x
    height = bottom_right_y - top_left_y 
    img_center_x = int(top_left_x + width *1.5 )
    img_center_y = int(top_left_y + height *1.5)
    img_th_cropped = img_th[int(top_left_y*0.8):int(top_left_y*1+height*.75), int(top_left_x*.6):int(top_left_x+width*0.75)].copy() 
    p3 = p3[int(top_left_y*0.8):int(top_left_y*1+height*.75), int(top_left_x*.6):int(top_left_x+width*0.75)].copy() 
    p4 = p4[int(top_left_y*0.8):int(top_left_y*1+height*.75), int(top_left_x*.6):int(top_left_x+width*0.75)].copy() 
    contours_cropped, hierarchy =  cv2.findContours(img_th_cropped,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    valid_area_low_limit_cropped = 1000 #float(self.parent.ui.tb_LOWLIMIT_SAMPLE.text())
    valid_area_high_limit_cropped = 100E6#float(self.parent.ui.tb_HIGHLIMIT_SAMPLE.text())
    refined_contours = []
    shape = []
    for i in range(0,len(contours_cropped)):
        cnt = contours_cropped[i]
        cnt = np.squeeze(cnt,1)
        if valid_area_low_limit_cropped <= cv2.contourArea(cnt) and  cv2.contourArea(cnt) <= valid_area_high_limit_cropped:
            color = np.random.randint(0, 255, size=(3, ))
            #convert data types int64 to int
            color = ( int (color [ 0 ]), int (color [ 1 ]), int (color [ 2 ])) 
            cnt = cnt[70:len(cnt)-130]
            for i in range(0,75):
                cnt = remove_bottom_node(cnt)        
            cv2.polylines(p4,[cnt],True,tuple(color),3)
            cv2.drawContours(p3, [cnt], 0, tuple(color), -1)
            for j in range(0,len(cnt)):
                spot = cnt[j]
                x_y = (spot[0],spot[1])
                cv2.circle(p3, tuple(x_y), radius=5, color=(255, 0, 0), thickness=-1)
                cv2.circle(p4, tuple(x_y), radius=5, color=(255, 0, 0), thickness=-1)


p2 = cv2.cvtColor(p2, cv2.COLOR_BGR2RGB)
p3 = cv2.cvtColor(p3, cv2.COLOR_BGR2RGB)
p4 = cv2.cvtColor(p4, cv2.COLOR_BGR2RGB)
x,y,width,height = cv2.boundingRect(cnt)
cv2.imwrite('p2.tiff',p2)
cv2.imwrite('p3.tiff',p3)
cv2.imwrite('p4.tiff',p4)
