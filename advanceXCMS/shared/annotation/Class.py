import numpy

class Peak(object):

    def __init__(self, mass, rt, compound_group=0, tag='',name=''):

        self.mz = mass
        self.rt = rt
        self.compound_group = compound_group
        self.tag = tag
        self.name = name
        self.id_num = numpy.random.rand(1)[0]
        self.matchedFeatures = []

    def get_name(self):
        return self.name

    def get_mass(self):
        return self.mz

    def get_rt(self):
        return self.rt

    def get_tag(self):
        return self.tag

    def get_id_num(self):
        return self.id_num

    def add_tag(self, tag):
        """
        tag shows if it's an isotope
        adduct etc,

        """
        self.tag = tag

    def set_parent(self, parent):
        # parent: the id_num of the parent peak
        self.parent = parent

    def set_xcms_id(self, xcms_id):
        self.xcms_id = xcms_id

    def get_xcms_id(self):
        if self.xcms_id:
            return self.xcms_id
        else:
            return 0

class Match(object):
    def __init__(self, l_match, x_match):
        self.__l_match = l_match
        self.__x_match = x_match

    def get_l_peak(self):
        return self.__l_match

    def get_x_peak(self):
        return self.__x_match

