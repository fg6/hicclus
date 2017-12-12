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

import matplotlib.pyplot as plt

#tf = dfa.copy(deep=True)

import fileinput

class of(float):
    def __str__(self):
        return "%0.1f" % self.real

class zf(float):
    def __str__(self):
        return "%0.0f" % self.real

class tf(float):
    def __str__(self):
        return "%0.2f" % self.real

t = 2   # target
nlinks = 5  # number of links

def get_data(file):
    print("Getting data")
    dfa = pd.read_csv(file, sep=" ", header=None)
    dfa.sample(frac=1) #shuffle rows, return all rows
    dfn = dfa.copy(deep=True)

    dfn.loc[:, nlinks+1:]  = dfn.loc[:, nlinks+1:].divide(dfn.values[:,nlinks], axis='index')  # norm by num_links
    return dfa, dfn


def get_subdf(tdf, scaffold_min_length):
    
    print("Getting subsample", scaffold_min_length)
    tdf = tdf[ (tdf[t+1] > scaffold_min_length) &  (tdf[t+2] > scaffold_min_length) ]
    return tdf

def get_subsample(tdf):
    data = tdf.as_matrix()
    #np.random.shuffle(data)
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



def plottami():    
      
    dfaname = dfa.rename(columns={ 2: 'target', 5: 'nlinks', 3 : 'len1', 4: 'len2'})

    dfa1n = dfn.groupby([2]).get_group(1)
    dfa0n = dfn.groupby([2]).get_group(0)
    dfa0nT = dfa0n.iloc[:,6:].T
    dfa1nT = dfa1n.iloc[:,6:].T

    fig, axes = plt.subplots(nrows=2, ncols=2)
    i=0
    j=0
    dfaname[['len1', 'len2']].plot.hist(ax=axes[i,j],  bins=100, title='Scaffold lengths',alpha=0.5, bottom=0.1); axes[i,j].set_yscale('log')
    j=1
    dfaname[['nlinks']].plot.hist(ax=axes[i,j], title='Number of links', bins=100, bottom=0.1); axes[i,j].set_yscale('log')

    i=1
    j=0
    dfaname.groupby('target')['nlinks'].mean().plot(ax=axes[i,j], kind='bar', yerr=dfaname.groupby('target')['nlinks'].std(), title='nlinks by target'); 
    j=1
 
    dfa1nT.mean(axis=1).plot(ax=axes[i,j], title='Mean links', label='target==1')
    dfa0nT.mean(axis=1).plot(ax=axes[i,j], title='Mean links', label='target==0')
    j=4

    
    plt.show()





#### main ####
info=1

fitX=0
predictX=1
if fitX == 0:
    predictX=0

     
### Get Data ###
try: 
    size
except NameError:    
    myfile='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/bothhic_fromscratch/bwa_temp/hicana/map_n_reads.txt'
    dfa, dfn = get_data(myfile)
    size=len(dfa[0])
    print("Input data read")
    

looppa=1
if looppa:

    #sizes=[100000, 500000, 1000000, 2000000]
    #si=['100k','500k','1M','2M']

    sizes=[1]
    si=['all']

    # create the dicts if not there already:
    try: 
        if mydfs.keys(): 
            if len(sizes) is not len(mydfs.keys()):
                   print ("  Warning: mydfs has less dfs than the list of sizes!")
    except NameError:    
        mydfs = {}
        for i,min_size in enumerate(sizes):
        
            if min_size == 1:
                idf = dfn.copy(deep=True)
            else:
                idf = get_subdf(dfn, min_size)
            
            thisdf= 'df'+str(si[i])
            mydfs[thisdf] = idf.copy(deep=True)
            
    

    scores = {}
    for key in mydfs:
        
        print("  ",key)
        kdf = mydfs[key]


        # need this to really run the loop on multiple sizes:
        #try:
        #    del X, target, Z
        #    del X_train, X_test, y_train, y_test
        #    del Z_train, Z_test, zy_train, zy_test
        #except NameError: 
        #    if 0: print("niente")

        # Get data in arrays:
        try:
            if 0: print(len(target))
        except NameError:     
            X, target, Z = get_subsample(kdf)
       
        ### Print and Plot some Infos ###
        if info:
           
            # these numbers from map_reads.cpp
            nreads=126352766
            read_pairs=nreads/2
            chrunmapped=5170033  #read-pair (at least one read)
            same_chr=55382706
            same_scaffold=48360028  # of total
            samechr_diffscaf=7681295 
            million=1000000


 
            print("\n  Total number of read-pairs mapped:", zf((read_pairs - chrunmapped)/million), "M"
                  "\n  Both reads mapped to the same chr:", zf(same_chr/million), "M, or", of(same_chr*100/read_pairs), "%",
                  "\n  Both reads mapped to a different scaffold:", 
                  zf((read_pairs-same_scaffold)/million), "M, or", of((read_pairs-same_scaffold)*100/read_pairs), "%",
                  "\n  Read-pair from same chr mapped to different scaffolds:", zf(samechr_diffscaf/million),
                  "M, or", of(samechr_diffscaf*100/read_pairs), "%")

            
            links_same_chr = np.sum(target)
            print("\n  Number of links:", zf(Z.sum()/million), "M", 
                  "\n  Scaffold pairs from same chr:", links_same_chr, "or", of(links_same_chr*100./len(target)), "%")
            

            
            numbers = [(read_pairs - chrunmapped), same_chr, samechr_diffscaf ]
            N = 1
            ind = np.arange(N)
            width = 1   
            p3 = plt.bar(ind, numbers[2], width)
            p2 = plt.bar(ind, numbers[1], width, bottom=numbers[2])
            p1 = plt.bar(ind, numbers[0], width, bottom=numbers[1])
            plt.legend((p1[0], p2[0], p3[0]), ('Read-Pairs', 'On Same-Chr', 'On Diff Scaffolds'))
            #plt.show()


            #plottami()
            print("\n")


        if fitX:    
            # Resize:
            test_perc=0.2
            X_train, X_test, y_train, y_test, Z_train, Z_test, zy_train, zy_test = resize(test_perc)

            n_est = 200 
            maxf = 'log2'
            crit = 'gini'
            min_s_leaf = 10


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
            
            results = xclf.predict(X_test) 
            score = metrics.accuracy_score(y_test,results)
            conmat = cm(y_test, results)
            pos_ok = conmat[1][1]
            neg_ok = conmat[0][0]
            false_pos = conmat[0][1]
            false_neg = conmat[1][0]
            print(key, "Pos_ok:", pos_ok, "Neg_ok:", neg_ok, 
                  "False_pos:", false_pos, "False Neg:", false_neg, 
                  "Score=", score)

            #skplt.metrics.plot_confusion_matrix(y_test, results, title="Confusion Matrix",
            #                                    normalize=False,figsize=(6,6),text_fontsize='large')
            #plt.show()
        


        
     
    
            


