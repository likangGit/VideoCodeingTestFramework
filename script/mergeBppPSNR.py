import re
from glob import glob
from matplotlib import pyplot as plt
data_list = glob('results/Flower*/BppPSNR/data.txt')
fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,5))

ax1.grid(True)
ax2.grid(True)
scale_patten = re.compile(r'.*_(\d+\D{1}\d+)_.*')
line_type = ['-b','--r','-.b','-g','-.k']
for data, lt in zip(data_list, line_type):
    label = scale_patten.match(data).group(1)

    with open(data, 'r') as f:
        data_dict = eval(f.read())
        bpp_list = data_dict['bpp_list']
        kbps_list = data_dict['kbps_list']
        psnr_list = data_dict['psnr_list']
        ax1.plot(bpp_list, psnr_list, lt, label=label)
        ax2.plot(kbps_list, psnr_list, lt, label=label)
ax1.set_xlabel('bpp')
ax1.set_ylabel('PSNR/db')
ax2.set_xlabel('kbps')
ax2.set_ylabel('PSNR/db')
ax1.legend()
ax2.legend()
plt.savefig('results/mergeBppPsnr.png',dpi=200)
        