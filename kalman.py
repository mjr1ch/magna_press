import cv2
import numpy as np
import matplotlib.pyplot as plt
from pykalman import KalmanFilter

# Main settings:
file="singleball.mov"
filter_train_ratio = 0.5

capture = cv2.VideoCapture(file)
numframes=int(capture.get(7))
numframes_train = int(filter_train_ratio*numframes)

print ("\t Total No. Frames: ", numframes)
print ("\t No. Frames Train: ", numframes_train)

# Background filter settings:
history = 10
nGauss = 3
bgThresh = 0.6
noise = 20

bgs = cv2.BackgroundSubtractorMOG(history,nGauss,bgThresh,noise)
f = plt.figure()
plt.ion()
plt.axis([0,480,360,0])
measuredTrack = np.zeros((numframes_train,2))-1
measurementMissingIdx = [False]*numframes_train

# Get measured trace to train a Kalman Filter:
count=0
legendPlotted = False

while count<numframes_train:
    count+=1
    img2 = capture.read()[1]
    cv2.imshow("Video",img2)
    foremat=bgs.apply(img2)
    cv2.waitKey(100)
    foremat=bgs.apply(img2)
    ret,thresh = cv2.threshold(foremat,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        m= np.mean(contours[0],axis=0)
        measuredTrack[count-1,:]=m[0]
        if not legendPlotted:
            plt.plot(m[0,0],m[0,1],'ob', label='measurement')
            plt.legend(loc=2)
            legendPlotted = True
        else:
            plt.plot(m[0,0],m[0,1],'ob')
        plt.pause(0.05)
    else:
        measurementMissingIdx[count-1] = True
    cv2.imshow('Foreground',foremat)
    cv2.waitKey(80)

# Train the Kalman filter:
measurements = np.ma.asarray(measuredTrack)
measurements[measurementMissingIdx] = np.ma.masked

# Kalman filter settings:
Transition_Matrix=[[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]]
Observation_Matrix=[[1,0,0,0],[0,1,0,0]]

kf=KalmanFilter(transition_matrices=Transition_Matrix,
            observation_matrices =Observation_Matrix)

(smoothed_state_means, smoothed_state_covariances) = kf.smooth(measurements)

plt.plot(smoothed_state_means[:,0],smoothed_state_means[:,1],'xr',label='kalman output')
legend = plt.legend(loc=2)
plt.title("Constant Velocity Kalman Filter")

# Apply (pre-trained) filter one interval at a time,
# with plotting in real time.

x_now = smoothed_state_means[-1, :]
P_now = smoothed_state_covariances[-1, :]
legendPlotted = False

while count<numframes:
    newMeasurement = np.ma.asarray(-1)
    count+=1
    img2 = capture.read()[1]
    cv2.imshow("Video",img2)
    foremat=bgs.apply(img2)
    cv2.waitKey(100)
    foremat=bgs.apply(img2)
    ret,thresh = cv2.threshold(foremat,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        m= np.mean(contours[0],axis=0)
        newMeasurement = np.ma.asarray(m[0])

    else:
        newMeasurement = np.ma.masked

    cv2.imshow('Foreground',foremat)
    cv2.waitKey(80)

    (x_now, P_now) = kf.filter_update(filtered_state_mean = x_now,
                                      filtered_state_covariance = P_now,
                                      observation = newMeasurement)    
    if not legendPlotted:
        plt.plot(x_now[0],x_now[1],'xg', label='kalman update')
        legendPlotted = True
        plt.legend(loc=2)

    else:
        plt.plot(x_now[0],x_now[1],'xg')

    plt.pause(0.05)

