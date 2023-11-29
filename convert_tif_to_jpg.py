# This script converts a TIFF to one or more JPEG(s).
# A TIFF may contain several frames/pages, and rather than
# one TIFF such as 001.tif with multiple pages,
# we want all of its frames as individual JPEG:s in a folder 
# named after the TIFF: 001/001.jpg, 001/002.jpg etc.

from PIL import Image
import os

INPUT_FOLDER = "M:/Faksimiili/Ehrstrom_HKA/Mechelin_Leo_1905_1913"
OUTPUT_FOLDER = "M:/Faksimiili/Ehrstrom_HKA/jpg/Mechelin_Leo_1905_1913"

def convert_tif_to_jpg():
    # loop through the tif files in the input folder
    for tif_file in os.listdir(INPUT_FOLDER):
        if tif_file.endswith(".tif"):
            tif_path = os.path.join(INPUT_FOLDER, tif_file)
            # for each tif file: create a directory for its jpg:s
            # named after the tif file
            output_dir = os.path.join(OUTPUT_FOLDER, os.path.splitext(tif_file)[0])
            os.makedirs(output_dir, exist_ok=True)
            print(str(output_dir))
            with Image.open(tif_path) as img:
                # loop through each frame (page) in the tif file
                for i in range(img.n_frames):
                    img.seek(i)
                    # create the output path, the image nr padded with leading zeros
                    output_path = os.path.join(output_dir, f"{i+1:03d}.jpg")
                    # save the frame as a jpg file, setting the quality as desired
                    img.save(output_path, "jpeg", quality=92)

def main():
    convert_tif_to_jpg()
    print("All files converted.")

main()