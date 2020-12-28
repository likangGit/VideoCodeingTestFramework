import os
import re
import cv2
import shutil
from glob import glob
import numpy as np
from .core import FUNCTION_REGISTER, Operator
class VideoCaptureYUV:
    def __init__(self, filename, size):
        self.height, self.width = size
        self.frame_len = self.width * self.height * 3 // 2
        self.f = open(filename, 'rb')
        self.shape = (int(self.height*1.5), self.width)
    def __del__(self):
        self.f.close()

    def read_raw(self):
        try:
            raw = self.f.read(self.frame_len)
            if raw == b'':
                return False, None
            yuv = np.frombuffer(raw, dtype=np.uint8)
            yuv = yuv.reshape(self.shape)
        except Exception as e:
            print(str(e))
            return False, None
        return True, yuv

    def read(self):
        ret, yuv = self.read_raw()
        if not ret:
            return ret, yuv
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420, 3)
        return ret, bgr

class PSNR(Operator):
    def __init__(self, useDataType):
        super(PSNR, self).__init__()
        self.useDataType = useDataType

    def operate(self, input, output):
        print('PSNR start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        sr_w, sr_h, fps = self.extractParameters(input)
        ref_file = self.getReferenceFile(input)
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
        print('ref:{}'.format(reference))
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
            if retSrc != retRef:
                raise Exception('two file has different frames')
            # if retRef and (not retSrc)
            #     raise Exception('input frames should be more than retRef')
            if not retRef:
                break
            psnr_list.append(cv2.PSNR(imgSrc, imgRef) )
        return np.mean(psnr_list)

    def getReferenceFile(self,input):
        input_stage = os.path.basename(os.path.dirname(input) )
        if 'encodingStage' in input_stage:
            reference_stage = 'encodingStage'
        if 'upResolutionStage' in input_stage:
            reference_stage =  'downResolutionStage'
        if 'upFrameRateStage' in input_stage:
            reference_stage = 'downFrameRateStage'
        obj = re.match(r'(.*)/{}.*'.format(reference_stage), input)
        if obj:
            ref_path = obj.group(1)
        else:
            raise Exception('PSNR execuate faild:input:{}'.format(input))
    
        ref_file = glob(os.path.join(ref_path, '*.yuv'))[0]
        return ref_file

FUNCTION_REGISTER('analyzerStage', 'PSNR', PSNR,True)