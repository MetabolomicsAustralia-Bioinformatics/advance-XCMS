import numpy as np
import matplotlib.pyplot as plt
#plt.style.use('seaborn-deep')

if1 = open('optTest.dat', 'r').readlines()

iters = []
diffs = []
for l in if1:
    l = [_.strip() for _ in l.split(' ')]
    iters.append(int(l[0]))
    diffs.append(float(l[3]))

iterVals = list(set(iters))

iters = np.asarray(iters)
diffs = np.asarray(diffs)

results = []
labels = []
for i in iterVals:
    labels.append(str(i))
    mask = np.where(iters == i)
    iterdiffs = diffs[mask]
    print (np.sum(iterdiffs) / iterdiffs.shape[0]), iterdiffs.shape[0]
    results.append(iterdiffs)

#for i in results:
#    plt.hist(i, bins= 'auto', alpha = 0.5)
plt.hist(results, bins= 'auto', alpha = 0.5, label = labels)
plt.legend()
plt.show()


