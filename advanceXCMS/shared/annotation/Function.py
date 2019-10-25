import os
from shutil import copyfile

import sys
from Class import Peak, Match

sys.path.append(
    os.path.join(
        os.getcwd(), '..'
    )
)

from advanceXCMS.shared import commonClasses

def read_library_peaks(input_file):
    fp = open(input_file, 'r')

    lines = fp.readlines()

    peak_list = []

    for i, line in enumerate(lines):
        parts = [x.strip('$').strip() for x in line.split('$')]
        try:
            rt = float(parts[1])
            mass = float(parts[2])
        except:
            try:
                parts = [x.strip(',').strip() for x in line.split(',')]
                rt = float(parts[2])
                mass = float(parts[1])
            except:
                print 'Warning: Error reading line %s from reference file' %i
                print '====================================================='
                print 'Line contents: %s' %line.strip()
                print
                continue

        name = parts[0]
        #print name, rt, mass
        tag = ''
        peak = Peak(float(mass), float(rt), name=name)
        peak.add_tag(tag)

        peak_list.append(peak)

    return peak_list


def read_xcms_peaks(input_file):
    fp = open(input_file, 'r')

    lines = fp.readlines()

    peak_list = []

    for line in lines[2:]:
        parts = line.split('\t')
        xcms_id = parts[0].strip('"')
        rt = parts[4]
        mass = parts[1]

        if parts[-3] != '' and parts[-2] == '':
            tag = parts[-3]
        elif parts[-3] == '' and parts[-2] != '':
            tag = parts[-2]
        elif parts[-3] != '' and parts[-2] != '':
            tag = parts[-3]+' ' + parts[-2]
        else:
            tag = ''

        tag = tag.strip('"')
        compound_group = parts[-1]
        name = 'unknown'


        peak = Peak(float(mass), float(rt), compound_group = compound_group, \
                    tag=tag, name=name)
        peak.set_xcms_id(int(xcms_id))


        peak_list.append(peak)

    return peak_list


def add_isotope(peak, isotope):
    mass = peak.get_mass()
    rt = peak.get_rt()
    tag = "M+"+str(isotope)
    name = peak.get_name()
    id_num = peak.get_id_num()
    new_mass = mass + isotope*1.0086710869

    new_peak = Peak(new_mass, rt, '0', tag, name=name+' '+tag)
    new_peak.set_parent(id_num)

    return new_peak


def get_adduct_peak(peak, adduct, mode):
    """
    Adducts are from CAMERA paper supplemental material
    """
    if mode not in ['pos','neg']:
        print "Error: mode must be 'pos' or 'neg'"

    mass = peak.get_mass()
    rt = peak.get_rt()

    positive_dict = {'M+H':1.0078250, 'M+Na':22.989769, 'M+K':39.0983,
                     'M+NH4':18.03773, 'M+2H(2+)':2.01565,
                     'M+Na+HCOOH':69.013079, 'M+H+K(2+)':40.106125,
                     '2M+Na':22.989769, 'M+K+HCOOH':85.12161,
                     '2M+K':39.0983}

    negative_dict = {"M-H":-1.0078250,"M-H+NaCOOH":66.997429,
                     "M-2H+Na":20.974119,"2M-2H+Na":20.974119,
                     "M-H+HCOOH":45.015485, "2M-H":-1.0078250,
                     "2M-2H+K":37.08265, "M-2H+K":37.08265}

    if adduct not in [positive_dict.keys(),negative_dict.keys()]:
        print "Error, adduct not found"


    if mode == 'pos':
        if '2M' in adduct:
            new_mass = 2*mass + positive_dict[adduct]
        else:
            new_mass = mass + positive_dict[adduct]
        if '(2+)' in adduct:
            new_mass = new_mass/2

    if mode == 'neg':
        if '2M' in adduct:
            new_mass = 2*mass + negative_dict[adduct]
        else:
            new_mass = mass + negative_dict[adduct]

    new_peak = Peak(new_mass, rt, '0', adduct)

    return new_peak

def get_adduct_peaks(peak, mode):
    """
    Adducts are from CAMERA paper supplemental material
    """
    if mode not in ['pos','neg']:
        print "Error: mode must be 'pos' or 'neg'"

    mass = peak.get_mass()
    rt = peak.get_rt()
    name = peak.get_name()

    positive_dict = {'M+H':1.0078250, 'M+Na':22.989769, 'M+K':39.0983,
                     'M+NH4':18.03773, 'M+2H(2+)':2.01565,
                     'M+Na+HCOOH':69.013079, 'M+H+K(2+)':40.106125,
                     '2M+Na':22.989769, 'M+K+HCOOH':85.12161,
                     '2M+K':39.0983}

    negative_dict = {"M-H":-1.0078250,"M-H+NaCOOH":66.997429,
                     "M-2H+Na":20.974119,"2M-2H+Na":20.974119,
                     "M-H+HCOOH":45.015485, "2M-H":-1.0078250,
                     "2M-2H+K":37.08265, "M-2H+K":37.08265}

    peaks = []

    if mode == 'pos':
        for key,value in positive_dict.iteritems():
            if '2M' in key:
                new_mass = 2*mass + value
            else:
                new_mass = mass + value
            if '(2+)' in key:
                new_mass = new_mass/2
            new_peak = Peak(new_mass, rt, '0', tag=key, name=name+' '+key)
            peaks.append(new_peak)

    if mode == 'neg':
        for key,value in negative_dict.iteritems():
            if '2M' in key:
                new_mass = 2*mass + value
            else:
                new_mass = mass + value
            if '(2+)' in key:
                new_mass = new_mass/2
            new_peak = Peak(new_mass, rt, '0', tag=key, name=name+' '+key)
            peaks.append(new_peak)

    return peaks


def get_decoy_peaks(peak, mode):
    """Based on the idea of Palmer, Alexandrov et al
    Use other elements from the periodic table to create
    impossible adducts
    """
    mass = peak.get_mass()
    rt = peak.get_rt()
    name = peak.get_name()
    decoy_dict = {'He':4.002602, 'Be':9.0121831, 'F':18.998403,
                  'Al':26.9815385, 'Sc':44.955908, 'Fe':55.845,
                  'Ge':72.630, 'Sr':87.62}
    HYDROGEN_MASS = 1.0078250

    id_num = peak.get_id_num()

    peaks = []

    if mode == 'pos':
        for key,value in decoy_dict.iteritems():
            new_mass = mass + value
            new_peak = Peak(new_mass, rt, '0', tag='+'+key, name=name+'+'+key)
            new_peak.set_parent(id_num)
            peaks.append(new_peak)

    if mode == 'neg':
        for key,value in decoy_dict.iteritems():
            new_mass = mass - HYDROGEN_MASS + value
            new_peak = Peak(new_mass, rt, '0', tag='-H+'+key, name=name+'-H+'+key)
            new_peak.set_parent(id_num)
            peaks.append(new_peak)

    return peaks

def write_library(peaks, output_file):

    op = open(output_file, 'w')
    op.write('Name, Mass, RT, Tag\n')
    for peak in peaks:
        name = peak.get_name()
        mass = peak.get_mass()
        rt = peak.get_rt()
        tag = peak.get_tag()
        op.write(name+','+str(mass)+','+str(rt)+','+tag+'\n')

def get_matches(library_peaks, xcms_peaks, ppm = None, seconds = None):

    for fn in xcms_peaks.featureNums:
        x_peak = xcms_peaks.featureDict[fn]
        x_mass = x_peak.getMZ()
        x_rt = x_peak.avgRT()

        for l_peak in library_peaks:
            l_mass = l_peak.get_mass()
            l_rt = l_peak.get_rt()
            if (abs(l_mass-x_mass)*1e6)/x_mass < ppm:
               # print "matched: ", l_peak.get_name(), "PPM error=",\
               #     (abs(l_mass-x_mass)*1e6)/x_mass

                massError = (abs(l_mass-x_mass)*1e6)/x_mass
                rtError = abs(l_rt-x_rt)

                if seconds:
                    if abs(rtError > seconds): continue

                data = {
                    'name': l_peak.get_name(),
                    'mz': l_peak.get_mass(),
                    'massError': massError,
                    'rt': l_peak.get_rt(),
                    'rtError': rtError
                    }
                x_peak.addAssignmentCandidate(data)
               # l_peak.matchedFeatures.append(fn)
    return xcms_peaks

def get_matches_consensus(library_peaks, consensus_peaks, ppm = None, seconds = None):
    for i, c in enumerate(consensus_peaks):
        x_mass = c.getMZ()
        x_rt = c.getRT()

        print 'Processing consensus peak %s: m/z: %s, rt: %s' %(
            i, x_mass, x_rt
        )


        for l_peak in library_peaks:
            l_mass = l_peak.get_mass()
            l_rt = l_peak.get_rt()
            if (abs(l_mass-x_mass)*1e6)/x_mass < ppm:
               # print "matched: ", l_peak.get_name(), "PPM error=",\
               #     (abs(l_mass-x_mass)*1e6)/x_mass

                print '    Match found: m/z: %s, rt = %s' %(
                    l_mass, l_rt
                )


                massError = (abs(l_mass-x_mass)*1e6)/x_mass
                rtError = abs(l_rt-x_rt)

                if seconds:
                    if abs(rtError > seconds): continue

                data = {
                    'name': l_peak.get_name(),
                    'mz': l_peak.get_mass(),
                    'massError': massError,
                    'rt': l_peak.get_rt(),
                    'rtError': rtError
                    }
                c.addAssignmentCandidate(data)

    return consensus_peaks

def rt_filter_matches(matches, seconds = 10):
    filtered_matches = []
    for match in matches:
        l_peak = match.get_l_peak()
        x_peak = match.get_x_peak()

        if abs((l_peak.get_rt()) - x_peak.get_rt()) < seconds:
            filtered_matches.append(match)

    return filtered_matches

def write_matches(matches, output_file):
    op = open(output_file, 'w')

    op.write("XCMS_id, XCMS Peak, Library Peak, XCMS Mass, Lib Mass, XCMS RT, Lib RT\n")

    l_names = []

    for match in matches:

        l_peak = match.get_l_peak()
        x_peak = match.get_x_peak()

        l_name = l_peak.get_name()
        if l_name in l_names:
            l_name = l_name + ' (1)'
        else:
            l_names.append(l_name)
        x_name = x_peak.get_tag()

        l_mass = l_peak.get_mass()
        x_mass = x_peak.get_mass()

        l_rt = l_peak.get_rt()
        x_rt = x_peak.get_rt()

        xcms_id = x_peak.get_xcms_id()

        op.write(str(xcms_id) + ',' + x_name + ',' + l_name + ',' + \
                 str(x_mass) + ',' + str(l_mass) + ',' + str(x_rt) + \
                 ',' + str(l_rt) +'\n')

def copy_annotated_pics(matches, pic_folder):
    l_names = []
    xcms_ids = []

    for match in matches:
        l_peak = match.get_l_peak()
        x_peak = match.get_x_peak()

        l_name = l_peak.get_name()
        if l_name in l_names:
            count = 0
            for name in l_names:
                if name == l_name:
                    count = count + 1
            l_name = l_name + ' ('+str(count)+')'
        l_names.append(l_name)

        xcms_id = x_peak.get_xcms_id()
        xcms_ids.append(xcms_id)

    # make a new folder
    if not os.path.exists(pic_folder + '/annotations'):
        os.makedirs(pic_folder + '/annotations')

    # copy files with correct name to new folder
    for i,xcms_id in enumerate(xcms_ids):
        if xcms_id < 100:
            xcms_id_str = '0' + str(xcms_id)
        else:
            xcms_id_str = str(xcms_id)
        src =  os.path.join(pic_folder, xcms_id_str + '.png')
        dst = pic_folder + '/annotations/' + l_names[i] + '.png'
        try:
            copyfile(src, dst)
        except:
            print "couldn't copy: ", dst, 'xcms id:', xcms_id

