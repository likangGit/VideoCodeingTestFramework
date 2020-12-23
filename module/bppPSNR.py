import os
import re
import shutil
import yaml
from glob import glob
from matplotlib import pyplot as plt
from .core import FUNCTION_REGISTER, Operator
class BppPSNR(Operator):
    def __init__(self):
        super(BppPSNR, self).__init__()

    def operate(self, inputs, output, output_root):
        print('BppPSNR start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        
        bpp_kbps_pattern = re.compile(r'.*_(\d+\.\d+)bpp_(\d+\.\d+)kbps.*')
        psnr_pattern = re.compile(r'.*_(\d+\.\d+)PSNR.yuv')
        bpp_list, kbps_list, psnr_list = [], [], []

        for input in inputs:
            folders = input.split('/')
            path = ''
            for i, f in enumerate(folders):
                path = os.path.join(path, f)
                if 'encodingStage' in f:
                    break
            bpp_file = os.path.basename(glob(path+'/*bpp*.yuv')[0])
            obj = bpp_kbps_pattern.match(bpp_file)
            if obj:
                bpp, kbps = float(obj.group(1) ), float(obj.group(2) )
                bpp_list.append(bpp)
                kbps_list.append(kbps)
            psnr_path = os.path.join(path, folders[i+1])
            psnr_file = os.path.basename(glob(psnr_path+'/*PSNR.yuv')[0])
            obj = psnr_pattern.match(psnr_file)
            if obj:
                psnr = float(obj.group(1))
                psnr_list.append(psnr)
        save_dict = {'bpp_list':bpp_list, 'kbps_list':kbps_list, 'psnr_list':psnr_list}
        with open(os.path.join(output, 'data.txt'), 'w') as f:
            f.write(str(save_dict))
        fig, (ax1, ax2) = plt.subplots(1,2)
        ax1.plot(bpp_list, psnr_list)
        ax1.set_ylabel('PSNR/db')
        ax1.set_xlabel('bpp')
        ax1.grid()
        for x,y in zip(bpp_list, psnr_list):
            ax1.text(x,y, '({}, {})'.format(x,y), va='bottom', fontsize=10)
        ax2.plot(kbps_list, psnr_list)
        ax2.set_ylabel('PSNR/db')
        ax2.set_xlabel('kbps')
        ax2.grid()
        for x,y in zip(kbps_list, psnr_list):
            ax2.text(x,y, '({}, {})'.format(x,y), va='bottom', fontsize=10)
        plt.savefig(os.path.join(output, 'line.png'), dpi=200)           
       
        print('BppPSNR finish:{}'.format(output))
        return inputs

FUNCTION_REGISTER('visualizationResultStage', 'BppPSNR', BppPSNR, False)