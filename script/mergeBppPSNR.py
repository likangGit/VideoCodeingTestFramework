import re
from glob import glob
from matplotlib import pyplot as plt
label_file = {
    # 'downFrameRate':'results/RaceNight_640x448_50fps_8bit.yuv/downFr1_0.5_0.25_0.125/BppPSNR/data.txt',
    # 'downResolution':'results/RaceNight_640x448_50fps_8bit.yuv/downReso1_0.5_0.25/BppPSNR/data.txt',
    'H_Q_640x448':'results/RaceNight_640x448_50fps_8bit.yuv/q30_40_50/BppPSNR/data.txt',
    'L_Q_640x448':'results/FlowerKids_640x448_50fps.yuv/BppPSNR_q/data.txt',
    # 'Q_3840x2160':'results/FlowerKids_3840x2160_50fps_8bit.yuv/BppPSNR/data.txt',
    # 'Q_1920x1080':'results/FlowerKids_1920x1080_50fps_8bit.yuv/BppPSNR/data.txt'
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
        psnr_list = data_dict['psnr_list']
        bpp_list, sorted_psnr_list = zip(*sorted(zip(bpp_list, psnr_list)))
        ax1.plot(bpp_list, sorted_psnr_list, lt, label=label)
        kbps_list, sorted_psnr_list = zip(*sorted(zip(kbps_list, psnr_list)))
        ax2.plot(kbps_list, sorted_psnr_list, lt, label=label)
ax1.set_xlabel('bpp')
ax1.set_ylabel('PSNR/db')
ax2.set_xlabel('kbps')
ax2.set_ylabel('PSNR/db')
ax1.legend()
ax2.legend()
plt.savefig('results/mergeBppPsnr.png',dpi=200)
        