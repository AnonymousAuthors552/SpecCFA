import matplotlib
import matplotlib.pyplot as pyplot

pyplot.rcParams["figure.figsize"] = (5.25,3.5)
w = 0.3

font = {'size' : 14}

matplotlib.rc('font', **font)

geiger = {
    "Name": "Geiger",
    "Lim": 1800,
    "Labels": ["Baseline", "Manual", "Select", "Minimze", "Top", "Static"],
    "Entries": [435, 124, 317, 306, 142, 381],
    "Log_size": [1740, 496, 1268, 1224, 568, 1524],
    "Blockmem": [0, 444, 128, 104, 684, 96],
    "Blocks": [0, 8, 2, 8, 8, 8]
}

gps = {
    "Name": "GPS",
    "Lim": 21000,
    "Labels": ["Baseline", "Manual", "Select", "Minimze", "Top", "Static"],
    "Entries": [4969, 2086, 2599,  3502, 2142, 4943],
    "Log_size": [19876, 8344, 10396, 14008, 8568, 19772],
    "Blockmem": [0, 260, 128, 60, 500, 84],
    "Blocks": [0, 8, 4, 8, 8, 8]
}

syringe = {
    "Name": "Syringe Pump",
    "Lim": 56000,
    "Labels": ["Baseline", "Manual", "Select", "Minimze", "Top", "Static"],
    "Entries": [13650, 435, 498, 645, 477, 852],
    "Log_size": [54600, 1740, 1992, 2580, 1908, 3408],
    "Blockmem": [0, 140, 128, 76, 214, 100],
    "Blocks": [0, 8, 4, 8, 5, 8]
}

temperature = {
    "Name": "Temperature Sensor",
    "Lim": 2550,
    "Labels": ["Baseline", "Manual", "Select", "Minimze", "Top", "Static"],
    "Entries": [627, 30, 35, 110, 305, 198],
    "Log_size": [2508, 120, 140, 440, 1220, 792],
    "Blockmem": [0, 144, 128, 88, 266, 84],
    "Blocks": [0, 8, 4, 8, 7, 8]
}
ultrasonic = {
    "Name": "Utrasonic Sensor",
    "Lim": 4500,
    "Labels": ["Baseline", "Manual", "Select", "Minimze", "Top", "Static"],
    "Entries": [1040, 11, 5, 17, 5, 22],
    "Log_size": [4160, 44, 20, 68, 20, 88],
    "Blockmem": [0, 84, 102, 72, 102, 42],
    "Blocks": [0, 8, 3, 8, 3, 5]
}
mouse = {
    "Name": "Mouse",
    "Lim": 4500,
    "Labels": ["Baseline", "Manual", "Select", "Minimze", "Top", "Static"],
    "Entries": [9673, 1822, 4406, 4140, 2015, 9123],
    "Log_size": [38692, 7288, 17624, 16560, 8060, 9123*4],
    "Blockmem": [0, 85, 128, 196, 444, 84],
    "Blocks": [0, 8, 4, 8, 8, 8]
}

tests = [geiger, gps, syringe, temperature, ultrasonic, mouse]

for test in tests:
    policies = test["Labels"][:]
    logs = test["Log_size"][:]
    blockmem = test["Blockmem"][:]

    print(f"policies: {policies}")


    # pyplot.bar(policies, logs, label="CFlog", color='white', edgecolor='black', width=w)
    # pyplot.bar(policies, blockmem, bottom=logs, label="Blockmem", color='grey', edgecolor='black', width=w)
    # pyplot.title(test["Name"])
    # pyplot.xlabel("Sub-Path Selection Policy")
    # pyplot.ylim((0,test["Lim"]))
    # pyplot.ylabel("Total Bytes")
    # pyplot.legend()

    pyplot.bar(policies[1:], logs[1:], label="CFlog",  color='white', edgecolor='black', width=w),
    pyplot.bar(policies[1:], blockmem[1:], bottom=logs[1:], label="Blockmem", color='grey', edgecolor='black', width=w)
    pyplot.title(test["Name"])
    pyplot.xlabel("Sub-Path Selection Policy")
    pyplot.ylabel("Total Bytes")
    pyplot.legend(loc="upper left", ncol=2)
    # # pyplot.savefig(f"{test['Name']}_policies_only.png")
    # pyplot.show()
    # pyplot.clf()

    pyplot.tight_layout()
    pyplot.savefig(f"{test['Name']}-selections.png")
    # pyplot.show()
    pyplot.clf()
