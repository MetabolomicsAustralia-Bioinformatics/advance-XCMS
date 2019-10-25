import numpy

class Peak(object):

    def __init__(self, index, mz, rt, areas):
        self.__index = index
        self.__mz = mz
        self.__rt = rt
        self.__areas = numpy.array(areas) # first 5 peak areas

        #self.__avg_area = sum(self.__areas)/len(self.__areas)

    def get_index(self):
        return self.__index
        
    def get_mz(self):
        return self.__mz

    def get_rt(self):
        return self.__rt

    #def get_avg_area(self):
    #return self.__avg_area
    def get_areas(self):
        return self.__areas

    
class Score(object):

    def __init__(self, len_pklist1, len_pklist2):
        print len_pklist1, len_pklist2
        print type(len_pklist1)
        self.score_matrix = numpy.zeros((len_pklist1, len_pklist2))

    def add_score(self, score, pos1, pos2):
        self.score_matrix[pos1, pos2] = score

    def get_score_matrix(self):
        return self.score_matrix
