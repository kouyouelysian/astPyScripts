#================ IMPORTS ================#

from pydub import AudioSegment
import os
import sys
import getopt
import shutil

#================ GLOBALS ================#

glob_help_string = """
This utility batch-processes wav audiofiles:
1. It repeats each audiofile X times
2. Puts an N seconds long slice of the beginning after repeats, with a fadeout.
3. Batch-renderes the repeat+fade version in different formats.
   For each formats, a subfolder with its name is auto-created (wav, flac, mp3, ...)
   You can opt to purge the already existing folders, if the script detects any.
   This WILL destroy their contents! Do it manually if you think you'll need them.
   So far the supported formats are: wav, mp3, flac.

Mostly it's useful for VGM batch editing: you want to loop each track a few times,
and then fade it out, and often the track count racks up to a hundred of files. But you can
also use it for general batch-conversion to mp3 or flac - just set the repetitions to 1
and fadeout to 0. 

Usage:
ast_rfmeu.py [options]

-h: display help
-v: verbose
-d, --directory: specify directory. Not specified = script works in its directory;
-r, --repeats: repeat times. defaults to 2
-o, --fadeout: fadeout repeat at th end, in seconds. defaults to 10
-f, --formats: output formats in one string thru commas. Example: wav,mp3,flac
"""

#================ FUNCTIONS ================#

'''
	tries to parse a string into an integer. returns False on fail.
'''
def prepareInt(arg):
	temp = 0
	try:
		temp = int(arg)
	except:
		return False
	return temp

'''
	backslash and whitespace bullshit
'''
def prepareFolderString(arg):
	# prepare the name
	if sys.platform == "linux" or sys.platform == "linux2":
	    # linux
	    arg = arg.replace("\\", "")

	elif sys.platform == "darwin":
	    # OS X
	    arg = arg.replace("\\", "")

	elif sys.platform == "win32":
	    # Windows...
	    arg = arg.replace("\\", "/")

	return arg.strip()

'''
	returns a list of all wav audiofiles in a given folder

	folder - target directory, defaults to script directory
	returns wavs, a list of strings of filenames
'''
def get_wavs_in_folder(folder = "./", verbose=False):
	if (not os.path.isdir(folder)):
		return False
	items = os.listdir(folder)
	wavs = []
	for f in items:
		if (os.path.isdir(f)):
			continue
		elif (f[0] == '.'):
			continue
		elif (not '.' in f):
			continue
		else:
			if ((f.split(".")[1] == "wav") or (f.split(".")[1] == "WAV")):
				wavs.append(f)	
	if (len(wavs) == 0):
		raise ValueError("the folder you provided has no wav audiofiles!")
	return wavs

'''
	exports a list of audiosegments to a named subfolder
	segments = list of pydub audiosegments
	names = list of names (must be same length and basically name each segment in order)
	folder = folder in which subfolders will be created, defaults to script folder
	format = output format of all files, defaults to wav

'''
def audiosegment_list_exporter(segments, files, folder = "./", audio_format = "wav", verbose = False):

	# get new folder path
	new_folder = os.path.join(folder, audio_format)
	if (verbose):
		print("\n\nnow exporting", len(segments), "segments to", new_folder, "as", audio_format, "files.")

	# check if the folder already exists, return False as error if it does
	if (os.path.isdir(new_folder)):
		return False

	os.mkdir(os.path.join(folder, audio_format))

	# make list of segments-names and export

	names = []
	for f in files:
		names.append(f.split('.')[0] + '.' + audio_format)

	print(names)

	list = tuple(zip(segments, names))
	for t in list:
		# t[0] = audiosegment, t[1] = name
		print(os.path.join(new_folder, t[1]))
		if (audio_format == "wav"):
			t[0].export(out_f = os.path.join(new_folder, t[1]), format = "wav")
		elif (audio_format == "mp3"):
			t[0].export(out_f = os.path.join(new_folder, t[1]), format = "mp3", codec = "mp3", bitrate="320k")
		else:
			t[0].export(out_f = os.path.join(new_folder, t[1]), format = audio_format, codec = audio_format)
	return True


'''
	wavs = list of wavefile names
	folder = path to the folder where the said wavefiles are
	returns segments, a list of pydub audiosegments
'''
def process_wavs_to_audiosegments(wavs, repeats, fadeout, folder, verbose=False):
	segments = []
	for w in wavs:
		if (verbose):
			print("processing: ", w)
		segments.append(repeat_and_fade(w, repeats, fadeout, folder))
	return segments

'''
	name = name of the file, e.g. painis.wav
	path = working folder
	returns audiosegment of a song
	renames the original file to e.g. painis-old.wav
	then saves the repeated and faded song as painis.wav
'''
def repeat_and_fade(name, repeats, fadeout, folder):
	song = AudioSegment.from_wav(os.path.join(folder, name))
	fadeout = min((fadeout)*1000, len(song))
	ending = song[:fadeout]
	song = song * repeats
	song += ending
	song = song.fade_out(int(fadeout/2))
	return song


'''
	gets options from command line upon script launch
'''
def get_opts(argv):

	formats = "wav"
	repeats = "2"
	fadeout = "10"
	verbose = False
	directory = "./"

	try:
		opts, args = getopt.getopt(argv,"hvf:r:o:d:",["formats=", "repeats=", "fadeout=", "directory="])
	except getopt.GetoptError:
		print('run ast_rfmeu.py -h for help')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(glob_help_string)
			sys.exit()
		elif opt == '-v':
			verbose = True
		elif opt in ("-f", "--formats"):
			formats = arg
		elif opt in ("-r", "--repeats"):
			repeats = arg
		elif opt in ("-o", "--fadeout"):
			fadeout = arg
		elif opt  in ("-d", "--directory"):
			directory = arg
	return directory, formats, repeats, fadeout, verbose

#================ MAIN RUN ================#

if __name__ == "__main__":
	print("\n\n~~~~~ Repeat/Fade/Multiexport Utility ~~~~~")
	print(" by Astro -> astrossoundhell.neocities.org")

	directory, formats, repeats, fadeout, verbose = get_opts(sys.argv[1:])

	if (formats == "wav" or directory == "./"):
		print("\nyou didn't specify some important parameters. Are you sure you want to run defaults? [Y/N]")
		temp = ""
		while (temp not in ["y", "n"]):
			temp = input("#: ")
			temp = temp.lower()
		if (temp == "n"):
			print('run ast_rfmeu.py -h for help')
			sys.exit(0)

				
	# check export formats

	if (verbose):
		print("\n\n\n======== preprocessing export format list...\n")
	allowed_formats = ["mp3", "wav", "flac"]
	provided_formats = formats.split(",")
	export_formats = []

	temp = 0
	for temp in range(len(provided_formats)):
		if (verbose):
			print("requested output format:", provided_formats[temp])
		if (not provided_formats[temp] in allowed_formats):
			if (verbose):
				print("  format is not one of the allowed formats - ignoring")
		else:
			export_formats.append(provided_formats[temp])
			if (verbose):
				print("  OK")
		temp += 1


	
	# start the whole conversion and repetition bullshit
	if (verbose):
		print("\n\n\n======== searching for wav files in provided folder...\n")
	folder = prepareFolderString(directory)
	wavnames = get_wavs_in_folder(folder, verbose)
	if (verbose):
		print("searching for wav files in", folder)
	if (not wavnames):
		raise ValueError("provided folder does not exist!")
	if (len(wavnames) == 0):
		print("no audio was found!")
		sys.exit(0)
	if (verbose):
		print("following wavefiles were found:")
		for w in wavnames:
			print("  -", w)


	# confirm the parameters with the user
	print("\n\n\n======== confirm parameters!\n")
	repeats = prepareInt(repeats)
	fadeout = prepareInt(fadeout)
	if (not repeats or not fadeout):
		raise ValueError("one or more of the INTEGER parameters (repeats, fadeout) is bad!")
	print("each song will be repeated", repeats, "times, then faded out in", fadeout, "seconds.")
	print("Exoprt formats are:")
	for f in export_formats:
		print("  -", f)
	print("following wavefiles are to be processed:")
	for w in wavnames:
		print("  -", w)
	print("is this OK? [Y/N]")
	yn = input("#: ").lower()

	# start processing and exporting
	if (yn == "y"):

		# check for dupe folders
		dupes = []
		for f in export_formats:
			if (os.path.isdir(os.path.join(folder, f))):
				dupes.append(os.path.join(folder, f))
		if (len(dupes) > 0):
			print("[!] dupe output folders found:")
			for d in dupes:
				print("  -", d)
			print("Delete these folders? [Y/N]")
			temp = ""
			while (temp not in ["y", "n"]):
				temp = input("#: ")
				temp = temp.lower()
			if (temp == "y"):
				# remove folders
				for d in dupes:
					shutil.rmtree(d)

			else:
				print("having these folders be most likely will make the script crash. You might want to remove them manually!")
			

		# batch process 
		print("\n\nprocessing audiofiles")
		segments = process_wavs_to_audiosegments(wavnames, repeats, fadeout, folder, verbose)

		for f in export_formats:
			if (verbose):
					print("\n\nexporting", f)
			success = audiosegment_list_exporter(segments, wavnames, folder, f, verbose)
			if (not success):
				raise ValueError("something went wrong during the export - most likely a dupe folder!")
			else:
				if (verbose):
					print("Done exporting", f)

	print("======== finished working!")
