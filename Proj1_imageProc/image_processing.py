import cv2 as cv
import numpy as np

# task declarations

img = cv.imread("corrupted.png")
shift_pixels = int(img.shape[0] / 2)
recovered_img = np.zeros_like(img)

first_sample = np.array([250, 158, 3]) # original image (541, 128) values
second_sample = np.array([40, 195, 240]) # original image (267, 564) values
min_norm = 50
max_norm = 200

## Step 1
# vertical shifting lazily subverted

recovered_img[:shift_pixels, :] = img[shift_pixels:, :]
recovered_img[shift_pixels:, :] = img[:shift_pixels, :]

cv.imshow("Corrected Picture", recovered_img)
cv.waitKey(0)
cv.destroyAllWindows()

cv.imwrite("step1.png", recovered_img)

## Step 2
# minmax normalization for sample pixels

norm_first =  ((first_sample - min_norm) / (max_norm - min_norm)) * 255
norm_second =  ((second_sample - min_norm) / (max_norm - min_norm)) * 255

norm_first = np.round(norm_first).astype(np.uint8)
norm_second = np.round(norm_second).astype(np.uint8)

# assess channels shifting