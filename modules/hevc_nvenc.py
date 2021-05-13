import os
import re
import shutil
import subprocess
from collections import deque
from .core import FUNCTION_REGISTER, Operator
class HEVC_NVENC(Operator):
    """reference：https://www.cnblogs.com/blackhumour2018/p/9427665.html
    """
    def __init__(self, cq=None,keyint_min=None,
                g=None,vframes=None, bppRef='input'):
        super(HEVC_NVENC, self).__init__()
        self.cq = cq
        self.keyint = keyint_min
        self.g = g
        self.vframes = vframes
        self.bppRef = bppRef

    def operate(self, input, output):
        print('HEVC NVENC start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        w, h, fps = self.extractParameters(input)
        tmp_output = os.path.join(output, 'tmp.mkv')
        #ffmpeg -framerate 50.0 -s 960x540 -i 960x540_50.0fps.yuv -r 50.0 -vcodec libx265 -x265-params "keyint=10:min-keyint=5:crf=20:no-scenecut=1" -f hevc out.h265
        # cmd = 'ffmpeg -s {}x{} -framerate {} -i {} -r {} -vcodec libx265 \
        #     -x265-params keyint={}:min-keyint={}:crf={}:no-scenecut=1 -f hevc {} -y -hide_banner'.format(
        #     w, h, fps, input,fps, self.keyInterval, self.keyInterval, self.Q , tmp_output)
        cmd = 'ffmpeg -s {}x{} -framerate {} -i {} -r {} -c:v hevc_nvenc'.format(w,h, fps, input,fps)
        cmd += ' -g {}'.format(self.g) if self.g else ''
        cmd += ' -vframes {}'.format(self.vframes) if self.vframes else ''
        cmd += ' -cq {}'.format(self.cq) if self.cq else ''
        cmd += ' -keyint_min {}'.format(self.keyint) if self.keyint else ''
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
            origin_file = os.path.join(*folders[:2], folders[1]) 
            
            frames = self.vframes if self.vframes else os.path.getsize(origin_file )/(w_origin*h_origin*3/2)
            bpp = self.calculateBPP(tmp_output, w_origin, h_origin, frames)

        newFileName = self.generateFileName(w,h,fps,bpp=round(bpp, 4), avgQP=self.cq, kbps=kbps)
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


FUNCTION_REGISTER('encodingStage', 'HEVC_NVENC', HEVC_NVENC,True, 2)