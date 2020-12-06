from .core import FUNCTION_REGISTER, Operator
class DownFrameRate(Operator):
    def __init__(self, rate, interval, test):
        super(DownFrameRate, self).__init__()
        self.rate = rate
        self.interval = interval
        self.test = test

    def operate(self, input, output):
        print('hello')


FUNCTION_REGISTER('frameRateStage', 'ffmpeg', DownFrameRate,False)
print('fr')