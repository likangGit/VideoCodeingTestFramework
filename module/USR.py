import os
import re
import shutil
import subprocess

from .core import FUNCTION_REGISTER, Operator
class USR(Operator):
    """
    """
    def __init__(self):
        super(USR, self).__init__()

    def operate(self, input, output):
        print('USR start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        w, h, fps = self.extractParameters(input)
        
        # convert yuv to png
        tmp_folder = os.path.join(output, 'tmp')
        if not os.path.exists(tmp_folder):
            os.mkdir(tmp_folder)
        cmd = 'ffmpeg -framerate {} -s {}x{} -i {} -f image2 {}/%d.png -hide_banner'.format(
            fps, w, h, input, tmp_folder)
        os.system(cmd)
        # use USR to super resolutioin
        obj = re.match(r'.*/downResolutionStage_FFmpeg_downRate_(.+)/enc.*', input)
        if obj:
            para = obj.group(1)
            up_rate = 1/float(para)
        else:
            raise Exception('USR intput valid:{}'.format(input))

        cmd = 'cd {}/3rdparty/VideoPhotoRepair;python main.py {} --operation usr --scale {} --clc'.format(
            os.path.dirname(__file__), os.path.abspath(tmp_folder), int(up_rate) )
      
        os.system(cmd)
        # convert png to yuv
        newFileName = self.generateFileName(int(w*up_rate), int(h*up_rate), fps)
        output = os.path.join(output, newFileName)
        cmd = 'ffmpeg -i {}/3rdparty/VideoPhotoRepair/results/usr/%d.png -pix_fmt yuv420p {} -hide_banner'.format(
            os.path.dirname(__file__), output)
        os.system(cmd)       
        shutil.rmtree(tmp_folder)
        return output


FUNCTION_REGISTER('upResolutionStage', 'USR', USR,False)