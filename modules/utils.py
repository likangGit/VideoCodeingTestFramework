import os
import re
import cv2
from glob import glob
import numpy as np
def getReferenceFile(input):
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
