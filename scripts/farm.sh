#!/bin/bash

# farm settings
ncpus=MYCPUS
nmem=MYJOBMEM 
queue=MYQUEUE

odir=.
mybin=$odir/$1
chmod +x $mybin


# farm settings
hh=1 # hosts
outd=$odir/outs
errd=$outd
tname="align"   #${mybin%.*}
jname=${tname##*_}
 
if [ ! -f $mybin ] ; then
 echo “Sorry binary not available”
 exit 1
fi
mkdir -p $outd $errd
bsub -q $queue -J split$jname -o $outd/out.%J -e $errd/errout.%J -n$ncpus -R"span[ptile=$ncpus] select[mem>$nmem] rusage[mem=$nmem]" -M$nmem  $mybin
