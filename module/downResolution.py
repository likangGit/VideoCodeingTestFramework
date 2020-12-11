import os
import shutil
from .core import FUNCTION_REGISTER, Operator
class FFmpeg(Operator):
    def __init__(self, downRate, h, w):
        super(FFmpeg, self).__init__()
        self.downRate = downRate
        self.h = h
        self.w = w

    def operate(self, input, output):
        print('FFmpeg start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        output = os.path.join(output,'0.yuv')
        if abs(self.downRate - 1) < 1e-5:
            shutil.copy(input, output)
        else:
            cmd = 'ffmpeg -s {}x{} -i {} -vf scale={}:-1 {} '.format(
                self.w, self.h, input, int(self.w * self.downRate), output)
            os.system(cmd)
        print('FFmpeg finish:{}'.format(output))
        return output

FUNCTION_REGISTER('downResolutionStage', 'FFmpeg', FFmpeg,True)