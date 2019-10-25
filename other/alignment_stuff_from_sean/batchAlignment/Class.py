import numpy

class Peak(object):

    def __init__(self, index, mz, rt, fname, areas, metName):
        self.index = index
        self.mz = mz
        self.rt = rt
        self.fnames = fname
        self.areas = numpy.array(areas[0:10]) # first 5 peak areas
        self.allAreas = areas
        self.metName = metName
        self.container = []
        self.counter = 0
        #self.__avg_area = sum(self.__areas)/len(self.__areas)

    def get_name(self):
        return self.fnames

    def get_index(self):
        return self.index

    def get_mz(self):
        return self.mz

    def get_rt(self):
        return self.rt

    #def get_avg_area(self):
    #return self.__avg_area
    def get_areas(self):
        return self.areas


class Score(object):

    def __init__(self, len_pklist1, len_pklist2):
        print len_pklist1, len_pklist2
        print type(len_pklist1)
        self.score_matrix = numpy.zeros((len_pklist1, len_pklist2))

    def add_score(self, score, pos1, pos2):
        self.score_matrix[pos1, pos2] = score

    def get_score_matrix(self):
        return self.score_matrix
