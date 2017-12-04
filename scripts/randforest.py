import numpy as np	
from datetime import datetime
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection  import GridSearchCV
from matplotlib import pyplot as plt

import fileinput

def get_data(file):
    df = pd.read_csv(file, sep=" ", header=None)
    
    t = 0   # target
    nlinks = 2  #3 
    
    if nlinks == 3:
        df[1] = df[1] / df[1][df[1].idxmax()]
        df[2] = df[2] / df[2][df[2].idxmax()]
    
    df.loc[:, nlinks+1:] = df.loc[:, nlinks+1:] / df[nlinks][df[nlinks].idxmax()]  #   norm by max links


    data = df.as_matrix()
    np.random.shuffle(data)
    x = data[:, 1:]  
    y = data[:, t]
    z = data[:, nlinks] 

    return x, y, z, df


def find_best(x, y):
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
    CV_rfc.fit(x, y)

    # Print n return best parameters
    print('\n',CV_rfc.best_params_)   
    return CV_rfc.best_estimator_.n_estimators, CV_rfc.best_estimator_.max_features, CV_rfc.best_estimator_.criterion 


def myfit(x, y):
    clf =  RandomForestClassifier(n_jobs=-1, max_features= maxf, n_estimators=n_est, 
                                  criterion = crit, min_samples_leaf = min_s_leaf, oob_score = True) 
    clf.fit(x, y)
    return(clf)



def plottami(x, y, z):
    
    same_chr = np.sum(y == 1)
    print("  I have", len(y), "linked pair of scaffolds and:\n    ", 
          same_chr, "from the same chromosome (", 
          same_chr*100./len(y), "%)")
    
    nlinks = np.sum(z)
    print("    ", nlinks, "total number of links")
   
    #plt.hist(z) 
    #plt.show()
    #plt.scatter(z,y) 
    #plt.show()

#### main ####
resize=1
findbest=1
fitX=1
fitZ=1
predictX=1
predictZ=1
info=0




### Get Data ###

try: 
    size
except NameError:    
    myfile='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/bothhic_fromscratch/bwa_temp/hicana/more/map_n_reads.txt'
    #myfile='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/bothhic/bwa_temp/hicana/map_n_reads.txt'
    X, target, Z, df = get_data(myfile)
    size=len(target)

if resize:  
    test_perc=0.8
    X_train, X_test, y_train, y_test = train_test_split(X, target, random_state=1, test_size = test_perc)
    Z1=Z.reshape(-1, 1) 
    Z_train, Z_test, y_train, y_test = train_test_split(Z1, target, random_state=1, test_size = test_perc)




### Print and Plot some Infos ###

if info:
    print("\n Some info from the sample:")
    plottami(X, target, Z)
    print("\n")



### Fit n Predict ###

if findbest:
    n_est, maxf, crit, min_s_leaf = find_best(X_train, y_train)
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


