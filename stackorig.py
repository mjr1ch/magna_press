import cv2
import numpy as np


img = cv2.imread('new_test.tiff')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
sum_cols = thresh.sum(0)
indices = np.where(sum_cols < sum_cols.min() + 40000)[0]
x1, x2 = indices[0] - 5, indices[-1] + 5
if (x2 > 4023):
    x2 = 4022
diff1, diff2 = np.diff(thresh[:, [x1, x2]].T, 1)
y1_1, y2_1 = np.where(diff1)[0][:2]
y1_2, y2_2 = np.where(diff2)[0][:2]
y1, y2 = min(y1_1, y1_2), max(y2_1, y2_2)
img_canny = cv2.Canny(thresh[y1: y2, x1: x2], 50, 50)
contours, _ = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.line(img, (x1, y1_1), (x2, y1_2), (255, 0, 160), 5)
cv2.line(img, (x1, y2_1), (x2, y2_2), (255, 0, 160), 5)
cv2.drawContours(img[y1: y2, x1: x2], contours, -1, (0, 0, 255), 10)
cv2.imwrite('new_test_processed.tiff', img)

