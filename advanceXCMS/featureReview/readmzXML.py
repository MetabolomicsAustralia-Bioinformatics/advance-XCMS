


from pyteomics import mzxml, auxiliary

dataFiles = ['/media/sf_VM_share/singapore_all_data/batch4/PQC/Placenta QC (063).mzXML']

with mzxml.read(dataFiles[0]) as reader:
    auxiliary.print_tree(next(reader))

    for scan in reader:
        lvl = int(scan['msLevel'])
        time = float(scan['retentionTime']) * 60
        if scan['msLevel'] != 1: continue
        mzs = scan['m/z array']
        ints = scan['intensity array']
        print lvl, time, type(mzs), type(ints)
