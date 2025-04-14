import cv2
import os
import tkinter as tk
from tkinter import filedialog

# Function to select multiple images
def select_images():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("JPEG files", "*.jpg")])
    return file_paths

# Function to create video from images
def create_video_from_images(image_files, output_video_path, fps=30):
    if len(image_files) == 0:
        print("No images selected.")
        return
    
    # Read the first image to get the dimensions
    frame = cv2.imread(image_files[0])
    height, width, layers = frame.shape
    size = (width, height)

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can change the codec (e.g., 'MP4V' for MP4)
    out = cv2.VideoWriter(output_video_path, fourcc, fps, size)

    # Loop through all image files and write them to the video
    for image_file in image_files:
        img = cv2.imread(image_file)
        out.write(img)

    # Release the video writer
    out.release()
    print(f"Video saved to {output_video_path}")

# Main program
if __name__ == "__main__":
    image_files = select_images()
    if image_files:
        # Prompt for output video file name
        output_video_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI files", "*.avi"), ("MP4 files", "*.mp4")], title="Save Video As")
        if output_video_path:
            create_video_from_images(image_files, output_video_path, fps=30)
        else:
            print("No output file selected.")
    else:
        print("No images selected.")
