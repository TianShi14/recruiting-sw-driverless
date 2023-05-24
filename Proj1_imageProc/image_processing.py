import cv2 as cv
import numpy as np

# Function declarations

def bgr_shift(original_px, filter_px):
    return original_px - filter_px

def isItValid(hull, rect):
    ratio = rect[-2] / rect[-1] # width / height ratio, a pretty straightforward assumption about cones
    if ratio >= 0.8:
        return False
    
    center = rect[1] + rect[-1] / 2.0 
    above_center = []
    below_center = []
    
    
    for contour in hull:        # assess the position of the vertices in correlation to the y center of the figure
        for point in contour:
            if point[1] <= center:
                above_center.append(point[0])
            else:                                   
                below_center.append(point[0])
    try:        
        most_left = below_center[0]
        most_right = below_center[0]    # if an object has either no vertices aboe or underneath the center, it can't possibly be a cone
    except(IndexError):
        return False
    
    for point in below_center:  # assess the furthest vertices at the base of the possible cone
        if point < most_left:
            most_left = point
        if point > most_right:
            most_right = point
    
    for point in above_center:                          # if the vertices at the top of the figure are wider than the widest at the base, they're not converging upwards
        if point <= most_left or point >= most_right:   # hence they're not cones
            return False
    
    return True

def removeInner(cone_list : list):    # the function aims to fix the commonly occuring inner contours with about the same shape and size 
    cones = []
    for i in range(len(cone_list)):
        
        flag = 0
        if i == len(cone_list):
            break

        for j in range(i + 1, len(cone_list)):
            first_moments = cv.moments(cone_list[i])
            second_moments = cv.moments(cone_list[j])

            first_centroid = (first_moments["m10"] / first_moments["m00"], first_moments["m01"] / first_moments["m00"])     # find the center of gravity
            second_centroid = (second_moments["m10"] / second_moments["m00"], second_moments["m01"] / second_moments["m00"])

            if cv.norm(np.array(first_centroid), np.array(second_centroid), cv.NORM_L2) <= 5:   # if the euclidean distance of the center of gravity of one
                flag = 1                                                                        # object with any others' is less than 5px, the shape is assessing an
        if flag != 1:                                                                           # inner contour
            cones.append(cone_list[i])
            
    return cones

def assessColor(hsv, contour, bw_mask):                 # the idea is to create a mask of the cones with removed black and white lines, to have an average value of 
    mask = np.zeros(hsv.shape[:2]).astype(np.uint8)     # the color of the cones
    cv.drawContours(mask, [contour], 0, 255, -1)        
    mask = cv.bitwise_and(mask, cv.bitwise_not(bw_mask))
    hue = cv.mean(hsv, mask=mask)[0]
    
    if 10 <= hue < 20:
        return "orange"
    elif 20 <= hue < 35:
        return "yellow"
    else:
        return "blue"
# task declarations

img = cv.imread("corrupted.png")
shift_pixels = int(img.shape[0] / 2)
recovered_img = np.zeros_like(img)

first_sample = np.array([250, 158, 3]) # original image (541, 128) values
second_sample = np.array([40, 195, 240]) # original image (267, 564) values
min_norm = 50
max_norm = 200

## Step 1 - Position and Color Shift
# vertical shifting lazily subverted

recovered_img[:shift_pixels, :] = img[shift_pixels:, :]
recovered_img[shift_pixels:, :] = img[:shift_pixels, :]

# minmax normalization for sample pixels

norm_first =  ((first_sample / 255) * (max_norm - min_norm)) + min_norm
norm_second =  ((second_sample / 255) * (max_norm - min_norm)) + min_norm

norm_first = np.round(norm_first).astype(np.uint8)
norm_second = np.round(norm_second).astype(np.uint8)

# assess channels shifting

recovered_img[shift_pixels:, :] = np.clip(recovered_img[shift_pixels:, :] + bgr_shift(norm_first, recovered_img[541, 128]), 50, 200).astype(np.uint8)
recovered_img[:shift_pixels, :] = np.clip(recovered_img[:shift_pixels, :] + bgr_shift(norm_second, recovered_img[267, 564]), 50, 200).astype(np.uint8)

cv.imwrite("correct.png", recovered_img)
cv.imshow("Colour", recovered_img)
cv.waitKey(0)
cv.destroyAllWindows()

## Step 2 - Contours definition and optimiaztion ( I just hate myself, fully aware that I could've used pre trained YOLOv5 models but where's the fun in that )
# general mask

hsv_img = cv.cvtColor(recovered_img, cv.COLOR_BGR2HSV) # after testing HSV seems more efficient than Lab, YCrCb or RGB normalization (wonder why)

mask_hsv = cv.inRange(hsv_img, np.array([0, 50, 0]), np.array([180, 200, 200])) # detecting cone colored area
mask_black = cv.inRange(recovered_img, np.array([50, 50, 50]), np.array([75, 75, 75])) # detecting black "lines" in traffic cones
mask_white = cv.inRange(recovered_img, np.array([155, 155, 155]), np.array([200, 200, 200])) # detecting white relfective "lines" in traffic cones

mask = cv.bitwise_or(mask_white, cv.bitwise_or(mask_hsv, mask_black)) # unified traffic cones binary mask 

# mask processing for better conformity

mask = cv.erode(mask, np.ones((5,5), np.uint8), iterations=4)
mask = cv.dilate(mask, np.ones((5,5), np.uint8), iterations=5)
mask = cv.GaussianBlur(mask, (3,3), 0)
mask = cv.Canny(mask, 160, 80) 
contours , _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

# geometric approximations of contours 

image = recovered_img.copy() # OBSOLETE!! np.zeros((recovered_img.shape[0], recovered_img.shape[1], 3)).astype(np.uint8) # black image with same height / width as original
hull_list = [] # list of convex hulls ( geometrical approximation of boundings )

for contour in contours:
    approximated = cv.approxPolyDP(contour, 0.01 * cv.arcLength(contour, True), True)
    hull = cv.convexHull(approximated)
    if hull.shape[0] >= 3 and hull.shape[0] <= 10:
        hull_list.append(hull)
        cv.drawContours(recovered_img, [hull], 0, (0, 255, 0), 2)

cv.imshow("Geometric contour", recovered_img)
cv.imwrite("step2.png", recovered_img)
cv.waitKey(0)
cv.destroyAllWindows()

# Step 3 - Filtering unnecessary detections
# read the functions to understand what's going on
valid_hulls = []

for hull in hull_list:
    if isItValid(hull, cv.boundingRect(hull)):
        valid_hulls.append(hull)

valid_hulls = removeInner(valid_hulls)

for hull in valid_hulls:
    cv.drawContours(image, [hull], 0, (0, 255, 0), 2)
    
cv.imshow("Cones detected", image)
cv.imwrite("step3.png", image)
cv.waitKey(0)

# Step 4 - Saving bounding boxes to txt

with open("boxes.txt", "w") as file:
    for hull in valid_hulls:
        rect = cv.boundingRect(hull)
        file.write(f"${assessColor(hsv_img, hull, cv.bitwise_or(mask_black, mask_white))}: ${(rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3])}\n")
        