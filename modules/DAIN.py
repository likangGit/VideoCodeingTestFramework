import os
import re
import shutil
import subprocess

from .core import FUNCTION_REGISTER, Operator
class DAIN(Operator):
    """
    """
    def __init__(self):
        super(DAIN, self).__init__()

    def operate(self, input, output):
        print('DAIN start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        obj = re.match(r'.*/downFrameRateStage_BinaryFileProcess_downRate_(.+)/down.*', input)
        if obj:
            para = obj.group(1)
            up_rate = 1/float(para)
        else:
            raise Exception('DAIN intput valid:{}'.format(input))

        w, h, fps = self.extractParameters(input)

        if abs(up_rate - 1) < 1e-5:
            newFileName = self.generateFileName(w, h, fps*up_rate)
            output = os.path.join(output, newFileName)
            os.symlink(os.path.abspath(input), output)
        else:
            # convert yuv to png
            tmp_folder = os.path.join(output, 'tmp')
            if not os.path.exists(tmp_folder):
                os.mkdir(tmp_folder)
            cmd = 'ffmpeg -framerate {} -s {}x{} -i {} -f image2 {}/%d.png -hide_banner'.format(
                fps, w, h, input, tmp_folder)
            os.system(cmd)

            # use DAIN to super resolutioin
            cmd = 'cd {}/thirdparty/VideoPhotoRepair;python main.py {} --operation dain --multi {} --fps {} --clc'.format(
                os.path.dirname(__file__), os.path.abspath(tmp_folder), int(up_rate), int(fps) )
            os.system(cmd)

            # calculate source file frames
            folders = input.split('/')
            wh_obj = re.match(r'.*?_?(\d+)\D{1}(\d+)_.*',folders[1])
            w_input, h_input = float(wh_obj.group(1) ), float(wh_obj.group(2) )
            frames = os.path.getsize(os.path.join(*folders[:2], folders[1]) )/(w_input*h_input*3/2)
            png_path = os.path.join(os.path.dirname(__file__), 'thirdparty/VideoPhotoRepair/results/dain')
            current_frames = len(os.listdir( png_path) )
            for i in range(current_frames, int(frames), -1):
                os.remove(os.path.join(png_path, '{}.png'.format(i) ))

            # convert png to yuv
            newFileName = self.generateFileName(w, h, fps*up_rate)
            output = os.path.join(output, newFileName)
            cmd = 'ffmpeg -i {}/thirdparty/VideoPhotoRepair/results/dain/%d.png -pix_fmt yuv420p {} -hide_banner'.format(
                os.path.dirname(__file__), output)
            os.system(cmd)       
            shutil.rmtree(tmp_folder)
        return output


FUNCTION_REGISTER('upFrameRateStage', 'DAIN', DAIN,False)