import numpy as np	
from datetime import datetime
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier
from sklearn.grid_search import GridSearchCV
from matplotlib import pyplot as plt

import fileinput

def get_data(file):
    df = pd.read_csv(file, sep=" ")
    data = df.as_matrix()
    np.random.shuffle(data)
    X = data[:, 1:]  # 100 # norm by bin
    Y = data[:, 0]
    Z = data[:, 2] 

    return X, Z, Y

def find_best():
    clf =  RandomForestClassifier(n_jobs=-1,max_features= 'sqrt' , n_estimators=50, oob_score = True) 
    param_grid = {        
        'n_estimators': [200, 700, 1000],
        'max_features': ['auto', 'sqrt', 'log2'],
        'criterion': ['gini', 'entropy'],
        'min_samples_leaf': [1, 5, 10]
        }
    
    # Create a classifier with the parameter candidates
    CV_rfc = GridSearchCV(estimator=clf, param_grid=param_grid, cv= 5)
    
    # Train the classifier on training data
    CV_rfc.fit(X_train, y_train)

    print('\n',CV_rfc.best_params_)
    
    return CV_rfc.best_estimator_.n_estimators, CV_rfc.best_estimator_.max_features, CV_rfc.best_estimator_.criterion 


def myfit(x, y):
    clf =  RandomForestClassifier(n_jobs=-1, max_features= maxf, n_estimators=n_est, 
                                  criterion = crit, min_samples_leaf = min_s_leaf, oob_score = True) 
    clf.fit(x, y)
    return(clf)


def plottami(x, y):
    

    
    #plt.hist(Y) 
    #plt.show()

#### main ####
resize=1
findbest=0
fitX=1
fitZ=1
predictX=1
predictZ=1
plot=0


try: 
    size
except NameError:    
    myfile='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/bothhic_fromscratch/bwa_temp/hicana/map_n_reads.txt'
    X, Z, target = get_data(myfile)
    size=len(target)

if resize:  
    X_train, X_test, y_train, y_test = train_test_split(X, target, random_state=1, test_size=0.2)
    Z=Z.reshape(-1, 1) 
    Z_train, Z_test, y_train, y_test = train_test_split(Z, target, random_state=1, test_size=0.2)




if plot:
    plottami(X, target)


if findbest:
    n_est, maxf, crit, min_s_leaf = find_best()
else:
    n_est = 200 
    maxf = 'auto'
    crit = 'gini'
    min_s_leaf = 10


if fitX:    
    Xclf =  myfit(X_train, y_train)
if fitZ:    
    Zclf =  myfit(Z_train, y_train)

    
   
if predictX:
    results = Xclf.predict(X_train) 
    score = metrics.accuracy_score(y_train,results)
    print("Using X: train:",score)

    results = Xclf.predict(X_test)
    score =  metrics.accuracy_score(y_test,results)
    print("Using X: test",score)


if predictZ:
    results = Zclf.predict(Z_train) 
    score = metrics.accuracy_score(y_train,results)
    print("Using Z: train:",score)

    results = Zclf.predict(Z_test)
    score =  metrics.accuracy_score(y_test,results)
    print("Using Z: test",score)


