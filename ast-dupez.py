##========           ======##
##======== AST-DUPEZ ======##
##========  1.0      ======##

# a program that finds and removes file dupes in a given folder (at least attempts to)
# within a given error margin
# mainly intended to use with sample ripping programs
# it is a bit esotheric...

##========
##======== under the hood vars, imports
##========

import platform
from os import listdir, remove, chmod
from os.path import isfile, join, getsize

workingFolder = "" 
totalFiles = 0
totalChunks = 0
totalDupes = 0

writeoutName = "" # vars concerning script writeout
writeoutContent = ""
writeoutFname = ""

temp = None # just a temporary holder

##========
##======== runtime parameters
##========

rtpCompareError = 32 # [minimum n of mismatches to treat files as different]
rtpChunkDivError = 64 # [bytes]
writeoutName = "dupez_output" # [string], default value set here
v = False # verbose flag, [bool]
l = False # local deletion flag. [False] makes a .bat / .txt / .command file in workingfolder instead. [bool]

##========
##======== function/class definitions
##========

# a class of size-path pair because i couldn't do a do with the dictionary. sorry not sorry.
class cFile: 
	def __init__(self, fname, fsize):
		self.fname = fname
		self.fsize = fsize

# the function called on a list of similar-sized files from main runtime. the 'main' one
def processChunkList(chlist):
	output = []
	chunkLen = len(chlist)
	if (chunkLen == 0):
		if (v):
			print("null chunk. skipping...")
		return []

	elif (chunkLen < 2):
		if (v):
			print("chunk consists of 1 file. skipping...")
		return []
	temp = 0
	i = 0
	while (temp < chunkLen):
		i = temp+1
		while (i < chunkLen):
			if (v):
				print("\ncomparing: \n-- ", chlist[temp], "\n-- ", chlist[i])
			err = getListsError(fileToByteList(chlist[temp]), fileToByteList(chlist[i]))
			if (v):
				print("# of mismatches: ", err)
			if (err < rtpCompareError):
				if (v):
					print("\n\n[!] Found dupes: \n-- ", chlist[temp], "\n-- ", chlist[i], "\n")
				output.append(chlist[i])
			i += 1
		temp += 1
	return output

# gets a file by path fname and returns a list of byte objects
def fileToByteList(fname):
	output = []
	with open(fname, "rb") as fhandle:
		byte = fhandle.read(1)
		while byte != b"":
			output.append(byte)
			byte = fhandle.read(1)
	return output

# compares two lists l1 and l2 and returns the difference of elements inside of them as integer
def getListsError(l1, l2):
	sizeDiff = abs(len(l1) - len(l2))
	errCount = sizeDiff
	compFor = min(len(l1), len(l2))
	temp = 0
	while (temp < compFor):
		if (l1[temp] != l2[temp]):
			errCount += 1
		temp += 1
	return errCount


##========
##======== parameters asking
##========

print('~ AST-DUPEZ ~')

# get directory
workingFolder = input('\n\nplease provide working folder:').strip()

# get parameters
temp = input("do you wish to input custom working parameters? (y/n)")

if (temp == "n") or (temp == "N"):
	# if 'no'
	print('will work with default parameters.')
elif (temp == "y") or (temp == "Y"):
	# if 'yes'
	temp = input('file comparison error threshold, quantity [def 32]: ')
	if (temp.isdigit()):
		rtpCompareError = int(temp)
	temp = input('chunk step difference, bytes [def 32]: ')
	if (temp.isdigit()):
		rtpChunkDivError = int(temp)
	temp = input('set Verbose flag to True? [def n] (y/n): ')
	if (temp == "y") or (temp == "Y"):
		v = True
	temp = input('writeout delete script instead of auto-deleting dupes? [def n] (y/n): ')
	if ((temp == "y") or (temp == "Y")):
		l = False
		temp = input('input outfile name WITHOUT extention [blank for default]:')
		if (not temp == ""):
			writeoutName = temp
else:
	# if bad parameter
	print('got bad responce. will work with default parameters.')

# print 'working' message in case verbose flag is down
if not (v):
	print("working, please be patient...")

##========
##======== main runtime
##========

# get dict of files in directory
fDict = []
for f in listdir(workingFolder):
	if isfile(join(workingFolder, f)):
		temp = join(workingFolder, f)
		fDict.append(cFile(temp, getsize(temp)))
		totalFiles += 1

# sort dict by size to temp

temp = sorted(fDict, key=lambda x: x.fsize, reverse=False)
fDict = temp
temp = None

if (v):
	print("\n\n\n== SORTED ITEMS ==")
	for item in fDict:
		print("#-- ", item.fsize, item.fname)
	print("\n\n\n")

# divide into chunks 
markers = [] # list of keys that are the first items of new chunk
sOld = 0
sNew = 0

for item in fDict:
	sNew = item.fsize
	if (abs(sNew - sOld) > rtpChunkDivError):
		markers.append(item.fname)
		totalChunks += 1
	sOld = sNew

if (v): # verbose message
	print("\n\n\n== CHUNK MARKERS ==")
	for item in markers:
		print(item)
	print("\n\n\n")

# inside each chunk, compare all files
chunkFilesList = []
dupeList = []
for item in fDict:
	if (item.fname in markers): # if the file we found is a marker, process everything we've collected before
		dupeList += processChunkList(chunkFilesList) # process collected list
		chunkFilesList = [] # wipe it out

	chunkFilesList.append(item.fname) # append next file into the list

# post-compare actions
dupeList += processChunkList(chunkFilesList) # process the last listing
dupeList = list(set(dupeList)) # dedupe the dupe filenames list (lmao)
totalDupes = len(dupeList)

if (v): # verbose message
	print("\n\n\n== DUPE LIST ==")
	for item in dupeList:
		print(item)
	print("\n\n\n")

# deletion action

if (l): # if local delete is set to true
	# delete files locally thru os.remove
	for dupe in dupeList:
		remove(dupe)
else: # else (if it is false)
	# writeout a command file
	opsys = ""
	cmdExt = "sh"
	cmdDel = "rm "
	cmdHead = ""

	# format nerdery. 
	if platform.system().startswith('Linux'):
		opsys = "lin"
		cmdHead = "#!/bin/bash"

	elif platform.system().startswith('Darwin'):
		opsys = "mac"
		cmdExt = "command"

	elif platform.system().startswith('Windows'):
		opsys = "win"
		cmdDel = "del "
		cmdExt = "bat"

	else: # if we don't know the OS
		raise ValueError('OS unsupported, sowwy! Try local deletion.')

	# combine name and contents
	writeoutFname = join(workingFolder, writeoutName + "." + cmdExt)
	writeoutContent += cmdHead + "\n";
	for dupe in dupeList:
		writeoutContent += cmdDel + dupe + "\n"

	# write a file
	fhandle = open(writeoutFname, "w+")
	fhandle.write(writeoutContent)
	fhandle.close()

	if ((opsys == "lin") or (opsys == "mac")):
		chmod(writeoutFname, 0o777)

## print endprogram message
print("\n\ntotal files: ", totalFiles, "\ntotal chunks: ", totalChunks, "\ntotal dupes: ", totalDupes, "\n\n\n")
