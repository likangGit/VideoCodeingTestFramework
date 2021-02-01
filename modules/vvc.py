import os
import re
import shutil
import subprocess
from collections import deque
from .core import FUNCTION_REGISTER, Operator
class VVC(Operator):
    """reference：https://www.cnblogs.com/blackhumour2018/p/9427665.html
    """
    def __init__(self, crf,mode,frames,level=3.1, bppRef='input'):
        super(VVC, self).__init__()
        self.crf = crf
        self.mode = mode
        self.frames = frames
        self.level = level
        self.bppRef = bppRef
        self.cfg = {'lowdelay_P':'encoder_lowdelay_P_vtm.cfg'}

    def operate(self, input, output):
        print('VVC start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        w, h, fps = self.extractParameters(input)
        vvc_path = os.path.dirname(__file__)
        bitstream = os.path.join(output,'str.bin')
        recon = os.path.join(output,'rec.yuv')
        cmd = '{}/thirdparty/VVC/EncoderApp'.format(vvc_path)
        cmd += ' -c {}/thirdparty/VVC/{}'.format(vvc_path, self.cfg[self.mode])
        cmd += ' -i {} -fr {} -wdt {} -hgt {} -f {} -b {} -o {} -q {} --Level={} --OutputBitDepth=8'.format(
            input, fps, w, h, self.frames, bitstream, recon, self.crf, self.level)

        # print(cmd)
        
        p = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        inf_flag = False
        inform = ''
        while p.poll() is None:
            line = p.stdout.readline().rstrip()
            end = '\r' if ('POC' in line) else '\n'
            print(line, end=end)
            if inf_flag:
                inform = line
                inf_flag = False
            if 'Total Frames' in line:
                inf_flag = True

        inform = [i for i in inform.split(' ')[1:] if i != '']

        # calculate BPP and write it in file name
       
        frames, kbps = int(inform[0]), float(inform[2])
        if self.bppRef == 'predecessor':
            bpp = self.calculateBPP(bitstream, w, h, frames)
        else:
            folders = input.split('/')
            wh_obj = re.match(r'.*?_?(\d+)\D{1}(\d+)_.*',folders[1])
            
            w_input, h_input = float(wh_obj.group(1) ), float(wh_obj.group(2) )
            # print(w_input, h_input)
            # frames = os.path.getsize(os.path.join(*folders[:2], folders[1]) )/(w_input*h_input*3/2)
            bpp = self.calculateBPP(bitstream, w_input, h_input, frames)
        newFileName = self.generateFileName(w,h,fps,bpp=round(bpp, 4), avgQP=self.crf, kbps=kbps)
        output = os.path.join(output,newFileName)
        os.rename(recon, output)
        os.remove(bitstream)
        print('VVC finish:{}'.format(output))
   
        return output
    
    def calculateBPP(self, filename, w, h, frames):
        sizeByte = os.path.getsize(filename)
        bpp = sizeByte * 8 /(w * h * frames)
        return bpp


FUNCTION_REGISTER('encodingStage', 'VVC', VVC,True)