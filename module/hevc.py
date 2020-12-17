import os
import re
import shutil
import subprocess
from collections import deque
from .core import FUNCTION_REGISTER, Operator
class HEVC(Operator):
    """reference：https://www.cnblogs.com/blackhumour2018/p/9427665.html
    """
    def __init__(self, Q, keyInterval):
        super(HEVC, self).__init__()
        self.Q = int(Q)
        self.keyInterval = int(keyInterval)

    def operate(self, input, output):
        print('HEVC start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        w, h, fps = self.extractParameters(input)
        newFileName = self.generateFileName(w,h,fps,'mp4')
        output = os.path.join(output,newFileName)
        #ffmpeg -framerate 50.0 -s 960x540 -i 960x540_50.0fps.yuv -r 50.0 -vcodec libx265 -x265-params "keyint=10:min-keyint=5:crf=20:no-scenecut=1" -f hevc out.h265
        cmd = 'ffmpeg -s {}x{} -framerate {} -i {} -r {} -vcodec libx265 \
            -x265-params keyint={}:min-keyint={}:crf={}:no-scenecut=1 {} -y'.format(
            w, h, fps, input,fps, self.keyInterval, self.keyInterval, self.Q , output)
        
        p = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        line_queue = deque(maxlen=2)
        while p.poll() is None:
            line = p.stdout.readline().rstrip()
            line_queue.append(line)
            end = '\r' if (('frame=' in line) and ('fps=' in line) and ('time=' in line)) else '\n'
            print(line, end=end)
        inform = line_queue.popleft()
        assert ('encoded' in inform) and ('frames in' in inform) and \
                ('kb/s' in inform) and ('Avg QP' in inform), 'HEVC does not execuate correct'
        # write information in file name
        obj = re.match(r'encoded .*\), (.+) kb/s, Avg QP:(.+)', inform)
        if obj:
            previous_name = output
            bitrate, QP = obj.group(1), obj.group(2)
            extended = '_{}kbs_{}AvgQP'.format(bitrate, QP)
            name, ext = os.path.splitext(output)
            name += (extended + ext)
            output = name
            os.rename(previous_name,output)

        print('HEVC finish:{}'.format(output))
        return output

FUNCTION_REGISTER('encodingStage', 'HEVC', HEVC,True)