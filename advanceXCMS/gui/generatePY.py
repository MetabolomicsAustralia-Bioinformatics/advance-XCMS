import os, sys

os.chdir(os.path.dirname(sys.argv[0]))

wd = os.getcwd()
files = [f for f in os.listdir(wd) if '.ui' in f]

for filei in files:
    outName = filei.replace('.ui','.py')
    print filei, '>>>', outName
    os.system('pyuic4 -x %s -o %s' %(filei, outName))
