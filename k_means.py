import cv2
import numpy as np 
import matplotlib.pyplot as plt 



#original_image = cv2.imread("explant_nocontact3.tiff",0)
original_image = np.load('./images/image-2-None-0.npy')
print(original_image.shape)
pixel_values = original_image.reshape((-1, 1))
pixel_values = np.float32(pixel_values)
print(pixel_values.shape)

# define stopping criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 1000, 0.2)

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
segmented_image = segmented_image.reshape(original_image.shape)
# show the image
plt.imshow(segmented_image)
plt.show()