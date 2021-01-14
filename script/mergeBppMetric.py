import re
from glob import glob
from matplotlib import pyplot as plt
ylable='NIQE'
label_file = {
    'R0.5_Q*':'results/FlowerKids_640x448_50fps.yuv/r0.5_q20_50_niqe/BppMetrics/data.txt',
    'Q*':'results/FlowerKids_640x448_50fps.yuv/q20_50_niqe/BppMetrics/data.txt',
    }
fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,5))
ax1.grid(True)
ax2.grid(True)
line_type = ['s-b','v--g','o-.r','d-m','h-.k']
for (label,data), lt in zip(label_file.items(), line_type):

    with open(data, 'r') as f:
        data_dict = eval(f.read())
        bpp_list = data_dict['bpp_list']
        kbps_list = data_dict['kbps_list']
        psnr_list = data_dict['metric_list']
        bpp_list, sorted_psnr_list = zip(*sorted(zip(bpp_list, psnr_list)))
        ax1.plot(bpp_list, sorted_psnr_list, lt, label=label)
        kbps_list, sorted_psnr_list = zip(*sorted(zip(kbps_list, psnr_list)))
        ax2.plot(kbps_list, sorted_psnr_list, lt, label=label)
ax1.set_xlabel('bpp')
ax1.set_ylabel(ylable)
ax2.set_xlabel('kbps')
ax2.set_ylabel(ylable)
ax1.legend()
ax2.legend()
plt.savefig('results/mergeBpp{}.png'.format(ylable),dpi=200)
        