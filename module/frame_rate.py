import os
from .core import FUNCTION_REGISTER, Operator

class DownFrameRate(Operator):
    def __init__(self, rate, interval):
        super(DownFrameRate, self).__init__()
        self.rate = rate
        self.interval = interval

    def operate(self, input, output):
        output = os.path.join(output,'0.yuv')
        print('hello')
        return output

FUNCTION_REGISTER('frameRateStage', 'ffmpeg', DownFrameRate,True)