import re
from glob import glob
from matplotlib import pyplot as plt
label_file = {
    'R0.5_Q*':'results/FlowerKids_640x448_50fps.yuv/r0.5_q20_50_fid/BppFID/data.txt',
    'Q*':'results/FlowerKids_640x448_50fps.yuv/q20_50_fid/BppFID/data.txt',

    }
# label_file = {'3840x2160':'results/FlowerKids_3840x2160_50fps_8bit.yuv/BppPSNR/data.txt',
#                 '1920x1080':'results/FlowerKids_1920x1080_50fps_8bit.yuv/BppPSNR/data.txt'} 
fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,5))
ax1.grid(True)
ax2.grid(True)
line_type = ['s-b','v--g','o-.r','d-m','h-.k']
for (label,data), lt in zip(label_file.items(), line_type):

    with open(data, 'r') as f:
        data_dict = eval(f.read())
        bpp_list = data_dict['bpp_list']
        kbps_list = data_dict['kbps_list']
        psnr_list = data_dict['fid_list']
        bpp_list, sorted_psnr_list = zip(*sorted(zip(bpp_list, psnr_list)))
        ax1.plot(bpp_list, sorted_psnr_list, lt, label=label)
        kbps_list, sorted_psnr_list = zip(*sorted(zip(kbps_list, psnr_list)))
        ax2.plot(kbps_list, sorted_psnr_list, lt, label=label)
ax1.set_xlabel('bpp')
ax1.set_ylabel('FID')
ax2.set_xlabel('kbps')
ax2.set_ylabel('FID')
ax1.legend()
ax2.legend()
plt.savefig('results/mergeBppFid.png',dpi=200)
        