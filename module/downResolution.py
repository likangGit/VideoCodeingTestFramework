import os
import shutil
from .core import FUNCTION_REGISTER, Operator
class FFmpeg(Operator):
    def __init__(self, downRate):
        super(FFmpeg, self).__init__()
        self.downRate = downRate

    def operate(self, input, output):
        print('FFmpeg start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        sr_w, sr_h, fps = self.extractParameters(input)
        w = int(sr_w * self.downRate)
        h = int(sr_h * self.downRate)
        newFileName = self.generateFileName(w,h,fps)
        output = os.path.join(output, newFileName)
        if abs(self.downRate - 1) < 1e-5:
            shutil.copy(input, output)
        else:
            cmd = 'ffmpeg -s {}x{} -i {} -vf scale={}:-1 {} -y -hide_banner'.format(
                sr_w, sr_h, input, w, output)
            os.system(cmd)
        print('FFmpeg finish:{}'.format(output))
        return output

FUNCTION_REGISTER('downResolutionStage', 'FFmpeg', FFmpeg,True)