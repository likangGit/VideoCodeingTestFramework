from .core import FUNCTION_REGISTER, Operator
class DownResolution(Operator):
    def __init__(self, rate):
        super(DownResolution, self).__init__()
        self.rate = rate

    def operate(self, input, output):
        print('DownResolution')
        return output

FUNCTION_REGISTER('resolutionStage', 'ffmpeg', DownResolution,True)