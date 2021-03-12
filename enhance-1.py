#!/usr/bin/env python3
import sys
import os
import json
import pickle
import subprocess
from pyAudioAnalysis import audioSegmentation as aS
from mutagen.mp3 import MP3

model = sys.argv[1]
for file_name in sys.argv[2:len(sys.argv)]:
    print('Processing: %s' % (file_name))
    file_name_s = os.path.splitext(file_name)
    file_name_ya = os.path.basename(file_name_s[0])
    print('Base name: %s' % (file_name_ya))
    
    audio = MP3(file_name)
    audio_length = audio.info.length
    print('Audio length: %d seconds' % (audio_length))
    file_name_wav = 'output-wav/%s.wav' % (file_name_ya)  
    if not os.path.exists(file_name_wav):
        print('Converting to %s from %s' % (file_name_ya, file_name))
        result = subprocess.run(["ffmpeg", "-i", file_name, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000", file_name_wav])
    else:
        print('Already exists: %s' % (file_name_wav))
    predict = {}
    predict[file_name_s[0]] = {"segments": {}}
    segments = {"speech": [], "music": []}
    pickle_file = 'pickle/%s.pickle' % (file_name_ya)
    to_pickle = {}
    if not os.path.exists(pickle_file):
        print('Pickling: %s' % (pickle_file))
        try:
            labels, class_names, accuracy, cm = aS.hmm_segmentation(file_name_wav, sys.argv[1], True, "")
            for k in range(0, labels.ndim):
                print(labels.shape[k])
            to_pickle = {'labels': labels, 'class_names': class_names, 'accuracy': accuracy, 'cm': cm}
            pickle.dump(to_pickle, open(pickle_file, "wb"))
        except Exception as e:
            print(e)
    else:
        to_pickle = pickle.load(open(pickle_file, "rb"))
    file_info = {'file_name': '%s.mp3' % (file_name_ya), 'length': audio_length, 'segments': {'music': [], 'speech': []}}
    factor = float(audio_length) / len(to_pickle['labels'])
    previous_label = to_pickle['labels'][0]
    previous_idx = 0
    idx = 0
    for label in to_pickle['labels']:
        if label != previous_label:
            k = 'speech' if label == 0 else 'music'
            file_info['segments'][k].append([ float(previous_idx) * factor, float(1 + idx) * factor ])
            previous_label = label
            previous_idx = idx + 1
        idx += 1
    k = 'speech' if label == 0 else 'music'
    file_info['segments'][k].append([ float(previous_idx) * factor, float(idx) * factor ])
        
    json_output = 'json/%s.json' % (file_name_ya)  
    with open(json_output, 'w') as outfile:
       print('Writing to %s' % (json_output))
       json.dump(file_info, outfile, indent=4, sort_keys=True)
    