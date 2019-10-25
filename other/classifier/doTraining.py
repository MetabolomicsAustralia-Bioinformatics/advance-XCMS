import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression as LR
from sklearn.preprocessing import MinMaxScaler
import pickle

fname = sys.argv[1]
# names = ['maxint', 'intRange', 'noiseLevel', 'gSSE', 'centroid', 'class']

names = ['maxint', 'SNR', 'gSSE', 'centroid', 'localMaxima', 'class']

data = pd.read_csv(fname, names = names)

print data.shape
#print data.dtypes
print data.head(10)

pd.set_option('precision', 3)

#print
#print data.describe()

data['gSSE'] = data['gSSE'].astype(np.float64)
data['centroid'] = data['centroid'].astype(np.float64)

print data.dtypes
print
print data.describe()
print

# be careful of nan values
# seem to be only 1 in GSSE and centroid cols
print data.isnull().any()
print data.isnull().sum()

# drop nan values

print data.shape
data = data.dropna()
print data.shape

# from pandas.tools.plotting import scatter_matrix

# scatter_matrix(data)
# plt.show()

dataVals = data.values

X = dataVals[:, 0:5]
Y = dataVals[:, 5]

print X.shape
print Y.shape
print Y


scaler = MinMaxScaler(feature_range = (0,1))
rX = scaler.fit_transform(X)

print rX[0:10,:]


def linReg(features, assignments, test_size = 0.3, seed = 7):

    features_train, features_test, assignments_train, assignments_test = cross_validation.train_test_split(features, assignments, test_size = test_size, random_state = seed)
#
#    print features_train.shape
#    print assignments_train.shape
#
#    print features_test.shape
#    print assignments_test.shape
#
    model = LR()
    model.fit(features_train, assignments_train)

    result = model.score(features_test, assignments_test)

    print ("accuracy: %.3f%%" %(result*100))

    printDetails = True

    if printDetails:

        print '\n\n'
        print 'Classes', model.classes_
        print 'Decision Function:', model.decision_function(X)
        print 'Probability', model.predict_proba(X)
        print 'Coefficients'
        print model.coef_


    return model

model = linReg(rX,Y)

outFile = 'model.model'
pickle.dump(model, open(outFile, 'wb'))

