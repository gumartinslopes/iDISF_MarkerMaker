# Given a binary image, counts the amount of 
# object pixels and background pixels.

import cv2
img = cv2.imread('ue_result.png', cv2.IMREAD_GRAYSCALE)
cont_o = 0
cont_b = 0
for i in img:
    for j in i:
        if j > 0:
            cont_o += 1
        else:    
            cont_b += 1
print("Object pixels: ", cont_o)
print("Background pixels: ", cont_b)