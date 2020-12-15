import os
import shutil
from .core import FUNCTION_REGISTER, Operator

class BinaryFileProcess(Operator):
    def __init__(self, downRate):
        super(BinaryFileProcess, self).__init__()
        self.interval = 1//downRate

    def operate(self, input, output):
        print('BinaryFileProcess start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        w, h, fps = self.extractParameters(input)
        fps = fps / self.interval
        newFileName = self.generateFileName(w,h,fps)
        output = os.path.join(output, newFileName)

        bytePreFrame = h*w * 3 // 2
        if abs(self.interval - 1) < 1e-5:
            shutil.copyfile(input, output)
        else:
            count = 0
            writer = open(output, 'wb')
            with open(input, 'rb') as f:
                while True:
                    frame = f.read(bytePreFrame)
                    if frame == b'':
                        break
                    if count % self.interval == 0:
                        writer.write(frame)
                        # print("write frame id:{}".format(count))
                    count += 1
            writer.close()
            print("total frame:",count)
        print('BinaryFileProcess finish: {}'.format(output))
        return output

FUNCTION_REGISTER('downFrameRateStage', 'BinaryFileProcess', BinaryFileProcess)