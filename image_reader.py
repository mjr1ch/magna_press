# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
# [GCC 8.3.0]
# Embedded file name: /home/magnapress/magnapress/image_reader.py
# Compiled at: 2021-08-16 18:14:44
# Size of source mod 2**32: 17105 bytes
from pypylon import pylon
import cv2, numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import asyncio
from time import sleep
import csv
from timer import Timer

class Visualize_Sample:
    camera = None
    calibration = True
    top_left_corner = (0, 0)
    width_and_height = (100, 100)
    threshold_low = 0
    threshold_high = 255
    final_dark_tol = 1
    final_index_pad = 1
    final_bottom_trim = 2
    capture_profile = False
    image_stream = None
    data_file = None
    writer = None
    orig_height = 1
    orig_width_padding = None
    orig_height_padding = None
    orig_sample = None
    orig_top = None
    orig_bottom = None
    orig_left = None
    orig_right = None
    offset = None
    sensitivity = None
    sample_size = None
    sample = 0
    image_counter = 0
    x_adj = 0
    y_adj = 0
    resample = True

    def __init__(self):
        self.init_camera()

    async def get_profile(self):
        self.capture_profile = True
        await asyncio.sleep(1)
        self.image_stream.cancel()
        self.camera.StopGrabbing()

    async def get_newsample(self):
        self.resample = True

    def label_image(self, image, label, position, color):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (255, 255, 0)
        thickness = 7
        labelled_image = cv2.putText(image, label, position, font, fontScale, color, thickness, cv2.LINE_AA)
        return labelled_image

    async def stop_run(self):
        self.camera.StopGrabbing()
        self.image_stream.cancel()

    def Update_GUI_Labels(self, top_platen, sample_top, bottom_platen):
        self.parent.ui.lb_PLATEN_to_PLATEN.setText(str(bottom_platen - top_platen))
        self.parent.ui.lb_PLATEN_to_SAMPLE.setText(str(sample_top - top_platen))
        self.parent.ui.lb_SAMPLE_to_BOTTOM_PLATEN.setText(str(int(bottom_platen) - int(sample_top)))
        self.parent.ui.lb_SAMPLE_TOP_to_ORIGINAL_SAMPLE_TOP.setText(str(int(sample_top) - int(self.orig_sample)))
        self.parent.ui.lb_ORIGINALSAMPLE_to_BOTTOM_PLATEN.setText(str(int(self.orig_bottom) - int(self.orig_sample)))

    def Emit_Strain(self, val):
        self.parent.current_strain = val

    def init_camera(self):
        serial_number = '23437639'
        info = None

    async def find_platens(self, calibration, img):
        top = 0
        gap = 0
        read_size = 25
        h, w = img.shape[:2]
        for i in range(0, read_size):
            top += np.argmax((img[:, i] == 255), axis=0)[0]
            gap += np.count_nonzero((img[:, i] == 255), axis=0)[0]

        for i in range(w - 1, w - 1 - read_size, -1):
            top += np.argmax((img[:, i] == 255), axis=0)[0]
            gap += np.count_nonzero((img[:, i] == 255), axis=0)[0]

        top /= 2 * read_size
        gap /= 2 * read_size
        return (
         int(top), int(top + gap))

    async def find_sample(self, calibration, img, top, bottom):
        h, w = img.shape[:2]
        left_edge = 0
        right_edge = w - 1
        step_leftedge = int(w / 8)
        step_rightedge = int(w / 8)
        threshold = 0.25
        gap = bottom - top
        iter = 10
        for i in range(0, iter):
            test_left = np.count_nonzero((img[:, left_edge] == 255), axis=0)[0]
            test_right = np.count_nonzero((img[:, right_edge] == 255), axis=0)[0]
            if abs(test_left - gap) < gap * threshold:
                left_edge = left_edge + step_leftedge
            else:
                step_leftedge = int(step_leftedge / 2)
                if left_edge > 0:
                    left_edge = left_edge - step_leftedge
            if abs(test_right - gap) < gap * threshold:
                right_edge = right_edge - step_rightedge
            else:
                step_rightedge = int(step_rightedge / 2)
            if right_edge < w - 1:
                right_edge = right_edge + step_rightedge

        if calibration:
            if self.resample:
                sample_size = int(self.parent.ui.sld_SAMPLE_DENSITY.value())
                surface_points = np.random.choice(np.arange(left_edge, right_edge, dtype=int), sample_size, replace=False)
                self.surface_points = surface_points
                self.resample = False
                self.sample_density = sample_size
            else:
                surface_points = self.surface_points
                sample_size = self.sample_density
        else:
            surface_points = self.surface_points - self.x_adj
            sample_size = self.sample_density
        sample_height = 0
        for col in surface_points:
            top = np.argmax((img[:, col] == 255), axis=0)[0]
            gap = np.count_nonzero((img[:, col] == 255), axis=0)[0]
            sample_height += top + gap

        sample_height /= sample_size
        return (
         left_edge, right_edge, sample_height)

    async def annotate_image(self, calibration, img, lines):
        if calibration:
            raw_img = None
        else:
            raw_img = img.copy()
        if len(lines) == 2:
            top = lines[0][0][1]
            bottom = lines[1][0][1]
            new_height = bottom - top
            sample = 0
        else:
            top = lines[0][0][1]
            sample = lines[2][0][1]
            bottom = lines[1][0][1]
            new_height = bottom - sample
        left = lines[0][0][0]
        right = lines[0][1][0]
        for line in lines:
            point_1 = tuple(line[0])
            point_2 = tuple(line[1])
            img = cv2.line(img, point_1, point_2, (0, 0, 255), 30)

        if calibration:
            height_padding = int(self.parent.ui.sld_HEIGHT_PADDING.value())
            if top - height_padding < 0:
                top = height_padding
            if bottom + height_padding > 4023:
                bottom = 4023 - height_padding
            width_padding = int(self.parent.ui.sld_WIDTH_PADDING.value())
            if left - width_padding < 0:
                left = width_padding
            if right + width_padding > 4023:
                right = 4023 - width_padding
            cropped_img = img[top - height_padding:bottom + height_padding, left - width_padding:right + width_padding]
            cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
        else:
            cropped_img = img
        if self.capture_profile:
            self.orig_top = top
            self.orig_sample = sample
            self.orig_bottom = bottom
            self.orig_height = bottom - sample
            self.orig_left = left
            self.orig_right = right
            self.width_padding = width_padding
            self.height_padding = height_padding
            self.sample_density = int(self.parent.ui.sld_SAMPLE_DENSITY.value())
            self.x_adj = left - width_padding
            self.y_adj = top - height_padding
            self.capture_profile = False
        return (cropped_img, raw_img)

    async def overlay_original_data(self, img):
        color = (0, 255, 255)
        point_1 = (
         self.orig_left - self.x_adj, self.orig_top - self.y_adj)
        point_2 = (self.orig_right - self.x_adj, self.orig_top - self.y_adj)
        img = cv2.line(img, point_1, point_2, color, 30)
        point_1 = (self.orig_left - self.x_adj, self.orig_bottom - self.y_adj)
        point_2 = (self.orig_right - self.x_adj, self.orig_bottom - self.y_adj)
        img = cv2.line(img, point_1, point_2, color, 30)
        point_1 = (self.orig_left - self.x_adj, self.orig_sample - self.y_adj)
        point_2 = (self.orig_right - self.x_adj, self.orig_sample - self.y_adj)
        img = cv2.line(img, point_1, point_2, color, 30)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    async def calibrate_aquisition(self, img):
        top_platen, bottom_platen = await self.find_platens(True, img)
        sample_left, sample_right, sample_height = await self.find_sample(True, img, top_platen, bottom_platen)
        if sample_height == 9999:
            top_platen = np.array([(sample_left, top_platen), (sample_right, top_platen)], dtype=int)
            bottom_platen = np.array([(sample_left, bottom_platen), (sample_right, bottom_platen)], dtype=int)
            lines = [top_platen, bottom_platen]
        else:
            top_platen = np.array([(sample_left, top_platen), (sample_right, top_platen)], dtype=int)
            bottom_platen = np.array([(sample_left, bottom_platen), (sample_right, bottom_platen)], dtype=int)
            sample = np.array([(sample_left, sample_height), (sample_right, sample_height)], dtype=int)
            lines = [top_platen, bottom_platen, sample]
        cropped_img, raw_img = await self.annotate_image(True, img, lines)
        return (
         img, cropped_img)

    async def process_image(self, img):
        img = img[self.orig_top - self.height_padding:self.orig_bottom + self.height_padding,
         self.orig_left - self.width_padding:self.orig_right + self.width_padding]
        top_platen, bottom_platen = await self.find_platens(False, img)
        sample_left, sample_right, sample_height = await self.find_sample(False, img, top_platen, bottom_platen)
        if sample_height == 9999:
            new_height = bottom_platen - top_platen
            top = top_platen
            bottom = bottom_platen
            top_platen = np.array([(sample_left, top_platen), (sample_right, top_platen)], dtype=int)
            bottom_platen = np.array([(sample_left, bottom_platen), (sample_right, bottom_platen)], dtype=int)
            lines = [top_platen, bottom_platen]
        else:
            new_height = bottom_platen - sample_height
            top = top_platen
            bottom = bottom_platen
            top_platen = np.array([(sample_left, top_platen), (sample_right, top_platen)], dtype=int)
            bottom_platen = np.array([(sample_left, bottom_platen), (sample_right, bottom_platen)], dtype=int)
            sample = np.array([(sample_left, sample_height), (sample_right, sample_height)], dtype=int)
            lines = [top_platen, bottom_platen, sample]
        cropped_img, raw_img = await self.annotate_image(False, img, lines)
        cropped_img = await self.overlay_original_data(cropped_img)
        self.Update_GUI_Labels(top_platen[(0, 1)], sample[(0, 1)], bottom_platen[(0,
                                                                                  1)])
        self.image_counter += 1
        strain = float(100 - new_height / self.orig_height * 100)
        time, timestamp, force, position = self.parent.Emit_Data()
        data = [str(timestamp), str(time), str(force), str(position),
         str(strain), str(top), str(sample_height),
         str(bottom), str(self.orig_top - self.y_adj),
         str(self.orig_sample - self.y_adj), str(self.orig_bottom - self.y_adj)]
        filename = f"./images/image-{self.image_counter}-{timestamp}-{force}.npy"
        self.writer.writerow(data)
        np.save(filename, raw_img, allow_pickle=False)
        return cropped_img

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
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    async def grabbing_image(self):
        stopwatch = Timer()
        while self.camera.IsGrabbing():
            stopwatch.start()
            grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                img = self.converter.Convert(grabResult)
                img = img.GetArray()
                h, w, ch = img.shape
                if self.calibration:
                    original_img, final_img = await self.calibrate_aquisition(img)
                    bytesPerLine = ch * w
                    original_QT = QImage(original_img.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    cropped_h, cropped_w, ch = final_img.shape
                    cropped_bytesPerLine = cropped_w * ch
                    final_QT = QImage(final_img.data, cropped_w, cropped_h, cropped_bytesPerLine, QImage.Format_RGB888)
                    if not original_QT.isNull():
                        p0 = original_QT.scaled(480, 480, Qt.KeepAspectRatio)
                        self.parent.ui.original_image.setPixmap(QPixmap.fromImage(p0))
                    if not final_QT.isNull():
                        p2 = final_QT.scaled(480, 480, Qt.KeepAspectRatio)
                        self.parent.ui.final_image.setPixmap(QPixmap.fromImage(p2))
                    time = stopwatch.stop()
                    self.parent.ui.lb_TIME_ELAPSED.setText(f"{time:0.4f} seconds")
                    self.parent.ui.lb_FPS.setText(f"{1 / time:0.1f} FPS")
                else:
                    final_img = await self.process_image(img)
                    cropped_h, cropped_w, ch = final_img.shape
                    bytesPerLine = cropped_w * ch
                    final_QT = QImage(final_img.data, cropped_w, cropped_h, bytesPerLine, QImage.Format_RGB888)
                    if not final_QT.isNull():
                        p0 = final_QT.scaled(480, 480, Qt.KeepAspectRatio)
                        self.parent.ui.camera_image.setPixmap(QPixmap.fromImage(p0))
                    time = stopwatch.stop()
                    self.parent.ui.lb_FPS.setText(f"{1 / time:0.1f} FPS")
            await asyncio.sleep(0)

    async def aquire_images(self, calibration, calling_window):
        self.parent = calling_window
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        if calibration:
            self.calibration = True
        else:
            self.calibration = False
            self.data_file = open('run_data.csv', 'w', newline='')
            self.writer = csv.writer(self.data_file)
            header = ['timestamp', 'time_s', 'force_g', 'position', 'strain', 'top_platen', 'sample_top', 'bottom_platen', 'orig_top_platen', 'orig_sample_top', 'orig_bottom_platen']
            self.writer.writerow(header)
        self.image_stream = asyncio.create_task(self.grabbing_image())

    def remove_bottom_node(self, contour):
        if contour != []:
            index = np.argmax(contour, axis=0)[1]
            rows = contour.shape[0]
            return np.reshape(np.delete(contour, [index * 2, index * 2 + 1]), (rows - 1, 2))
        return contour

    def get_vertical_distance(self, contour):
        high_val = contour[(np.argmax(contour, axis=0)[1], 1)]
        low_val = contour[(np.argmin(contour, axis=0)[1], 1)]
        return high_val - low_val
# okay decompiling image_reader.cpython-37.pyc
