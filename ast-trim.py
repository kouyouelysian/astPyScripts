##======== some local under-the-hood settings...

import os
from os import listdir
from os.path import isfile, join
from sys import platform
from pydub import AudioSegment

##======== functions

'''
backslash bullshit
'''
def preparePathString(arg):
    # prepare the name
    if platform == "linux" or platform == "linux2":
        # linux
        arg = arg.replace("\\", "")

    elif platform == "darwin":
        # OS X
        arg = arg.replace("\\", "")

    elif platform == "win32":
        # Windows...
        arg = arg.replace("\\", "/")

    return arg


def detect_leading_silence(sound, silence_threshold=-20.0, chunk_size=0.3):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

##======== runtime

print("\n\n\n=== astro's cool wavefile trimmer ===\n\n\n")

## get path and format variables

pat = input("input working path: ")
if (pat == ""):
    raise SystemExit("Provide a path!!!\n\n\n")
pat = preparePathString(pat).strip()

ext = input("\ninput files extension (defaults to wav): ")
if (ext == ""):
    ext = "wav"

thresh = input("\ninput threshold (negative float, defaults to -50.0): ")
if (thresh != ""):
    thresh = float(thresh)
else:
    thresh = -50.0

## grab all files of 'ext' format in 'pat' directory as a list
print("\n\nworking...")
targets = [f for f in listdir(pat) if (isfile(join(pat, f)) and (join(pat, f)[-3:] == "wav"))]
print("successfully grabbed files.\n\n")

##====== PROCESS EACH

for item in targets:
    print("now processing: " + item + "...")
    sound = AudioSegment.from_file(join(pat, item), format=ext)

    start_trim = detect_leading_silence(sound, thresh)
    end_trim = detect_leading_silence(sound.reverse(), thresh)
    duration = len(sound)    
    trimmed_sound = sound[start_trim:duration-end_trim]
    trimmed_sound.export(join(pat, ("trimmed-"+item)), format=ext)



