
import os
import re
import cv2
import shutil
from glob import glob
import numpy as np
from .core import FUNCTION_REGISTER, Operator
from .utils import VideoCaptureYUV, getReferenceFile
from .thirdparty.niqe.niqe import niqe

class NIQE(Operator):
    def __init__(self):
        super(NIQE, self).__init__()

    def operate(self, input, output):
        print('NIQE start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        sr_w, sr_h, fps = self.extractParameters(input)
        # calculate NIQE
        niqe = self.calculateNIQE(input, (sr_h, sr_w))
        # create a soft link between input and output
        newFileName = self.generateFileName(sr_w, sr_h, fps, NIQE=round(niqe,4) )
        output = os.path.join(output, newFileName)
        os.symlink(os.path.abspath(input), output)

        print('NIQE finish:{}'.format(output))
        return output

    def calculateNIQE(self, input, size):
        inputYUVs = VideoCaptureYUV(input, size)
        niqe_list = []
        count = 0
        while True:
            print('\rprocessing frame:{}'.format(count),end='')
            count += 1
            retSrc, imgSrc = inputYUVs.read()
            if not retSrc:
                break
            gray = cv2.cvtColor(imgSrc, cv2.COLOR_BGR2GRAY)
            niqe_list.append(niqe(gray) )
        return np.mean(niqe_list)


FUNCTION_REGISTER('analyzerStage', 'NIQE', NIQE,True)