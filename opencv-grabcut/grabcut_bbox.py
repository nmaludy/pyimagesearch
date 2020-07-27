# -----------------------------
#   USAGE
# -----------------------------
# python grabcut_bbox.py

# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
import numpy as np
import argparse
import time
import cv2
import os

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, default=os.path.sep.join(["images", "adrian.jpg"]),
                help="Path to the input image that is going to apply GrabCut to")
ap.add_argument("-c", "--iter", type=int, default=10,
                help="Number of GrabCut iterations (larger value => slower runtime)")
args = vars(ap.parse_args())

# Load the input image from disk and then allocate memory for the output mask generated by the GrabCut method
# -- this mask should have the same spatial dimensions as the input image
image = cv2.imread(args["image"])
mask = np.zeros(image.shape[:2], dtype="uint8")

# Define the bounding box coordinates that approximately define the face and the neck regions (i.e, all visible skin)
rect = (151, 43, 236, 368)

# Allocate the memory for two arrays that the GrabCut algorithm internally uses
# when segmenting the foreground from the background
fgModel = np.zeros((1, 65), dtype="float")
bgModel = np.zeros((1, 65), dtype="float")

# Apply GrabCut using the bounding box segmentation method
start = time.time()
(mask, bgModel, fgModel) = cv2.grabCut(image, mask, rect, bgModel,
                                       fgModel, iterCount=args["iter"], mode=cv2.GC_INIT_WITH_RECT)
end = time.time()
print("[INFO] Applying GrabCut took {:.2f} seconds".format(end - start))

# The output mask has 4 possible output values, marking each pixel in the mask as:
# (1) Definite Background;
# (2) Definite Foreground;
# (3) Probable Background;
# (4) Probable Foreground;
values = (("Definite Background", cv2.GC_BGD), ("Probable Background", cv2.GC_PR_BGD),
          ("Definite Foreground", cv2.GC_FGD), ("Probable Foreground", cv2.GC_PR_FGD))

# Loop over the possible GrabCut mask values
for (name, value) in values:
    # Construct a mask for each one of the current values
    print("[INFO] Showing mask for '{}'".format(name))
    valueMask = (mask == value).astype("uint8") * 255
    # Display the mask in order to visualize it
    cv2.imshow(name, valueMask)
    cv2.waitKey(0)

# Set all definite background and probable background pixels to 0 while definite background and probable foreground to 1
outputMask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1)

# Scale the mask from the range [0, 1] to [0, 255]
outputMask = (outputMask * 255).astype("uint8")

# Apply a bitwise AND to the image using the mask generated by the GrabCut in order to generate the final output image
output = cv2.bitwise_and(image, image, mask=outputMask)

# Show the input image followed by the mask and output generated by GrabCut and bitwise masking
cv2.imshow("Input", image)
cv2.imshow("GrabCut Mask", outputMask)
cv2.imshow("GrabCut Output", output)
cv2.waitKey(0)