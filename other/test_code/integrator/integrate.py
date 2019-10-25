import os
import numpy as np
import matplotlib.pyplot as plt


'''
Alignment method
https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-8-419
'''


def getData(filei):
    if1 = open(filei,'r').readlines()

    rts = []
    ints = []

    for line in if1:
        l = [float(x.strip().strip(' ')) for x in line.split(' ')]

        rt, i = l[1],l[2]
        rts.append(rt)
        ints.append(i)

    rts = np.asarray(rts)
    ints = np.asarray(ints)

    return ints

files = ['p1.dat','p3.dat']

data = []
lengths = []

for f in files
    data.append(f)
    lengths.append(len(f))

v = max(lengths)
index = lengths.index(v)
minval = min(lengths)




#plt.plot(np.arange(len(i1)), i1)
#plt.plot(np.arange(len(i2)), i2)
#plt.show()

print len(i1), len(i2)

maxShift = 10

low, high = 0, len(i1)

print low,high

for i in range(maxShift * -1, maxShift + 1):
    xs1 = np.arange(len(i1))
    xs2 = np.arange(len(i2))

    shift1 = xs1 + i

    mask = np.where((shift > min(xs2)) & (shift < max(xs2)))

    s1 = xs1[mask]

    mask = np.where((shift > min(xs1)) & (shift < max(xs1)))

    print xs1
    print xs2


