import numpy as np	
from datetime import datetime
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection  import GridSearchCV
from matplotlib import pyplot as plt
import  scikitplot as skplt

#tf = dfa.copy(deep=True)

import fileinput

def get_data(file, scaffold_min_length):
    dfa = pd.read_csv(file, sep=" ", header=None)
    return dfa

def get_subsample(tdf, scaffold_min_length):

    t = 2   # target
    nlinks = 5  # number of links

    # select only scaffolds longer than scaffold_min_length
    tdf = tdf[ (tdf[t+1] > scaffold_min_length) &  (tdf[t+2] > scaffold_min_length) ]
    # scaffold lengths
    #tdf[t+1] /= tdf[t+1][tdf[t+1].idxmax()]
    #tdf[t+2] /= tdf[t+2][tdf[t+2].idxmax()]

    # link positions
    #tdf.loc[:, nlinks+1:] = tdf.divide(tdf[5].T, axis='index')
    tdf.loc[:, nlinks+1:]        = tdf.loc[:, nlinks+1:].divide(tdf.values[:,nlinks], axis='index')  # norm by num_links
    #tdf[nlinks]
    #tdf[nlinks][tdf[nlinks].idxmax()]  #   norm by max links

    data = tdf.as_matrix()
    np.random.shuffle(data)
    x = data[:, t+1:]  
    y = list(data[:, t])
    z = data[:, nlinks] 
    
    return x, y, z, tdf


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
    return CV_rfc.best_estimator_.n_estimators, CV_rfc.best_estimator_.max_features, CV_rfc.best_estimator_.criterion, CV_rfc.best_estimator_.min_samples_leaf

def myfit(x, y):
    #print(maxf, n_est, crit, min_s_leaf)
   
    clf =  RandomForestClassifier(n_jobs=-1, max_features= maxf, n_estimators=n_est, class_weight='balanced',
                                  criterion = crit, min_samples_leaf = min_s_leaf, oob_score = True) 
    clf.fit(x, y)
    return(clf)



def plottami(x, y, z):
    
    same_chr = np.sum(y)
    print("  I have", len(y), "linked pair of scaffolds and:\n    ", 
          same_chr, "from the same chromosome (", same_chr*100./len(y), "%)")
    
    nlinks = np.sum(z)
    print("    ", nlinks, "total number of links")
       
    dfaname = dfa.rename(columns={ 2: 'target', 5: 'nlinks', 3 : 'len1', 4: 'len2'})

    dfa1n = df.groupby([2]).get_group(1)
    dfa0n = df.groupby([2]).get_group(0)
    dfa0nT = dfa0n.iloc[:,6:].T
    dfa1nT = dfa1n.iloc[:,6:].T

    fig, axes = plt.subplots(nrows=2, ncols=2)
    i=0
    j=0
    dfaname[['len1', 'len2']].plot.hist(ax=axes[i,j],  bins=100, title='Scaffold lengths',alpha=0.5, bottom=0.1); axes[i,j].set_yscale('log')
    j=1
    #dfaname[['nlinks']].plot(ax=axes[i,j],  kind='hist', title='Number of links');
    dfaname[['nlinks']].plot.hist(ax=axes[i,j], title='Number of links', bins=100, bottom=0.1); axes[i,j].set_yscale('log')

    i=1
    j=0
    dfaname.groupby('target')['nlinks'].mean().plot(ax=axes[i,j], kind='bar', yerr=dfaname.groupby('target')['nlinks'].std(), title='nlinks by target'); 
    j=1
 
    dfa1nT.mean(axis=1).plot(ax=axes[i,j], title='Mean links', label='target==1')
    dfa0nT.mean(axis=1).plot(ax=axes[i,j], title='Mean links', label='target==0')
    #axes[i,j].legend(["target==1", "target==0"]);
    j=4

    
    plt.show()



findbest=0
fit=0
info=1

fitX=0
fitZ=0
if fit:
    fitX=1
    fitZ=1

predictZ=1
predictX=1
if fitX == 0:
    predictX=0
if fitZ == 0:
    predictZ=0


     
### Get Data ###
try: 
    size
except NameError:    
    myfile='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/bothhic_fromscratch/bwa_temp/hicana/map_n_reads.txt'
    dfa = get_data(myfile, 500000)
    size=len(dfa[0])
    print("Input data read")
    

looppa=0
if looppa:
    
    try:
        del X, target, Z, df   
        del X_train, X_test, y_train, y_test
        del Z_train, Z_test, y_train, y_test, Z1
    except NameError: 
        if 0: print("niente")

    X, target, Z, df = get_subsample(dfa, 500000)


    test_perc=0.2
    X_train, X_test, y_train, y_test = train_test_split(X, target, random_state=1, test_size = test_perc)    
    Xclf =  myfit(X_train, y_train)
    esults = Xclf.predict(X_train) 
    score = metrics.accuracy_score(y_train,results)
    print("Using X: train:",score)
    skplt.metrics.plot_confusion_matrix(y_train, results, title="Confusion Matrix",
                                        normalize=False,figsize=(6,6),text_fontsize='large')



resize=0
if resize:  
    test_perc=0.2
    X_train, X_test, y_train, y_test = train_test_split(X, target, random_state=1, test_size = test_perc)
    
    Z1=Z.reshape(-1, 1) 
    Z_train, Z_test, y_train, y_test = train_test_split(Z1, target, random_state=1, test_size = test_perc)
    


### Print and Plot some Infos ###
if info:
    print("\n Some info from the sample:")
    plottami(X_test, y_test, Z_test)  #X, target, Z)
    print("\n")

        
        
    ### Fit n Predict ###

if findbest:
    n_est, maxf, crit, min_s_leaf = find_best(X_train, y_train)
                #{'criterion': 'gini', 'max_features': 'log2', 'min_samples_leaf': 10, 'n_estimators': 200}
                # tested on whole sample without scaff lengths
else:
    n_est = 200 
    maxf = 'log2'
    crit = 'gini'
    min_s_leaf = 10
    
if fitX:    
    Xclf =  myfit(X_train, y_train)
    print("Fit X done")
if fitZ:    
    Zclf =  myfit(Z_train, y_train)  
    print("Fit Z done")
    
if predictX:
    results = Xclf.predict(X_train) 
    score = metrics.accuracy_score(y_train,results)
    print("Using X: train:",score)
    
    results = Xclf.predict(X_test)
    score =  metrics.accuracy_score(y_test,results)
    print("Using X: test",score)
    skplt.metrics.plot_confusion_matrix(y_test, results, title="Confusion Matrix",
                                        normalize=False,figsize=(6,6),text_fontsize='large')
    plt.show()

if predictZ:
    results = Zclf.predict(Z_train) 
    score = metrics.accuracy_score(y_train,results)
    print("Using Z: train:",score)
    
    results = Zclf.predict(Z_test)
    score =  metrics.accuracy_score(y_test,results)
    print("Using Z: test",score)
    skplt.metrics.plot_confusion_matrix(y_test, results, title="Confusion Matrix",
                                        normalize=False,figsize=(6,6),text_fontsize='large')
    plt.show()
        

            


