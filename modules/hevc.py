import os
import re
import shutil
import subprocess
from collections import deque
from .core import FUNCTION_REGISTER, Operator
class HEVC(Operator):
    """reference：https://www.cnblogs.com/blackhumour2018/p/9427665.html
    """
    def __init__(self, crf=None,codec=None,keyint=None,preset=None, tune=None,
                g=None,level=None,vframes=None, bppRef='input'):
        super(HEVC, self).__init__()
        self.crf = crf
        self.codec = codec
        self.keyint = keyint
        self.preset = preset
        self.tune = tune
        self.g = g
        self.level = level
        self.vframes = vframes
        self.bppRef = bppRef

    def operate(self, input, output):
        print('HEVC start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        w, h, fps = self.extractParameters(input)
        tmp_output = os.path.join(output, 'tmp.mkv')
        #ffmpeg -framerate 50.0 -s 960x540 -i 960x540_50.0fps.yuv -r 50.0 -vcodec libx265 -x265-params "keyint=10:min-keyint=5:crf=20:no-scenecut=1" -f hevc out.h265
        # cmd = 'ffmpeg -s {}x{} -framerate {} -i {} -r {} -vcodec libx265 \
        #     -x265-params keyint={}:min-keyint={}:crf={}:no-scenecut=1 -f hevc {} -y -hide_banner'.format(
        #     w, h, fps, input,fps, self.keyInterval, self.keyInterval, self.Q , tmp_output)
        cmd = 'ffmpeg -s {}x{} -framerate {} -i {} -r {}'.format(w,h, fps, input,fps)
        cmd += ' -c:v {}'.format(self.codec) if self.codec else '' 
        cmd += ' -preset {}'.format(self.preset) if self.preset else ''
        cmd += ' -tune {}'.format(self.tune) if self.tune else ''
        cmd += ' -g {}'.format(self.g) if self.g else ''
        cmd += ' -level {}'.format(self.level) if self.level else ''
        cmd += ' -vframes {}'.format(self.vframes) if self.vframes else ''
        if 'hevc' == self.codec or 'libx265' == self.codec:
            if self.crf or self.keyint:
                cmd += ' -x265-params'
                if self.crf and self.keyint:
                    cmd += ' crf={}:keyint={}'.format(self.crf, self.keyint)
                elif self.crf:
                    cmd += ' crf={}'.format(self.crf)
                else:
                    cmd += ' keyint={}'.format(self.keyint)
        elif 'hevc_nvenc' == self.codec:
            cmd += ' -cq {}'.format(self.crf) if self.crf else ''
            cmd += ' -keyint_min {}'.format(self.keyint) if self.keyint else ''
        else:
            raise Exception('undefined codec')
            
        cmd += ' {} -y -hide_banner'.format(tmp_output)

        # print(cmd)
        
        p = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        line_queue = deque(maxlen=2)
        while p.poll() is None:
            line = p.stdout.readline().rstrip()
            line_queue.append(line)
            end = '\r' if (('frame=' in line) and ('fps=' in line) and ('time=' in line)) else '\n'
            print(line, end=end)
        inform = line_queue.popleft()
        # if 'libx265' == self.codec:
        #     assert ('encoded' in inform) and ('frames in' in inform) and \
        #             ('kb/s' in inform) and ('Avg QP' in inform), 'HEVC does not execuate correct'
        #     # transform h265 to yuv, calculate BPP and write it in file name
        #     obj = re.match(r'encoded (\d+) frames .*\), (.+) kb/s, Avg QP:(.+)', inform)
        #     if obj:
        #         frames, kbps, QP = int(obj.group(1) ), obj.group(2), float(obj.group(3))
        #     else:
        #         raise Exception('HEVC execuate faild:{}'.format(output))
        # else:
        #     kbps = 
        frames = os.path.getsize(input) / (w*h*3/2)
        kbps = os.path.getsize(tmp_output) * 8 / frames * fps / 1024.0
        kbps = round(kbps, 4)
        if self.bppRef == 'predecessor':
            bpp = self.calculateBPP(tmp_output, w, h, frames)
        else:
            folders = input.split('/')
            wh_obj = re.match(r'.*?_?(\d+)\D{1}(\d+)_.*',folders[1])
            w_origin, h_origin = float(wh_obj.group(1) ), float(wh_obj.group(2) )
            # print(w_input, h_input)
            frames_origin = os.path.getsize(os.path.join(*folders[:2], folders[1]) )/(w_origin*h_origin*3/2)
            bpp = self.calculateBPP(tmp_output, w_origin, h_origin, frames_origin)

        newFileName = self.generateFileName(w,h,fps,bpp=round(bpp, 4), avgQP=self.crf, kbps=kbps)
        output = os.path.join(output,newFileName)
        cmd = 'ffmpeg -i {} {} -hide_banner'.format(tmp_output, output)
        os.system(cmd)
        # os.remove(tmp_output)
        print('HEVC finish:{}'.format(output))
        return output
    
    def calculateBPP(self, filename, w, h, frames):
        sizeByte = os.path.getsize(filename)
        bpp = sizeByte * 8 /(w * h * frames)
        return bpp


FUNCTION_REGISTER('encodingStage', 'HEVC', HEVC,True, 2)