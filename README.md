# SCAMP Colour Extraction

# Introduction
This repository is part of a Final Year EEE Project to add colour acquisition to a monochrome camera known as the [SCAMP Vision Sensor](https://personalpages.manchester.ac.uk/staff/p.dudek/scamp/). This repository contains code mainly used to extract the pixels of a colourised SCAMP image in a csv format ready for creating graphs in Excel or Matlab, but also has other features such as performing colour correction transformation and compiling images into a video. This exists as several programs that each take image data from the [SCAMP Image Acquisition repository](https://github.com/aleifericsson/SCAMP-Image-Acquisition) to function.

# Installation
All of the programs here have been written in Python 3.14. To run the program, ensure your system has Python 3.14 and use [pip](https://pypi.org/project/pip/) to install the libraries listed on the top of each program.

# Usage/Workflow
1. Import the folder of images with numbered .png files into the same directory from [Image Acquisition](https://github.com/aleifericsson/SCAMP-Image-Acquisition)
2. Run pixel_extracter.py to open an image and extract the hex colour codes of the primary red, green and blue squares of the [ColorChecker](https://en.wikipedia.org/wiki/ColorChecker). This requires pressing on the codes of the squares (13, 14, 15) and defining the corresponding squares' regions on image, then pressing the export button.
3. Run matrix_maker.py and use those values to produce a .txt file of the transformation matrix, which should be made into the same directory
4. Run video_player.py to load the folder of images and view it as a video
5. Press the "Load Matrix" button and load the matrix produced by matrix_maker.py. Tweak saturation and lightness as needed and press "Apply Matrix".
6. Press "Export to MP4" to export the video.
7. Run pixel_extracter.py again on the transformed images of the video to define regions of all the squares of the ColorChecker for extraction.

# References
The method of deriving and using the transformation matrix has been obtained from the following paper:

Zhen Zeng, Hongzhi Jia. 2014 "[Color restoration in the black-and-white video camera](https://doi.org/10.1016/j.ijleo.2013.09.082)". Optik Volume 125, Issue 8, April 2014, Pages 1918-1921. https://doi.org/10.1016/j.ijleo.2013.09.082

# Previews
### pixel_extracter.py
<img width="900" height="562" alt="image" src="https://github.com/user-attachments/assets/5b830eaa-4313-4feb-a5fb-94ded243433b" />

### video_player.py
<img width="267" height="656" alt="image" src="https://github.com/user-attachments/assets/5cf6cad1-99a1-4a44-81dd-5b8f3c3ca15b" />

# Future Improvements
- Automate the entire workflow to be able to be done in one program


