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
        tmp_output = os.path.join(output, 'tmp.h265')
        #ffmpeg -framerate 50.0 -s 960x540 -i 960x540_50.0fps.yuv -r 50.0 -vcodec libx265 -x265-params "keyint=10:min-keyint=5:crf=20:no-scenecut=1" -f hevc out.h265
        cmd = 'ffmpeg -s {}x{} -framerate {} -i {} -r {} -vcodec libx265 \
            -x265-params keyint={}:min-keyint={}:crf={}:no-scenecut=1 -f hevc {} -y -hide_banner'.format(
            w, h, fps, input,fps, self.keyInterval, self.keyInterval, self.Q , tmp_output)
        
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
        # transform h265 to yuv, calculate BPP and write it in file name
        obj = re.match(r'encoded (\d+) frames .*\), (.+) kb/s, Avg QP:(.+)', inform)
        if obj:
            frames, kbps, QP = int(obj.group(1) ), obj.group(2), float(obj.group(3))
            bpp = self.calculateBPP(tmp_output, w, h, frames)
            newFileName = self.generateFileName(w,h,fps,bpp=round(bpp, 4), avgQP=QP, kbps=kbps)
            output = os.path.join(output,newFileName)
            cmd = 'ffmpeg -framerate {} -i {} {} -hide_banner'.format(fps, tmp_output, output)
            os.system(cmd)
            os.remove(tmp_output)
            print('HEVC finish:{}'.format(output))
        else:
            raise Exception('HEVC execuate faild:{}'.format(output))
        return output
    
    def calculateBPP(self, filename, w, h, frames):
        sizeByte = os.path.getsize(filename)
        bpp = sizeByte * 8 /(w * h * frames)
        return bpp


FUNCTION_REGISTER('encodingStage', 'HEVC', HEVC,True)