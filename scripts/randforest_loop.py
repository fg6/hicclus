import numpy as np	
from datetime import datetime
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection  import GridSearchCV
from matplotlib import pyplot as plt
import  scikitplot as skplt
from sklearn.metrics import confusion_matrix as cm

#tf = dfa.copy(deep=True)

import fileinput


t = 2   # target
nlinks = 5  # number of links

def get_data(file, scaffold_min_length):
    print("Getting data")
    dfa = pd.read_csv(file, sep=" ", header=None)
    dfn = dfa.copy(deep=True)

    dfn.loc[:, nlinks+1:]  = dfn.loc[:, nlinks+1:].divide(dfn.values[:,nlinks], axis='index')  # norm by num_links
    #dfn[t+1] /= dfn[t+1][dfn[t+1].idxmax()]
    #dfn[t+2] /= dfn[t+2][dfn[t+2].idxmax()]

    return dfa, dfn




def get_subdf(tdf, scaffold_min_length):
    
    print("Getting subsample", scaffold_min_length)
    tdf = tdf[ (tdf[t+1] > scaffold_min_length) &  (tdf[t+2] > scaffold_min_length) ]


    #print(tdf.head())
    return tdf

def get_subsample(tdf):
    #print("Get data as arrays")
    data = tdf.as_matrix()
    np.random.shuffle(data)
    x = data[:, t+1:]  
    y = list(data[:, t])
    z = data[:, nlinks] 
    
    return x, y, z

def myfit(x, y):
    clf =  RandomForestClassifier(n_jobs=-1, max_features= maxf, n_estimators=n_est, class_weight='balanced',
                                  criterion = crit, min_samples_leaf = min_s_leaf, oob_score = True) 
    clf.fit(x, y)
    return(clf)

def resize(test_perc):
    X_train, X_test, y_train, y_test = train_test_split(X, target, random_state=1, test_size = test_perc)   
    Z1=Z.reshape(-1, 1) 
    Z_train, Z_test, zy_train, zy_test = train_test_split(Z1, target, random_state=1, test_size = test_perc)
     
    return X_train, X_test, y_train, y_test, Z_train, Z_test, zy_train, zy_test


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




fit=0
info=0

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
    dfa, dfn = get_data(myfile, 500000)
    size=len(dfa[0])
    print("Input data read")
    

looppa=1
if looppa:

    sizes=[100000, 500000, 1000000, 2000000]
    si=['100k','500k','1M','2M']

    #sizes=[1000000]
    #si=['1M']

    # create the dicts if not there already:
    try: 
        if mydfs.keys(): 
            #print(" No Need to recreate the dict, dfs already there!")
            if len(sizes) is not len(mydfs.keys()):
                   print ("  Warning: mydfs has less dfs than the list of sizes!")
    except NameError:    
        mydfs = {}
        for i,min_size in enumerate(sizes):
        
            idf = get_subdf(dfn, min_size)
            
            thisdf= 'df'+str(si[i])
            mydfs[thisdf] = idf.copy(deep=True)
            
    

    scores = {}
    for key in mydfs:
        
        print("  ",key)
        kdf = mydfs[key]
        try:
            del X, target, Z
            del X_train, X_test, y_train, y_test
            del Z_train, Z_test, zy_train, zy_test
        except NameError: 
            if 0: print("niente")

        # Get data in arrays:
        X, target, Z = get_subsample(kdf)
        # Resize:
        test_perc=0.2
        X_train, X_test, y_train, y_test, Z_train, Z_test, zy_train, zy_test = resize(test_perc)

        xclf =  myfit(X_train, y_train)
        results = xclf.predict(X_train) 
        
        score = metrics.accuracy_score(y_train,results)
        conmat = cm(y_train, results)
        pos_ok = conmat[1][1]
        neg_ok = conmat[0][0]
        false_pos = conmat[0][1]
        false_neg = conmat[1][0]
        print(key, "Pos_ok:", pos_ok, "Neg_ok:", neg_ok, 
              "False_pos:", false_pos, "False Neg:", false_neg, 
              "Score=", score)

        

        #skplt.metrics.plot_confusion_matrix(y_train, results, title="Confusion Matrix",
        #                                normalize=False,figsize=(6,6),text_fontsize='large')




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
        

            


