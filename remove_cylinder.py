import pydicom
import glob
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import re

# Specify the path to your DICOM directory and a sample DICOM file for adjustment
dicom_dir = '/Users/tonganze/Desktop/Cam IIA/GG2/Low resolution reconstructed CT data-20240527/merged_dicom'
dicom_file = '/Users/tonganze/Desktop/Cam IIA/GG2/Low resolution reconstructed CT data-20240527/merged_dicom/a_0048.dcm'

# Initial guess for the parameters
x, y, r = 251, 264, 207  # Adjusted initial values for a smaller circle
rect_left = (39, 206, 50, 110)  # Rectangle mask for the left side (x, y, width, height)
rect_right = (413, 210, 50, 110)  # Rectangle mask for the right side (x, y, width, height)

def visualize_circle_and_rectangles(image, x, y, r, rect_left, rect_right):
    # Create a copy of the image
    img_copy = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    # Draw the circle on the image copy
    cv2.circle(img_copy, (x, y), r, (0, 255, 0), thickness=2)
    # Draw rectangles on the image copy
    cv2.rectangle(img_copy, (rect_left[0], rect_left[1]), (rect_left[0]+rect_left[2], rect_left[1]+rect_left[3]), (0, 255, 0), 2)
    cv2.rectangle(img_copy, (rect_right[0], rect_right[1]), (rect_right[0]+rect_right[2], rect_right[1]+rect_right[3]), (0, 255, 0), 2)
    return img_copy

def remove_outer_circle(image, x, y, r):
    # Create a mask for the circle
    mask = np.zeros_like(image, dtype=np.uint8)
    cv2.circle(mask, (x, y), r, (255, 255, 255), thickness=-1)
    mask = mask == 0
    image[mask] = 0
    return image

def remove_outer_circle_and_rectangles(image, x, y, r, rect_left, rect_right):
    # Remove the outer circle
    image = remove_outer_circle(image, x, y, r)
    
    # Create masks for the rectangles
    image[rect_left[1]:rect_left[1]+rect_left[3], rect_left[0]:rect_left[0]+rect_left[2]] = 0
    image[rect_right[1]:rect_right[1]+rect_right[3], rect_right[0]:rect_right[0]+rect_right[2]] = 0

    return image

def process_dicom(file_path, x, y, r, rect_left, rect_right, apply_rectangles, preview=False):
    # Read the DICOM file
    dicom_dataset = pydicom.dcmread(file_path)

    # Extract the image data
    if hasattr(dicom_dataset, 'pixel_array'):
        pixel_array = dicom_dataset.pixel_array

        # Remove the outer circle and rectangles if needed
        if apply_rectangles:
            processed_image = remove_outer_circle_and_rectangles(pixel_array, x, y, r, rect_left, rect_right)
        else:
            processed_image = remove_outer_circle(pixel_array, x, y, r)

        if preview:
            return processed_image, pixel_array

        # Save the modified image as a new DICOM file
        dicom_dataset.PixelData = processed_image.tobytes()
        output_path = os.path.join(dicom_dir, 'processed_' + os.path.basename(file_path))
        dicom_dataset.save_as(output_path)
        print(f"Processed file saved to: {output_path}")

    else:
        print(f"No image data found in {file_path}")

# Read the DICOM file and get the image
image = process_dicom(dicom_file, x, y, r, rect_left, rect_right, apply_rectangles=True, preview=True)

if image is not None:
    processed_image, original_image = image
    while True:
        # Display the image with the current circle and rectangle overlays
        img_with_overlays = visualize_circle_and_rectangles(original_image, x, y, r, rect_left, rect_right)
        plt.imshow(img_with_overlays, cmap='gray')
        plt.title("Adjust the circle and rectangle parameters")
        plt.show()

        # Interactive input for adjusting the parameters
        adjust = input("Adjust (x/y/r/rect_left/rect_right) or done? ").strip().lower()
        if adjust == 'x':
            x = int(input("Enter new x coordinate: "))
        elif adjust == 'y':
            y = int(input("Enter new y coordinate: "))
        elif adjust == 'r':
            r = int(input("Enter new radius: "))
        elif adjust == 'rect_left':
            rect_left = tuple(map(int, input("Enter new left rectangle (x, y, width, height): ").split()))
        elif adjust == 'rect_right':
            rect_right = tuple(map(int, input("Enter new right rectangle (x, y, width, height): ").split()))
        elif adjust == 'done':
            break
        else:
            print("Invalid input. Please enter 'x', 'y', 'r', 'rect_left', 'rect_right', or 'done'.")

    # Apply the final parameters to the selected range of images in the directory
    dicom_files = glob.glob(f"{dicom_dir}/*.dcm")

# Adjust the loop to handle filenames correctly
for dicom_file in dicom_files:
    # Extract the number from the filename to check the range
    base_name = os.path.basename(dicom_file)
    
    # Use a regular expression to find all numbers in the filename
    numbers = re.findall(r'\d+', base_name)
    
    # If numbers are found, proceed with the first number
    if numbers:
        file_number = int(numbers[0])
        
        if file_number >= 930:
            process_dicom(dicom_file, x, y, r, rect_left, rect_right, apply_rectangles=True)
        elif file_number < 930:
            process_dicom(dicom_file, x, y, r, rect_left, rect_right, apply_rectangles=False)
else:
        print(f"No numeric value found in filename: {base_name}")

