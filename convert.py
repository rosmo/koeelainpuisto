#!/usr/bin/env python3
import sys

from mutagen.mp3 import MP3
audio = MP3(sys.argv[1])
audio_length = audio.info.length

f = open(sys.argv[2], "r")
current_time = 0
for l in f.readlines():
    segment = l.strip().split("-")
    print('%d\t%d\tmusic' % (current_time, int(segment[0])-1))
    print('%d\t%d\tspeech' % (int(segment[0]), int(segment[1])))
    current_time = int(segment[1]) + 1

print('%d\t%d\tmusic' % (current_time, int(audio_length)))
