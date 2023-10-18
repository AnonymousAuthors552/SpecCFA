# libraries
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (13*2,7*2)

font = {'size'   : 24*2}

matplotlib.rc('font', **font)

CFLOG = 0
BLOCKMEM = 1
temp = {}
temp[CFLOG] = [1254, 676, 200, 222, 210, 186, 188, 182, 156]
for i in range(len(temp[CFLOG])):
    temp[CFLOG][i] *= 2
temp[BLOCKMEM] = [0, 82, 112, 146, 176, 190, 208, 226, 248]

ultrasonic = {}
ultrasonic[CFLOG] = [2080, 150, 144, 136, 128, 122, 118]
for i in range(len(ultrasonic[CFLOG])):
    ultrasonic[CFLOG][i] *= 2
ultrasonic[BLOCKMEM] = [0, 82, 92, 114, 136, 154, 168]

geiger = {}
geiger[CFLOG] = [870, 840, 718, 614, 524, 410, 370, 326, 248]
for i in range(len(geiger[CFLOG])):
    geiger[CFLOG][i] *= 2
geiger[BLOCKMEM] = [0, 26, 112, 134, 228, 314, 384, 418, 444]

syringe = {}
syringe[CFLOG] = [27300, 2628, 2040, 1648, 1636, 1628, 1622, 1616, 1610]
for i in range(len(syringe[CFLOG])):
    syringe[CFLOG][i] *= 2
syringe[BLOCKMEM] = [0, 82, 104, 122, 140, 162, 180, 198, 216]

gps = {}
gps[CFLOG] = [9938, 6824, 5970, 5770, 5442, 5320, 5064, 5052, 4832]
for i in range(len(gps[CFLOG])):
    gps[CFLOG][i] *= 2
gps[BLOCKMEM] = [0, 18, 36, 54, 92, 110, 152, 230, 260]

# # hardware based solutions
# litehax = [0.03*xc7z020[LUT], 0.02*xc7z020[FF]] #https://ieeexplore-ieee-org.ezproxy.rit.edu/stamp/stamp.jsp?tp=&arnumber=8587757
# lofat = [0.06*xc7z020[LUT], 0.04*xc7z020[FF]] #https://dl.acm.org/doi/pdf/10.1145/3061639.3062276
# atrium = [0.2*xc7z020[LUT], 0.15*xc7z020[FF]] #https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8203803

# # create dataset
# lut = [acfa[LUT], acfa_sponge[LUT],  garota[LUT], tinycfa[LUT], sancus[LUT], msp430[LUT],]
# ff = [acfa[FF], acfa_sponge[FF],  garota[FF], tinycfa[FF], sancus[FF], msp430[FF]]
# bars = ('ACFA', 'ACFA\nw/ Hash Engine', 'GAROTA', 'Tiny-CFA\n(APEX)', 'SANCUS', 'openMSP430')
# x_pos = np.arange(len(bars))
 
# # Create bars and choose color https://towardsdatascience.com/how-to-fill-plots-with-patterns-in-matplotlib-58ad41ea8cf8
bars = (0, 1, 2, 3, 4, 5, 6, 7, 8)
x_pos = np.arange(len(bars))

plt.bar(x_pos - 0.2, gps[CFLOG], 0.4, label="CFLog", color="lightgrey", linewidth=4, edgecolor='black')
plt.bar(x_pos + 0.2, gps[BLOCKMEM], 0.4, label="BlockMem",  linewidth=4,  fill=False, edgecolor='black')
plt.title("GPS")
plt.legend()
plt.ylabel('Total Bytes')
plt.xlabel('Total Sub-paths')
plt.xticks(x_pos, bars)
plt.savefig('gps_plot.png')
plt.clf()

plt.bar(x_pos - 0.2, geiger[CFLOG], 0.4, label="CFLog", color="lightgrey", linewidth=4, edgecolor='black')
plt.bar(x_pos + 0.2, geiger[BLOCKMEM], 0.4, label="BlockMem",  linewidth=4, fill=False, edgecolor='black')
plt.title("Geiger")
plt.legend()
plt.ylabel('Total Bytes')
plt.xlabel('Total Sub-paths')
plt.xticks(x_pos, bars)
plt.savefig('geiger_plot.png')
plt.clf()

plt.bar(x_pos - 0.2, temp[CFLOG], 0.4, label="CFLog", color="lightgrey", linewidth=4, edgecolor='black')
plt.bar(x_pos + 0.2, temp[BLOCKMEM], 0.4, label="BlockMem",  linewidth=4,  fill=False, edgecolor='black')
plt.title("Temperature Sensor")
plt.legend()
plt.ylabel('Total Bytes')
plt.xlabel('Total Sub-paths')
plt.xticks(x_pos, bars)
plt.savefig('temperature_plot.png')
plt.clf()

plt.bar(x_pos - 0.2, syringe[CFLOG], 0.4, label="CFLog", color="lightgrey", linewidth=4, edgecolor='black')
plt.bar(x_pos + 0.2, syringe[BLOCKMEM], 0.4, label="BlockMem",  linewidth=4,  fill=False, edgecolor='black')
plt.title("Syringe Pump")
plt.legend()
plt.ylabel('Total Bytes')
plt.xlabel('Total Sub-paths')
plt.xticks(x_pos, bars)
plt.savefig('syringe_plot.png')
plt.clf()

bars = (0, 1, 2, 3, 4, 5, 6)
x_pos = np.arange(len(bars))
plt.bar(x_pos - 0.2, ultrasonic[CFLOG], 0.4, label="CFLog", color="lightgrey", linewidth=4, edgecolor='black')
plt.bar(x_pos + 0.2, ultrasonic[BLOCKMEM], 0.4, label="BlockMem",  linewidth=4,  fill=False, edgecolor='black')
plt.title("Ultrasonic Sensor")
plt.legend()
plt.ylabel('Total Bytes')
plt.xlabel('Total Sub-paths')
plt.xticks(x_pos, bars)
plt.savefig('ultrasonic_plot.png')
plt.clf()