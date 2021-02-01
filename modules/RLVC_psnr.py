import os
import numpy as np
import re
from modules.core import FUNCTION_REGISTER, Operator


class RLVC_dec(Operator):
    def __init__(self, lumda):
        super(RLVC_dec, self).__init__()
        self.lumda = lumda

    def operate(self, input, output):
        print('RLVC Decoding Process start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        sr_w, sr_h, fps = self.extractParameters(input)
        w = int(sr_w)
        h = int(sr_h)
        fps = int(fps)
        if (w % 16 != 0) or (h % 16 != 0):
            raise ValueError('Height and Width must be a mutiple of 16.')

        # Recording w,h,frames of input
        folders = input.split('/')
        wh_obj = re.match(r'.*?_?(\d+)\D{1}(\d+)_.*', folders[1])
        w_input, h_input = float(wh_obj.group(1)), float(wh_obj.group(2))
        frames_input = os.path.getsize(os.path.join(*folders[:2], folders[1])) / (w_input * h_input * 3 / 2)
        w_input = int(w_input)
        h_input = int(h_input)
        frames_input = int(frames_input)
        # print(w_input, h_input, frames_input)

        # yuv to PNGs
        out_ab = os.getcwd() + '/' + output
        out_fpath = '/'.join(out_ab.split('/')[:-1])
        # png_path=out_ab+'/Pngs_from_{}x{}_{}fps'.format(w,h,fps)
        png_path = out_fpath + '/Pngs_from_{}x{}_{}fps'.format(w, h, fps)
        if not os.path.exists(png_path):
            os.makedirs(png_path)
        frame_ex = 0
        for dirpath, dirnames, filenames in os.walk(png_path):
            for file in filenames:
                frame_ex = frame_ex + 1
                if frame_ex != 0:
                    print('PNGs existed already! Continue RLVC decoding......')
                    break
        if frame_ex == 0:
            input_path = '/'.join(input.split('/')[:-1])
            input_name = input.split('/')[-1]

            cmd1 = 'ffmpeg -s {}x{} -i {} Pngs_from_{}x{}_{}fps/f%03d.png'.format(w, h, input_name, w, h, fps)
            os.system('cd {};{}'.format(input_path, cmd1))
        lumda = self.lumda
        print('--------------Working on RLVC Decoding, lumda={}------------------'.format(lumda))
        # HLVC decoding Frame Count
        frame_count = 0
        for dirpath, dirnames, filenames in os.walk(png_path):
            for file in filenames:
                frame_count = frame_count + 1
        # assert (frame_count % 10 == 1)

        # RLVC decoding
        #"--f_P" denotes the number of P frames to be encoded in the forward direction,
        # and"--b_P" denotes the number of P frames to be encoded in the backward direction
        # python RLVC.py --path BasketballPass --f_P 6 --b_P 6 --mode PSNR  --metric PSNR --l 1024
        Rlvc_pypath = 'modules/thirdparty/RLVC'
        cmd = 'python RLVC.py --path {} --output {} --frame {} --l {} --w {} --h {} --f_input {}'.format(
            png_path, out_ab, frame_count, lumda,w_input,h_input,frames_input)
        os.system('cd {};{}'.format(Rlvc_pypath, cmd))

        # PSNR&bpp read,Clear
        recordtxt1 = os.getcwd() + '/modules/thirdparty/RLVC/psnr.txt'
        f1 = open(recordtxt1, 'r', encoding='utf-8')
        msg1 = f1.readline()
        if msg1 == '':
            raise ValueError('PSNR value not found in txt. Check RLVC decoding process!')
        f1.close()
        # Clear message in txt
        f1 = open(recordtxt1, 'w', encoding='utf-8')
        f1.close()

        recordtxt2 = os.getcwd() + '/modules/thirdparty/RLVC/bpp.txt'
        f2 = open(recordtxt2, 'r', encoding='utf-8')
        msg2 = f2.readline()
        if msg2 == '':
            raise ValueError('Bpp value not found in txt. Check RLVC decoding process!')
        f2.close()
        # Clear message in txt
        f2 = open(recordtxt2, 'w', encoding='utf-8')
        f2.close()

        # psnr1=np.around(float(psnr1),decimals=5)
        bpp2 = np.around(float(msg2), decimals=5)
        newFileName = self.generateFileName(w, h, fps, bpp=bpp2, avgQP=None, kbps=None)

        # PNGs to YUV
        if not os.path.exists(out_ab):
            raise FileExistsError('Output path "{}" cannot find, check RLVC decoding!'.format(out_ab))
        print('Changing PNGs to YUV......')
        Newlocation=os.path.join(out_ab,newFileName)
        cmd2 = 'ffmpeg -i f%03d.png -s {}x{} -pix_fmt yuv420p {}'.format(w, h, Newlocation)
        out_frames=out_ab+'/frames/'
        os.system('cd {};{}'.format(out_frames, cmd2))
        print('RLVC decoding finish: {}'.format(Newlocation))
        print('--------------RLVC Decoding: lumda={} Completed!------------------'.format(lumda))
        output = os.path.join(output,newFileName)
        return output
        # return newFileName


FUNCTION_REGISTER('encodingStage', 'RLVC', RLVC_dec, False)
