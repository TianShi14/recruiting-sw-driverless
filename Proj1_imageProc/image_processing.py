import cv2 as cv
import numpy as np
import torch

# Function declarations

def bgr_shift(original_px, filter_px):
    return original_px - filter_px

# task declarations

img = cv.imread("corrupted.png")
shift_pixels = int(img.shape[0] / 2)
recovered_img = np.zeros_like(img)

first_sample = np.array([250, 158, 3]) # original image (541, 128) values
second_sample = np.array([40, 195, 240]) # original image (267, 564) values
min_norm = 50
max_norm = 200

## Step 1 - Position Shift
# vertical shifting lazily subverted

recovered_img[:shift_pixels, :] = img[shift_pixels:, :]
recovered_img[shift_pixels:, :] = img[:shift_pixels, :]

cv.imwrite("step1.png", recovered_img)
cv.imshow("Corretta", recovered_img)
cv.waitKey(0)
cv.destroyAllWindows()

## Step 2 - Color Shift
# minmax normalization for sample pixels

norm_first =  ((first_sample / 255) * (max_norm - min_norm)) + min_norm
norm_second =  ((second_sample / 255) * (max_norm - min_norm)) + min_norm

norm_first = np.round(norm_first).astype(np.uint8)
norm_second = np.round(norm_second).astype(np.uint8)

# assess channels shifting

recovered_img[shift_pixels:, :] = np.clip(recovered_img[shift_pixels:, :] + bgr_shift(norm_first, recovered_img[541, 128]), 50, 200).astype(np.uint8)
recovered_img[:shift_pixels, :] = np.clip(recovered_img[:shift_pixels, :] + bgr_shift(norm_second, recovered_img[267, 564]), 50, 200).astype(np.uint8)

cv.imwrite("correct.png", recovered_img)
cv.imshow("Corretta", recovered_img)
cv.waitKey(0)
cv.destroyAllWindows()

## Step 3 - Cone Detection
# general mask

hsv_img = cv.cvtColor(recovered_img, cv.COLOR_BGR2HSV) # after testing HSV seems more efficient than Lab, YCrCb or RGB normalization

cv.imshow("coso", hsv_img)
cv.waitKey()
cv.destroyAllWindows()

mask_hsv = cv.inRange(hsv_img, np.array([0, 75, 0]), np.array([180, 200, 200]))
mask_black = cv.inRange(recovered_img, np.array([50, 50, 50]), np.array([75, 75, 75]))
mask_white = cv.inRange(recovered_img, np.array([155, 155, 155]), np.array([200, 200, 200]))

mask = cv.bitwise_or(mask_white, cv.bitwise_or(mask_hsv, mask_black))

cv.imshow("Corretta", mask)
cv.waitKey(0)
cv.destroyAllWindows()

# 

mask = cv.erode(mask, np.ones((5,5), np.uint8), iterations=4)

cv.imshow("Corretta", mask)
cv.waitKey(0)
cv.destroyAllWindows()

mask = cv.dilate(mask, np.ones((5,5), np.uint8), iterations=6)

cv.imshow("Corretta", mask)
cv.waitKey(0)
cv.destroyAllWindows()

mask = cv.GaussianBlur(mask, (3,3), 0)

cv.imshow("Corretta", mask)
cv.waitKey(0)
cv.destroyAllWindows()

mask = cv.Canny(mask, 160, 80)

cv.imshow("Corretta", mask)
cv.waitKey(0)
cv.destroyAllWindows()

contours , _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

image = np.zeros((recovered_img.shape[0], recovered_img.shape[1], 3)).astype(np.uint8)

for contour in contours:
    cv.drawContours(recovered_img, [cv.approxPolyDP(contour, 0.01 * cv.arcLength(contour, True), True)], 0, (0, 250, 0), 2)


cv.imshow("Pisello", recovered_img)
cv.waitKey()