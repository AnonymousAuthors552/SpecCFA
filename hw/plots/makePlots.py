# libraries
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (12*1.5,4*1.5)

font = {'size'   : 24*1.5}

matplotlib.rc('font', **font)

# create dataset
lut = [2122, 197, 303, 439, 560, 681, 807, 929, 1051]
ff = [910, 122, 228, 364, 485, 606, 732, 854, 976]
bars = ('Baseline', '1', '2', '3', '4', '5', '6', '7', '8')
x_pos = np.arange(len(bars))
 
# Create bars and choose color https://towardsdatascience.com/how-to-fill-plots-with-patterns-in-matplotlib-58ad41ea8cf8
plt.bar(x_pos - 0.2, lut, 0.4, hatch='/', label="LUT", color='lightgray', edgecolor='black')
plt.bar(x_pos + 0.2, ff, 0.4, hatch='.', label="FF", fill=False)

# Show legend
plt.legend()

#Y axis label
plt.ylabel('Total Count')
 
# Create names on the x axis
plt.xticks(x_pos, bars)

# Show graph
# plt.show()

# Save graph
plt.savefig('hw_cost.png')

# Clear graph
plt.clf()