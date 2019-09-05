##========           ======##
##======== AST-CROP  ======##
##========   1.0     ======##

# a program that crops all pictures to given size in a folder

##========
##======== under the hood vars, imports
##========

import cv2
import numpy as np
from os import listdir, remove, mkdir
from os.path import isfile, join, exists

temp = None # just a temporary holder
scaleSafetyMargin = 10 # a little safety measure for scale feature. nudge it if you know what you are doing

##========
##======== runtime parameters
##========

rtpTargetX = 600 # target image width [px]
rtpTargetY = 600 # target image height [px]
rtpAlignX = 0 # horizontal align, -1 left, 0 center, 1 right [int]
rtpAlignY = 0 # vertical align, -1 top 0 center 1 bototm [int]
rtpUseScaledown = False # scaledown images that are too big [bool]

v = False # verbose flag

##========
##======== function/class definitions
##========

##========
##======== parameters asking
##========

print('\n\n~ AST-CROPALL ~')

# get directory
workingFolder = input('\n\nplease provide working folder with images\n(accepted formats: jpg, png)\n?: ').strip()

# get parameters
temp = input("\ndo you wish to input custom working parameters? (y/n)\n")
if (temp == "y") or (temp == "Y"):
	# if 'yes'
	temp = input('\ntarget image width, px: ')
	try:
		temp = int(temp)
		rtpTargetX = int(temp)
	except ValueError:
		raise ValueError('input an integer!')
	temp = input('target image height, px: ')
	try:
		temp = int(temp)
		rtpTargetY = int(temp)
	except ValueError:
		raise ValueError('input an integer!')
	temp = input('image hor align [-1 left, 0 mid, 1 right]: ')
	try:
		temp = int(temp)
		rtpAlignX = int(temp)
	except ValueError:
		raise ValueError('input an integer!')
	temp = input('image vert align [-1 top, 0 mid, 1 bottom]: ')
	try:
		temp = int(temp)
		rtpAlignY = int(temp)
	except ValueError:
		raise ValueError('input an integer!')
	temp = input('scale down bigger images to best fit? [def n] (y/n): ')
	if (temp == "y") or (temp == "Y"):
		rtpUseScaledown = True
	temp = input('set Verbose flag to True? [def n] (y/n): ')
	if (temp == "y") or (temp == "Y"):
		v = True
elif (temp == "n") or (temp == "N"):
	# if 'no'
	print('will work with default parameters.\n\n')
else:
	# if bad parameter
	print('got bad responce. will work with default parameters.\n\n')

##========
##======== main runtime
##========

# put non-verbose runtime message
if (not v):
	print('\nworking...\n')

# get dict of files in directory
imList = []
for f in listdir(workingFolder):
	if (isfile(join(workingFolder, f)) and (f.endswith('jpg') or f.endswith('png'))):
		temp = join(workingFolder, f)
		imList.append(temp)
if (v):
	print("\n\n=== list of found images ===")
	for f in imList:
		print(f)

# make a directory for cropped images
outputDir = join(workingFolder, "cropped")
if (not exists(outputDir)):
	mkdir(outputDir)

# process every image
imCount = 0
ext = ''
xStart = 0
xEnd = 0
yStart = 0
yEnd = 0

for im in imList:
	# read the next image, get its extention
	imHandle = cv2.imread(im);
	if (im.endswith('png')):
		ext = 'png'
	elif (im.endswith('jpg')):
		ext = 'jpg'

	# get width/height of original image
	h, w, temp = imHandle.shape
	if (v):
		print("\n\n--NEXT IMAGE: ", im, "\n   size: ", h, 'x', w)

	# if image is smaller than needed width/height - scale it up
	if (w < rtpTargetX or h < rtpTargetY):
		if (v):
			print('upscaling ', im, ', image too small')
		temp = max((rtpTargetX+scaleSafetyMargin)/w, (rtpTargetY+scaleSafetyMargin)/h)
		imHandle = cv2.resize(imHandle,(int(temp*w),int(temp*h)))

	# if scaledown is enabled, check if image is too big and do the stuff if it is
	elif ((w > rtpTargetX or h > rtpTargetY) and (rtpUseScaledown)):
		if (v):
			print('downscaling ', im, ', image too big')
		temp = max((rtpTargetX+scaleSafetyMargin)/w, (rtpTargetY+scaleSafetyMargin)/h)
		imHandle = cv2.resize(imHandle,(int(temp*w),int(temp*h)))

	# re-get the width/height of the new image
	h, w, temp = imHandle.shape
	if (v):
		print("New size: ", h, 'x', w)

	# calculate the start and end points for horizontal cropping
	if (rtpAlignX == -1):
		# if hor align is left
		xStart = 0
		xEnd = rtpTargetX
	elif (rtpAlignX == 0):
		# if hor align is center
		xStart = int((w/2) - (rtpTargetX/2))
		xEnd = int((w/2) + (rtpTargetX/2))
	elif (rtpAlignX == 1):
		# if hor align is right
		xStart = w - rtpTargetX
		xEnd = w
	else:
		# if hor align is some bullshit 
		raise ValueError('Bad hor align index!')

	# calculate the start and end points for vertical cropping
	if (rtpAlignY == -1):
		# if vert align is top
		yStart = 0
		yEnd = rtpTargetY
	elif (rtpAlignY == 0):
		# if vert align is mid
		yStart = int((h/2) - (rtpTargetY/2))
		yEnd = int((h/2) + (rtpTargetY/2))
	elif (rtpAlignY == 1):
		# if vert align is bottom
		yStart = h - rtpTargetY
		yEnd = h
	else:
		# if hor align is some bullshit 
		raise ValueError('Bad vert align index!')

	if (v):
		print("cropping:\n--hor ", xStart, "~", xEnd, "\n--ver ", yStart, "~", yEnd)

	# crop the image
	imHandle = imHandle[yStart:yEnd, xStart:xEnd]
	temp = join(outputDir, str(imCount)+'.'+ext)
	if (v):
		print('cropped OK, saving as ', temp, '...' )
	cv2.imwrite(temp, imHandle)
	imCount += 1

## print endprogram message
print("\ndone\n")
