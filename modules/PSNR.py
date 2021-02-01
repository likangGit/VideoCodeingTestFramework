import os
import re
import cv2
import shutil
from glob import glob
import numpy as np
from .core import FUNCTION_REGISTER, Operator
from .utils import VideoCaptureYUV, getReferenceFile

class PSNR(Operator):
    def __init__(self, useDataType):
        super(PSNR, self).__init__()
        self.useDataType = useDataType

    def operate(self, input, output):
        print('PSNR start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        sr_w, sr_h, fps = self.extractParameters(input)
        ref_file = getReferenceFile(input)
        # calculate PSNR
        psnr = self.calculatePSNR(input, ref_file, (sr_h, sr_w))
        # create a soft link between input and output
        newFileName = self.generateFileName(sr_w, sr_h, fps, PSNR=round(psnr,4) )
        output = os.path.join(output, newFileName)
        os.symlink(os.path.abspath(input), output)

        print('PSNR finish:{}'.format(output))
        return output

    def calculatePSNR(self, input, reference, size):
        inputYUVs = VideoCaptureYUV(input, size)
        referenceYUVs = VideoCaptureYUV(reference, size)
        psnr_list = []
        count = 0
        while True:
            print('\rprocessing frame:{}'.format(count),end='')
            count += 1
            if self.useDataType == 'YUV':
                retSrc, imgSrc = inputYUVs.read_raw()
                retRef, imgRef = referenceYUVs.read_raw() 
            else:
                retSrc, imgSrc = inputYUVs.read()
                retRef, imgRef = referenceYUVs.read()
            # if retSrc != retRef:
            #     raise Exception('two file has different frames')
            if retSrc and (not retRef):
                raise Exception('reference frames should be more than input')
            if not retSrc:
                break
            psnr_list.append(cv2.PSNR(imgSrc, imgRef) )
        return np.mean(psnr_list)


FUNCTION_REGISTER('analyzerStage', 'PSNR', PSNR,True)