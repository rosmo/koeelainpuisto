from pyAudioAnalysis import audioSegmentation as aS
import sys
import time
import numpy

#for window_length in numpy.arange(1.0, 3.0, 0.5):
#    for window_step in numpy.arange(0.5, 3.0, 0.5):
for window_length in [1.5]:
    for window_step in [2.0]:
        start = time.time()
        print('Training window_length=%f window_step=%f' % (window_length, window_step))
        aS.train_hmm_from_directory('training/', '%s-win%f-step%f' % (sys.argv[1], window_length, window_step), window_length, window_step)
        end = time.time()
        print(end - start)
