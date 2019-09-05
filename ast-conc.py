##========          ======##
##======== AST-CONC ======##
##========   1.0    ======##

## script for generating an SOX command that concatenates all of the files in a folder together
## but inserts a silence separator between every file
##
## done for merging a bunch of ripped samples

##======== some local under-the-hood settings...

maxOpen = 10
chlist = []

import os
from os import listdir
from os.path import isfile, join

##======== functions

def prepareFiles(targets, rate, volume):
	global output
	newTargets = []
	for item in targets:
		output += "sox -D -G "
		output += item
		output += " -r "
		output += rate
		output += " "
		output += item + ".wav "
		output += " vol "
		output += volume
		output += "\n"
		newTargets.append(item + ".wav")
	output += "\n"
	return newTargets


def makeRemoveFiles(locTargets):
	global output
	for item in locTargets:
		output += "rm "
		output += item
		output += "\n"
	output += "\n\n"


def makeChunks(locTargets, locPass):
	head = 0;
	ticks = 0;

	global chlist
	global chunks
	global smr
	global spath
	global pat
	global maxOpen
	global output

	chlist = []
	chunks = 0

	while ((head + maxOpen) < len(locTargets)):
		## make a chunk
		output += "sox "
		ticks = 0
		while (ticks < maxOpen):
			output += locTargets[head + ticks]
			output += " "
			ticks += 1
			if (sdo == True):
				output += "-r "
				output += smr
				output += " "
				output += spath
				output += " "

		## add chunk to chunks list and to output list
		head += maxOpen
		chname = join(pat,("chunk" + str(chunks) + "pass" + str(locPass) + "." + ext))
		chlist.append(chname)
		output += chname
		output += "\n\n\n"
		chunks += 1


	## make the last chunk
	output += "sox "
	while (head < len(locTargets)):
		output += locTargets[head]
		output += " "
		if (sdo == True):
			output += "-r "
			output += smr
			output += " "
			output += spath
			output += " "
		head += 1

	## add chunk to chunks list and to output list
	chname = join(pat,("chunk" + str(chunks) + "pass" + str(locPass) + "." + ext))
	chlist.append(chname)
	output += chname
	output += "\n\n"


##======== runtime

print("\n\n\n=== astro's cool file concatenator ===\n\n\n")

## get path and format variables

pat = input("input working path: ")
if (pat == ""):
	raise SystemExit("Provide a path!!!\n\n\n")

sdo = False;
spath = input("\ninput silence separator file;\nmust be same format as grabbed files;\nleave blank for no separator.\n?:")
if (spath == ""):
	print("no silence separation will be done.")
else:
	sdo = True;

ext = input("\ninput files extension (defaults to wav): ")
if (ext == ""):
	ext = "wav"

opn = input("\nresulting file name (blank for default): ")
if (opn == ""):
	opn = "coolConcatOut"

smr = input("\nforce resample all files to custom rate?\nInput frequency (just the number) to resample.\nleave blank for default 44100Hz.\n?: ")
if (smr == ""):
	smr = "44100"

vol = input("\ndecrease volume of all samples to prevent clipping?\n (real number from 0.0 to 1.0, leave blank for default 1.0)\n?: ")
if (vol == ""):
	vol = "1.0"

## grab all files of 'ext' format in 'pat' directory as a list
print("\n\nworking...")
targets = [join(pat, f) for f in listdir(pat) if (isfile(join(pat, f)) and (join(pat, f)[-3:] == "wav"))]
print("successfully grabbed files.\n\n")

## ask for a silence file



##====== MAKE TEXT OF A SCRIPT

## variable to put command text into

output = ""

## prepare files

targets = prepareFiles(targets, smr, vol)
if (sdo == True):
	output += "sox " + spath + " -r " + smr + " " + spath + ".wav\n\n"
	spath += ".wav"

## recursive chunk making...

stage = 0

while (1):
	makeChunks(targets, stage)
	if (chunks < maxOpen):
		makeRemoveFiles(targets)
		break
	makeRemoveFiles(targets)
	targets = chlist
	stage += 1

# when there is less chunks than max files open of SOX concat them into final file

targets = chlist
output += "sox "
for item in targets:
	output += "-r "
	output += smr
	output += " "
	output += item
	output += " "
	if (sdo == True):
		output += "-r "
		output += smr
		output += " "
		output += spath
		output += " "

output += join(pat, opn + "." + ext)
output += ("\n\n")

## remove chunks

makeRemoveFiles(chlist)

## remove resampled silence

output += "rm "
output += spath
output += "\n"
	
##======== WRITE FILE WITH COMMAND

fname = input("\n\ninput filename to create (with extension), blank for default: ")
if (fname == ""):
	fname = "concatScript.txt"

fname = join(pat, fname)

fhandle = open(fname, "w+")
fhandle.write(output)
fhandle.close()
