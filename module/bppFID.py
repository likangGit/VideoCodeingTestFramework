import os
import re
from glob import glob
from matplotlib import pyplot as plt
from .core import FUNCTION_REGISTER, Operator
class BppFID(Operator):
    def __init__(self):
        super(BppFID, self).__init__()

    def operate(self, inputs, output, output_root):
        print('BppFID start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        bpp_kbps_pattern = re.compile(r'.*_(\d+\.\d+)bpp_(\d+\.\d+)kbps.*')
        bpp_pattern = re.compile(r'.*_(\d+\.\d+)bpp*')
        fid_pattern = re.compile(r'.*_(\d+\.\d+)FID.yuv')
        bpp_list, kbps_list, fid_list = [], [], []

        for input in inputs:
            folders = input.split('/')
            path = ''
            for i, f in enumerate(folders):
                path = os.path.join(path, f)
                if 'encodingStage' in f:
                    break
            bpp_file =os.path.basename(glob(path+'/*bpp*.yuv')[0])
            #obj = bpp_kbps_pattern.match(bpp_file)

            # To find if kbps in filename, using "has_kbps" to record
            if 'kbps' in bpp_file:
                has_kbps = True
                obj = bpp_kbps_pattern.match(bpp_file)
                bpp, kbps = float(obj.group(1) ), float(obj.group(2) )
                bpp_list.append(bpp)
                kbps_list.append(kbps)
            else:
                has_kbps = False
                obj = bpp_pattern.match(bpp_file)
                bpp = float(obj.group(1))
                bpp_list.append(bpp)

            # psnr_path = os.path.join(path, folders[i+1])
            # psnr_file = os.path.basename(glob(psnr_path+'/*PSNR.yuv')[0])
            fid_file = os.path.basename(input)
            obj = fid_pattern.match(fid_file)
            fid = float(obj.group(1))
            fid_list.append(fid)
            
        save_dict = {'bpp_list':bpp_list, 'kbps_list':kbps_list, 'fid_list':fid_list}
        with open(os.path.join(output, 'data.txt'), 'w') as f:
            f.write(str(save_dict))
    
        self.plot(bpp_list, kbps_list, fid_list, output)
        print('BppFID finish:{}'.format(output))
        return inputs

    def plot(self, bpp_list, kbps_list, fid_list, output):
        if len(kbps_list) > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2)
        else:
            fig, (ax1) = plt.subplots(1)

        bpp_list, sorted_fid_list = zip(*sorted(zip(bpp_list, fid_list)))
        ax1.plot(bpp_list, sorted_fid_list)
        ax1.set_ylabel('FID')
        ax1.set_xlabel('bpp')
        ax1.grid()
        for x,y in zip(bpp_list, sorted_fid_list):
            ax1.text(x,y, '({}, {})'.format(x,y),va='bottom', fontsize=10)

        if len(kbps_list) > 0:
            kbps_list, sorted_fid_list = zip(*sorted(zip(kbps_list, fid_list)))
            ax2.plot(kbps_list, sorted_fid_list)
            ax2.set_ylabel('FID')
            ax2.set_xlabel('kbps')
            ax2.grid()
            for x,y in zip(kbps_list, sorted_fid_list):
                ax2.text(x,y, '({}, {})'.format(x,y),va='bottom', fontsize=10)

        plt.savefig(os.path.join(output, 'line.png'), dpi=200)           
       

FUNCTION_REGISTER('visualizationResultStage', 'BppFID', BppFID, False)