#!/usr/bin/env python3
import sys
import os
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC, CHAP

for file_name in sys.argv[1:len(sys.argv)]:
    print('Processing: %s' % (file_name))
    file_name_s = os.path.splitext(file_name)
    file_name_ya = os.path.basename(file_name_s[0])
    print('Base name: %s' % (file_name_ya))
    mp3_file = 'output/%s.mp3' % (file_name_ya)
    file_info = {}
    with open(file_name, 'r') as infile:
        file_info = json.load(infile)
     try: 
        tags = ID3(mp3_file)
    except ID3NoHeaderError:        
        tags = ID3()

    if len(tags.getall(u"SYLT::'en'")) != 0:
        tags.delall(u"SYLT::'en'")
        tags.delall(u"SYLT::'fi'")
        tags.save(mp3_file)

    captions = []
    for caption_key, caption in file_info['captions'].items():
        segment_start, segment_end = caption_key.split("-", 2)
        segment_start = int(float(segment_start) * 1000)
        segment_end = int(float(segment_end) * 1000)
        captions.append((caption, segment_start))
        tags.add(CHAP(element_id=caption_key, start_time=segment_start, end_time=segment_end))
    tags.setall("SYLT", [SYLT(encoding=Encoding.UTF8, lang='eng', format=2, type=1, text=captions)])
    print('Saving tags to: %s' % (mp3_file))
    tags.save(v2_version=3)
