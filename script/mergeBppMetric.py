import re
from glob import glob
from matplotlib import pyplot as plt

def getMetricName(dataDict):
    name_list = ['PSNR', 'FID', 'NIQE']
    for n in name_list:
        if n+'_list' in dataDict:
            return n

label_file = {
    'NVENC50gop': 'results/11221_1920x1080_25fps_8bit.yuv/nvenc_cq_gop50/BppMetrics/data.txt',
    'NVENC100gop':'results/11221_1920x1080_25fps_8bit.yuv/nvenc_cq_gop100/BppMetrics/data.txt',
    'NVENC250gop':'results/11221_1920x1080_25fps_8bit.yuv/nvenc_cq_gop250/BppMetrics/data.txt',
    'NVENC500gop':'results/11221_1920x1080_25fps_8bit.yuv/nvenc_cq_gop500/BppMetrics/data.txt',
    
    }
fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,5))
ax1.grid(True)
ax2.grid(True)
line_type = ['s-b','v--g','o-.r','d-m','h-.k','o-r']
for (label,data), lt in zip(label_file.items(), line_type):

    with open(data, 'r') as f:
        data_dict = eval(f.read())
        metric_name = getMetricName(data_dict)
        bpp_list = data_dict['bpp_list']
        kbps_list = data_dict['kbps_list']
        psnr_list = data_dict[metric_name + '_list']
        bpp_list, sorted_psnr_list = zip(*sorted(zip(bpp_list, psnr_list)))
        ax1.plot(bpp_list, sorted_psnr_list, lt, label=label)
        kbps_list, sorted_psnr_list = zip(*sorted(zip(kbps_list, psnr_list)))
        ax2.plot(kbps_list, sorted_psnr_list, lt, label=label)
ax1.set_xlabel('bpp')
ax1.set_ylabel(metric_name)
ax2.set_xlabel('kbps')
ax2.set_ylabel(metric_name)
ax1.legend()
ax2.legend()
plt.savefig('results/mergeBpp{}.png'.format(metric_name),dpi=200)

