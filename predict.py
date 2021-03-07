from pyAudioAnalysis import audioSegmentation as aS
import sys

labels, class_names, accuracy, cm = aS.hmm_segmentation(sys.argv[1], sys.argv[2], True, sys.argv[3] if len(sys.argv) == 4 else None)
print(labels)
print(class_names)
print(accuracy)
print(cm)