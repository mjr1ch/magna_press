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
import csv

class Visualize_Sample():
    
    camera = None    
    calibration = True
    top_left_corner = (0,0)
    width_and_height = (100,100)
    finalthreshold_low = 0
    finalthreshold_high = 255
    final_dark_tol = 1
    final_index_pad = 1
    final_bottom_trim = 2
    capture_profile = False
    image_stream = None
    final_canny_max = 0 
    final_canny_min = 0   
    width = 0
    height = 0
    line1 = None 
    line2 = None 
    image_counter = 0 
    data_file = None
    writer = None
    orig_height = 1 
    kernel_size = 1  
    horizontal_black = None
    horizontal_white = None 
    vertical_black = None 
    vertical_white = None 
    orig_profile = None
    orig_sample_height = None 
    orig_sample_top = None 
    orig_platen_bottom = None 
    offset = None 
    image_counter = 0 

    def __init__(self):
        #super(Visualize_Sample,self).__init__(parent.ui)
        self.init_camera()

    def find_peaks(self,vals,zeros,fraction_black,fraction_white):
    
        white_shift = np.max(vals)*fraction_white
        black_shift = np.min(vals)*fraction_black
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
            if (shrink == 0 or current_index == 0): 
                return peaks
            offset += shrink
            #print(f'advance current_index to = {offset}')

            if (np.argmax(vals > white_shift) == np.argmax(vals <  black_shift)):
                break
        return peaks

    async def get_profile(self):
        self.capture_profile = True
        await asyncio.sleep(0.0001)
        self.image_stream.cancel()
        self.camera.StopGrabbing()

    def label_image(self,image,label,position,color):
        # font
        font = cv2.FONT_HERSHEY_SIMPLEX
        # fontScale
        fontScale = 1
        # Blue color in BGR
        color = (255, 255, 0)
        # Line thickness of 2 px
        thickness = 7
        labelled_image = cv2.putText(image,label, position, font,fontScale, color, thickness, cv2.LINE_AA)
        return labelled_image 


    async def stop_run(self):
        self.camera.StopGrabbing()
        self.image_stream.cancel()

    def calibrate_aquisition(self,img):
        print('calibration')
        img_h, img_w = img.shape[:2]
        print('Step 1')
        kernel = int(self.parent.ui.sld_KERNEL_SIZE.value())
        print('Step 2')
        kernel = int(2*kernel + 1)
        print('Step 3')
        img = cv2.GaussianBlur(img,(kernel,kernel),cv2.BORDER_DEFAULT)
        print('Step 4')
        p0 = img
        print('Step 5')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print('Step 6')
        thresh_HL = int(self.parent.ui.sld_THRESHOLD_HL.value())
        print('Step 7')
        thresh_LL = int(self.parent.ui.sld_THRESHOLD_LL.value())
        print('Step 8')
        _, thresh = cv2.threshold(gray, thresh_LL, thresh_HL, cv2.THRESH_BINARY)
        print('Step 9')
        p1 = thresh
        print('Step 10')
        sum_rows = thresh.sum(axis=1)
        print('Step 11')
        rows_diff = np.gradient(sum_rows,1)
        print('Step 12')
        rows_diff_zeros = np.nonzero(rows_diff == 0)[0]
        print('Step 13')
        vfraction_black = float(self.parent.ui.sld_VERTICAL_BLACK.value()/100)
        print('Step 14')
        vfraction_white = float(self.parent.ui.sld_VERTICAL_WHITE.value()/100)
        print('Step 15')
        y_boundaries = self.find_peaks(rows_diff,rows_diff_zeros,vfraction_black,vfraction_white)
        print('Step 16')
        y_sample_top = 0
        print('Step 17')
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
        print('Step 18')
        print('here')
        print(y_top_platen)
        print(y_bottom_platen)
        height_padding = int((y_bottom_platen - y_top_platen)*0.25)
        print('Step 19')
        thresh_cropped = thresh[crop_top:y_bottom_platen,0:img_w]
        print('Step 20')
        sum_cols = thresh_cropped.sum(axis=0)
        print('Step 21')
        cols_diff = np.gradient(sum_cols,1)
        print('Step 22')
        cols_diff_zeros = np.nonzero(cols_diff == 0)[0]
        print('Step 23')
        hfraction_black = float(self.parent.ui.sld_HORIZONTAL_BLACK.value()/100)
        print('Step 24')
        hfraction_white = float(self.parent.ui.sld_HORIZONTAL_WHITE.value()/100)
        print('Step 25')
        x_boundaries = self.find_peaks(cols_diff,cols_diff_zeros,hfraction_black,hfraction_white)
        print('Step 26')
        x_points = len(x_boundaries)
        print('Step 27')
        if x_points  < 2 :
            p0 = cv2.cvtColor(p0, cv2.COLOR_BGR2RGB)
            p2 = np.zeros((img_h,img_w,3), np.uint8)
            return p0, p1 , p2
        print('Step 28')
        x_boundaries = [ x * -1 for x in x_boundaries]
        print('Step 29')
        #left_boundary = abs(max(x_boundaries))
        #right_boundary = abs( min(x_boundaries))
        left_boundary = abs(x_boundaries[0])
        print('Step 30')
        right_boundary = abs(x_boundaries[1])
        print('Step 31')
        width_padding = int((right_boundary - left_boundary)*0.25)
        print('Step 32')
        if (left_boundary - width_padding < 1):
            left_boundary = width_padding + 1 
        if (right_boundary + width_padding > 4024):
            right_boundary = img_w - width_padding -1
        print('Step 33')
        final_crop = thresh[crop_top:y_bottom_platen,left_boundary-width_padding:right_boundary+width_padding]
        print('Step 34')
        img_canny = cv2.Canny(final_crop, 25,75)
        print('Step 35')
        contours, _ = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print('Step 36')
        p2 = img
        print('Step 37')
        cv2.line(p2, (left_boundary, y_top_platen), (right_boundary, y_top_platen), (153, 204, 255), 5)
        print('Step 38')
        cv2.line(p2, (left_boundary, y_bottom_platen), (right_boundary, y_bottom_platen), (153, 204, 255), 5)
        print('Step 39')
        if (y_sample_top != 0):
            cv2.line(p2, (left_boundary, y_sample_top), (right_boundary, y_sample_top), (255, 0, 160), 5)
        print('Step 40')
        cv2.drawContours(p2, contours, -1, (0, 0, 255), 10, offset = (left_boundary-width_padding,crop_top))
        print('Step 41')
        p2 = p2[crop_top-height_padding:y_bottom_platen,left_boundary-width_padding:right_boundary+width_padding]
        if (self.capture_profile):
            self.finalthreshold_high = thresh_HL
            self.finalthreshold_low = thresh_LL 
            self.kernel_size = kernel  
            self.horizontal_black = hfraction_black
            self.horizontal_white = hfraction_white
            self.vertical_black = vfraction_black
            self.vertical_white = vfraction_white
            self.orig_profile = contours
            self.orig_sample_top = y_sample_top
            self.orig_platen_bottom = y_bottom_platen
            self.orig_sample_height = y_bottom_platen - y_sample_top 
            self.offset = (left_boundary-width_padding,crop_top)
            self.capture_profile = False
        p0 = cv2.cvtColor(p0, cv2.COLOR_BGR2RGB)
        p2 = cv2.cvtColor(p2, cv2.COLOR_BGR2RGB)
        return p0, p1 , p2

    def process_image(self,img):
        print('step 1')
        img_h, img_w = img.shape[:2]
        print('step 2')
        img = cv2.GaussianBlur(img,(self.kernel_size,self.kernel_size),cv2.BORDER_DEFAULT)
        print('step 3')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print('step 4')
        _, thresh = cv2.threshold(gray, self.finalthreshold_low, self.finalthreshold_high, cv2.THRESH_BINARY)
        print('step 5')
        sum_rows = thresh.sum(axis=1)
        print('step 6')
        rows_diff = np.gradient(sum_rows,1)
        print('step 7')
        rows_diff_zeros = np.nonzero(rows_diff == 0)[0]
        print('step 8')
        y_boundaries = self.find_peaks(rows_diff,rows_diff_zeros,self.vertical_black,self.vertical_white)
        print('step 9')
        y_sample_top = 0
        print('step 10')
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
        height_padding = int((y_bottom_platen - y_top_platen)*0.25)
        print('step 11')
        thresh_cropped = thresh[crop_top:y_bottom_platen,0:img_w]
        print('step 12')
        sum_cols = thresh_cropped.sum(axis=0)
        print('step 13')
        cols_diff = np.gradient(sum_cols,1)
        print('step 14')
        cols_diff_zeros = np.nonzero(cols_diff == 0)[0]
        print('step 15')
        x_boundaries = self.find_peaks(cols_diff,cols_diff_zeros,self.horizontal_black,self.horizontal_white)
        print('step 16')
        x_points = len(x_boundaries)
        print('step 17')
        if x_points  < 2 :
            p0 = cv2.cvtColor(p0, cv2.COLOR_BGR2RGB)
            return p0
        x_boundaries = [ x * -1 for x in x_boundaries]
        print('step 18')
        print(x_boundaries)
        left_boundary = abs(x_boundaries[0])
        print('step 19')
        right_boundary = abs(x_boundaries[1])
        print('step 20')
        width_padding = int((right_boundary - left_boundary)*0.25)
        print('step 21')
        if (left_boundary - width_padding < 1):
            left_boundary = width_padding + 1 
        if (right_boundary + width_padding > 4024):
            right_boundary = img_w - width_padding -1
        final_crop = thresh[crop_top:y_bottom_platen,left_boundary-width_padding:right_boundary+width_padding]
        print('step 22')
        img_canny = cv2.Canny(final_crop, 25,75)
        print('step 23')
        contours, _ = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print('step 24')
        cv2.line(img, (left_boundary, y_top_platen), (right_boundary, y_top_platen), (153, 204, 255), 5)
        print('step 25')
        cv2.line(img, (left_boundary, y_bottom_platen), (right_boundary, y_bottom_platen), (153, 204, 255), 5)
        print('step 26')
        if (y_sample_top == 0):
            cv2.line(img, (left_boundary, y_sample_top), (right_boundary, y_sample_top), (255, 0, 160), 5)
        cv2.drawContours(img, contours, -1, (0, 0, 255), 10, offset = (left_boundary-width_padding,crop_top))
        print('step 27')
        cv2.drawContours(img, self.orig_profile, -1, (255,255,255), 3, offset = (left_boundary-width_padding,crop_top))
        print('step 28')
        cv2.line(img, (left_boundary, self.orig_sample_top), (right_boundary, self.orig_sample_top), (255, 255, 255), 3)
        cv2.line(img, (left_boundary, self.orig_platen_bottom), (right_boundary, self.orig_platen_bottom), (255, 255, 255), 3)
        print('step 29')
        img = img[crop_top-height_padding:y_bottom_platen,left_boundary-width_padding:right_boundary+width_padding]
        print('step 30')
        if (y_sample_top > self.orig_sample_top):
            new_height = y_bottom_platen - y_sample_top 
        else:
            if (y_top_platen > self.orig_sample_top):
                new_height = y_bottom_platen - y_top_platen
            else:
                new_height = y_bottom_platen - self.orig_sample_top
        print('step 31')
        strain = float (100 - new_height/self.orig_sample_height*100)
        print('step 32')
        self.Emit_Strain(strain)
        print('step 33')
        p0 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print('step 34')
        self.image_counter += 1
        print('step 35')
        time,timestamp,force,position = self.parent.Emit_Data()
        print('step 36')
        image_label =f'time point = {timestamp} \r\n {str(round(strain,2))}% Strain \r\n {force} grams' 
        print('step 37')
        h,w = p0.shape[:2]
        print('step 38')
        p0 = self.label_image(p0,image_label,(int(w/8),int(h*3/4)),(0,255,255))
        print('step 39')
        data = [str(timestamp),str(time),str(force),str(position),str(strain)]
        filename = f'./images/image-{self.image_counter}.tiff'
        cv2.imwrite(filename,p0)
        self.writer.writerow(data)
        return p0

    def Emit_Strain(self, val):
        self.parent.current_strain = val

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
        
        self.converter = pylon.ImageFormatConverter()
        # converting to opencv bgr format
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    async def grabbing_image(self):
        while self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():             
                img = self.converter.Convert(grabResult)
                img = img.GetArray()
                h, w, ch  = img.shape
                if (self.calibration):
                    original_img, threshold_img, final_img = self.calibrate_aquisition(img)
                    bytesPerLine = ch*w
                    original_QT = QImage(original_img.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    bytesPerLine = w
                    threshold_QT = QImage(threshold_img.data, w, h, bytesPerLine, QImage.Format_Grayscale8)
                    cropped_h,cropped_w, ch = final_img.shape
                    bytesPerLine = cropped_w*ch
                    final_QT = QImage(final_img.data, cropped_w, cropped_h, bytesPerLine, QImage.Format_RGB888)
                    if not (original_QT.isNull()):
                        p0 = original_QT.scaled(480,480, Qt.KeepAspectRatio)
                        self.parent.ui.original_image.setPixmap(QPixmap.fromImage(p0))
                    if not (threshold_QT.isNull()):
                        p1 = threshold_QT.scaled(480,480, Qt.KeepAspectRatio)
                        self.parent.ui.threshold_image.setPixmap(QPixmap.fromImage(p1))
                    if not (final_QT.isNull()):
                        p2 = final_QT.scaled(480,480, Qt.KeepAspectRatio)
                        self.parent.ui.final_image.setPixmap(QPixmap.fromImage(p2))
                else:
                    final_img = self.process_image(img)
                    cropped_h,cropped_w, ch = final_img.shape
                    bytesPerLine = cropped_w*ch
                    final_QT = QImage(final_img.data, cropped_w, cropped_h, bytesPerLine, QImage.Format_RGB888)
                    if not (final_QT.isNull()):
                        p0 = final_QT.scaled(480, 480, Qt.KeepAspectRatio)  
                        self.parent.ui.camera_image.setPixmap(QPixmap.fromImage(p0))
            await asyncio.sleep(0)

    async def aquire_images(self,calibration,calling_window):
        
        self.parent = calling_window
        # Grabing Continusely (video) with minimal delay
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        if (calibration):
            self.calibration = True 
        else:
            self.calibration = False
            self.data_file = open('run_data.csv', 'w',newline='')
            self.writer = csv.writer(self.data_file)
            header = ['timestamp','time (s)', 'force','position', 'strain']
            self.writer.writerow(header)

        print('trying out emit data')
        self.image_stream = asyncio.create_task(self.grabbing_image()) 

    def find_nearest_index(self,center,points):
        distance = np.array(list(map(abs,(points[:,0] - center))))
        index = np.argmin(distance,axis = 0)
        rows = points.shape[0]
        value = points[index][:]
        return np.reshape(np.delete(points,[index*2,index*2+1]),(rows-1,2)),value

    def remove_bottom_node(self,contour):
        if (contour != []):
            index = np.argmax(contour,axis = 0)[1]
            rows = contour.shape[0]
            
            return np.reshape(np.delete(contour,[index*2,index*2+1]),(rows-1,2))
        else:
            return contour  

    def get_vertical_distance(self,contour):
        high_val = contour[np.argmax(contour,axis=0)[1],1]
        low_val = contour[np.argmin(contour,axis=0)[1],1]
        return high_val - low_val


