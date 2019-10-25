import sys

if1 = open(sys.argv[1],'r')
cols = [int(c.strip(',').strip()) for c in sys.argv[2].split(',')]

with open(sys.argv[1],'r') as if1:
    for l in if1:
        l = [l.strip(',').strip() for l in l.split(',')]

        out = []

        for c in cols:
            out.append(l[c])

        print((len(out)*"{: >20} ").format(*out))

