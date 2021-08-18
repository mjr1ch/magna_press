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

class Visualize_Sample():
    
    camera = None    
    run_image_label = None
    calib_image1 = None
    calib_image2 = None
    calib_image3 = None 
    convertor = None 

    def __init__(self):
        #super(Visualize_Sample,self).__init__(parent)
        self.init_camera()

    def process_image(self,img):
        print("processing image")
        im = 255-img # invert
        im = im.astype(np.float32)
        imh, imw = im.shape[:2]
        im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # raw image from camera 
        p1 = im_gray.copy
        
        ################################################################3
        #               Extracting features from image 
        ##################################################################
        kernel_size = 3
        im_blur = cv2.GaussianBlur(im_gray,(kernel_size, kernel_size),0).astype('uint8')
        th, img_th = cv2.threshold(im_blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        low_threshold = 250
        high_threshold = 350
        contours, hierarchy =  cv2.findContours(img_th,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        poly_list = []
        largest_contours = []
        listx = []
        listy = []
        valid_area_low_limit = 4e6
        valid_area_high_limit = 10e6
        # filter countours out until we have largest 5         
        for i in range(0,len(contours)):
            cnt = contours[i]
            if valid_area_low_limit <= cv2.contourArea(cnt) and cv2.contourArea(cnt)<= valid_area_high_limit:
                largest_contours.append(cnt)
        p2 = np.zeros((imh,imw,3), np.uint8)
        
        # convert countours to polygons 
        for i in range(0,len(largest_contours)):
            cnt = largest_contours[i]
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.005*peri,True)      
            M = cv2.moments(approx)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            listx.append(cX)
            listy.append(cY)
            poly_list.append(approx)
      
        for i in range(0,len(poly_list)):
            shape = poly_list[i]
            color = (0,255,0)
            #cv2.drawContours(bg_img, contours_cropped, 0, tuple(color), -1)
            color = np.random.randint(0, 255, size=(3, ))
            #convert data types int64 to int
            color = ( int (color [ 0 ]), int (color [ 1 ]), int (color [ 2 ]))
            cv2.fillPoly(p2,[approx],tuple(color))
            cv2.polylines(p2,[approx],True,tuple(color),10)
        for j in range(0,len(shape)):
            spot = approx[j]
            x_y = (spot[0][0],spot[0][1])
            # print(tuple(x_y))
            cv2.circle(p2, tuple(x_y), radius=20, color=(0, 0, 255), thickness=-1)
        
        #######################################################################
        # creating focused image on sample 
        #######################################################################
        
        p3 = np.zeros((imh,imw,3), np.uint8)
        listxy = list(zip(listx,listy))
        listxy = np.array(listxy)
        
        ### Calculating crop
        close_points = []
        for i in range(0,len(poly_list)): 
            shape = poly_list[0]
            mid_point = listxy[0][:]
        for j in range (0,4):
            num_of_points = len(shape)
            close_index = self.find_nearest_index(mid_point,shape)
            close_points.append(shape[close_index])
            shape = np.concatenate((shape[0:close_index],shape[close_index+1:len(shape)]),axis=0)
    
        close_points = np.asarray(close_points)
        crop_x = np.argmin(close_points[:,:,0])
        crop_y = np.argmin(close_points[:,:,1])
        max_x = np.argmax(close_points[:,:,0])
        max_y = np.argmax(close_points[:,:,1])
        crop_x = int(close_points[crop_x,:,0])
        crop_y = int(close_points[crop_y,:,1])
        max_x = int(close_points[max_x,:,0])
        max_y = int(close_points[max_y,:,1])
        width = max_x - crop_x
        height = max_y - crop_y 

        img_th_cropped = img_th[int(crop_y*1):int(crop_y*1+height*1), int(crop_x*.98):int(crop_x*.95+width*1)].copy() 
        
        
        contours_cropped, hierarchy =  cv2.findContours(img_th_cropped,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        valid_area_low_limit_cropped = 1e4
        valid_area_high_limit_cropped = 1e9
        refined_contours = []
        shape = []
        for i in range(0,len(contours_cropped)):
            cnt = contours_cropped[i]
            if valid_area_low_limit_cropped <= cv2.contourArea(cnt) and  cv2.contourArea(cnt) <= valid_area_high_limit_cropped:
                refined_contours.append(cnt)
        for i in range(0,len(poly_list)): 
            shape = poly_list[i]
            color = (0,255,0)
            #cv2.drawContours(bg_img, contours_cropped, 0, tuple(color), -1)
            color = np.random.randint(0, 255, size=(3, ))
            #convert data types int64 to int
            color = ( int (color [ 0 ]), int (color [ 1 ]), int (color [ 2 ])) 
            cv2.fillPoly(p3,[approx],tuple(color))
            cv2.polylines(p3,[approx],True,tuple(color),10)
        for j in range(0,len(shape)):
            spot = approx[j]
            x_y = (spot[0][0],spot[0][1])
            # print(tuple(x_y))
            cv2.circle(p3, tuple(x_y), radius=20, color=(0, 0, 255), thickness=-1)
        for i in range(0,len(refined_contours)):
            cnt = refined_contours[i] 
            color = np.random.randint(0, 255, size=(3, ))
            #convert data types int64 to int
            color = ( int (color [ 0 ]), int (color [ 1 ]), int (color [ 2 ])) 
            cv2.drawContours(p3, [cnt], 0, tuple(color), -1,offset=(int(crop_x*1),int(crop_y*1)))
        x,y,width,height = cv2.boundingRect(cnt)
        return p1, p2, p3, width, height
        

    def init_camera(self):
        serial_number = '23437639'
        info = None 

        for i in pylon.TlFactory.GetInstance().EnumerateDevices():
            if i.GetSerialNumber() == serial_number:
                info = i 
                break  
        else:
            print('Camera with {} serial number not found '.format(serial_number))

        if info is not None:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(info))
            self.camera.Open()
    
    async def grabbing_image(self):
        
        while self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                print("grabbing image")
                img = self.converter.Convert(grabResult)
                img = img.GetArray()
                orig_img = img.copy()                
                orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
                h, w, ch  = img.shape
                orig_img, contour_img, sample_img, height, width = self.process_image(img)
                bytesPerLine = w
                original_QT = QImage(orig_img.data, w, h, bytesPerLine, QImage.Format_Grayscale8)
                contour_QT = QImage(contour_img.data, w, h, bytesPerLine, QImage.Format_Indexed8)
                sample_QT = QImage(sample_img, w, h, bytesPerLine, QImage.Format_Indexed8)
                p1 = original_QT.scaled(640, 480, Qt.KeepAspectRatio)
                p2 = contour_QT.scaled(640, 480, Qt.KeepAspectRatio)
                p3 = sample_QT.scaled(640, 480, Qt.KeepAspectRatio) 
                if (self.calib_image2 != None):
                    self.calib_image1.setPixmap(QPixmap.fromImage(p1))
                    self.calib_image2.setPixmap(QPixmap.fromImage(p2))
                    self.calib_image3.setPixmap(QPixmap.fromImage(p3))
                else: 
                    self.run_image_label.setPixmap(QPixmap.fromImage(p1))
                await asyncio.sleep(0.1)
                QApplication.processEvents()

    async def aquire_images(self,*arg):
        if (len(arg) == 3):
            self.calib_image1 = arg[0]
            self.calib_image2 = arg[1]
            self.calib_image3 = arg[2]
        else:
            self.run_image_label = arg[0]
        print("aquriing images")
        # Grabing Continusely (video) with minimal delay
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        self.converter = pylon.ImageFormatConverter()

        # converting to opencv bgr format
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        
        image_stream = asyncio.create_task(self.grabbing_image()) 
        print("Finish processing image")


    def dim(a):
        if not type(a) == list:
            return []
        return [len(a)] + dim(a[0])


    def closest_node(node, nodes):
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_2 = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_2)

    def closest_node2(node, nodes):
        nodes = np.asarray(nodes)
        dist_2 = np.sum((nodes - node)**2, axis=1)
        return np.argmin(dist_2)

    def find_nearest_index(self,node, nodes):
        distances = np.sqrt((nodes[:,:,0] - node[0]) ** 2 + (nodes[:,:,1] - node[1]) ** 2)
        return  np.argmin(distances)



