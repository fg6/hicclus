import numpy as np	
from datetime import datetime
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier
from sklearn.grid_search import GridSearchCV
from matplotlib import pyplot as plt

def get_data(file):
    df = pd.read_csv(file)
    data = df.as_matrix()
    np.random.shuffle(data)
    X = data[:, 1:] # data is from 0..255
    Y = data[:, 0]
    return X, Y


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


def plottami(X, Y):
    
    plt.hist(Y) #, histtype=‘step’)
    plt.show()

#### main ####
resize=1
findbest=0
dofit=0
predict=0
plot=1


del size
try: 
    size
except NameError:
    X, target = get_data('map_n_reads.txt')
    size=len(target)

if resize:  
    X_train, X_test, y_train, y_test = train_test_split(X, target, random_state=1, test_size=0.2)


if plot:
    plottami(X, target)


if findbest:
    n_est, maxf, crit, min_s_leaf = find_best()

else:
    n_est = 200 
    maxf = 'auto'
    crit = 'gini'
    min_s_leaf = 10


if dofit:        
    clf =  RandomForestClassifier(n_jobs=-1, max_features= maxf, n_estimators=n_est, 
                                  criterion = crit, min_samples_leaf = min_s_leaf, oob_score = True) 
    clf.fit(X_train,  y_train)
    
   
if predict:
    results = clf.predict(X_train) 
    score = metrics.accuracy_score(y_train,results)
    print("train:",score)

    results = clf.predict(X_test)
    score =  metrics.accuracy_score(y_test,results)
    print("test",score)


