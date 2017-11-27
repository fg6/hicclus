

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

np.random.seed(19680801)
N = 100
x = np.random.rand(N)
y = np.random.rand(N)
colors = np.random.rand(N)
area = 2 #np.pi * (15 * np.random.rand(N))**2  

scaffolds='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/refhicclus/bwa_temp/draft/scaffolds_lenghts.txt'
als='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/refhicclus/bwa_temp/aligns/paired_hic_reads.als'
als='/lustre/scratch117/sciops/team117/hpag/fg6/analysis/Devel/mouse/refhicclus/bwa_temp/aligns/test1'

df = pd.read_csv(scaffolds, sep=" ", names =  ['Scaffold', 'Lenght'], header=None)
df.columns = ['Scaffold', 'Lenght']
genome_lenght= df['Lenght'].sum()

scaff_pos0={}

start=0
for index, row in df.iterrows():
    scaff_pos0[row.Scaffold] = start
    start+=row.Lenght

x=[]
y=[]
with open(als, "r") as r:
    for line in r:
        read, chr1, pos1, chr2, pos2, insert, l1, l2 = line.split(' ')[:8]        
        x.append(int(pos1) + scaff_pos0[chr1])
        y.append(int(pos2) + scaff_pos0[chr2])
        

plt.scatter(x, y, s=area ) #, c=colors, alpha=0.5)
s=0
plt.axvline(x=s)
plt.axhline(y=s)
for xc in df.Lenght:
    plt.axvline(x=xc+s)
    plt.axhline(y=xc+s)

    s+=xc
plt.show()

