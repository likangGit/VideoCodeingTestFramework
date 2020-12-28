import os
import numpy as np
from module.core import FUNCTION_REGISTER, Operator


class hlvc_dec(Operator):
    def __init__(self, lumda):
        super(hlvc_dec, self).__init__()
        self.lumda = lumda

    def operate(self, input, output):
        print('HLVC Decoding Process start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        sr_w, sr_h, fps = self.extractParameters(input)
        w = int(sr_w)
        h = int(sr_h)
        fps = int(fps)
        if (w % 16 != 0) or (h % 16 != 0):
            raise ValueError('Height and Width must be a mutiple of 16.')

        #yuv to PNGs
        out_ab=os.getcwd()+'/'+output
        out_fpath='/'.join(out_ab.split('/')[:-1])
        #png_path=out_ab+'/Pngs_from_{}x{}_{}fps'.format(w,h,fps)
        png_path=out_fpath+'/Pngs_from_{}x{}_{}fps'.format(w,h,fps)
        if not os.path.exists(png_path):
            os.makedirs(png_path)
        frame_ex=0
        for dirpath, dirnames, filenames in os.walk(png_path):
            for file in filenames:
                frame_ex =  frame_ex + 1
                if frame_ex != 0:
                    print('PNGs existed already! Continue hlvc decoding......')
                    break
        if frame_ex==0:
            input_path='/'.join(input.split('/')[:-1])
            input_name=input.split('/')[-1]

            cmd1 = 'ffmpeg -s {}x{} -i {} Pngs_from_{}x{}_{}fps/f%03d.png'.format(w, h, input_name,w,h,fps )
            os.system('cd {};{}'.format(input_path,cmd1))
        lumda=self.lumda
        print('--------------Working on HLVC Decoding, lumda={}------------------'.format(lumda))
        # HLVC decoding Frame Count
        frame_count = 0
        for dirpath, dirnames, filenames in os.walk(png_path):
            for file in filenames:
                frame_count = frame_count + 1
        assert (frame_count % 10 == 1)

        # HLVC decoding
        hlvc_pypath = 'module/3rdparty/HLVC'
        cmd = 'python HLVC_video_fast.py --path {} --output {} --frame {} --mode PSNR --l {} '.format(png_path,out_ab,frame_count,lumda)
        os.system('cd {};{}'.format(hlvc_pypath,cmd))

        #PSNR&bpp read,Clear
        recordtxt=os.getcwd()+'/module/3rdparty/HLVC/psnr_bpp.txt'
        f=open(recordtxt,'r', encoding='utf-8')
        msg=f.readline()
        if msg=='':
            raise ValueError('PSNR and bpp value not found in txt. Check HLVC decoding process!')
        f.close()
        #Clear message in txt
        f=open(recordtxt,'w', encoding='utf-8')
        f.close()

        psnr1,bpp1=msg.split('_')
        psnr1=np.around(float(psnr1),decimals=4)
        bpp1=np.around(float(bpp1),decimals=4)

        #Function: generateFileName(self, w, h, fps, fmt='yuv', bpp=None, avgQP=None,PSNR=None):
        newFileName = self.generateFileName(w, h, fps,fmt='yuv', bpp=bpp1, avgQP=None,PSNR=psnr1)


        #PNGs to YUV
        if not os.path.exists(out_ab):
            raise FileExistsError('Output path "{}" cannot find, check HLVC decoding!'.format(out_ab))
        print('Changing PNGs to YUV......')
        cmd2='ffmpeg -i f%03d.png -s {}x{} -pix_fmt yuv420p {}'.format(w,h,newFileName)
        os.system('cd {};{}'.format(out_ab,cmd2))
        print('HLVC_decProcess finish: {}'.format(output))
        print('--------------HLVC Decoding: lumda={} Completed!------------------'.format(lumda))
        output = os.path.join(output, newFileName)
        return output
        #return newFileName


FUNCTION_REGISTER('encodingStage', 'HLVC', hlvc_dec,False)
