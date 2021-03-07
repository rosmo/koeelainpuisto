#!/usr/bin/env python3
from pyAudioAnalysis import audioSegmentation as aS
import sys
import os 

def evaluate_file(model_name, file_name):
    gt_file = None 
    if os.path.exists('evaluate/%s.segments' % (file_name)):
        gt_file = 'evaluate/%s.segments' % (file_name)
        print('Using ground truth: %s' % (gt_file))
        audio_file = 'evaluate/%s.wav' % (file_name)
    elif os.path.exists('training/%s.segments' % (file_name)):
        gt_file = 'training/%s.segments' % (file_name)
        print('Using ground truth: %s' % (gt_file))
        audio_file = 'training/%s.wav' % (file_name)
    else:
        audio_file = 'training/%s.wav' % (file_name)
    print('Segmenting: %s' % (audio_file))
    labels, class_names, accuracy, cm = aS.hmm_segmentation(audio_file, model_name, True, gt_file)
    print(labels, 'SHAPE', labels.shape, 'NDIM', labels.ndim)
    #for k in labels:
    #    print('k=' % k, labels[k:])
    print(class_names, type(class_names))
    print(accuracy)
    print(cm)

test_files = ['kep23082015', 'kep03082013', 'kep10032012', 'kep22032014']
for test_file in test_files:
    evaluate_file(sys.argv[1], test_file)