#!/bin/bash

if [ $# -lt 1 ]; then
    echo; echo " align_bwa.sh: Some errors in your runalign.sh script!"
    exit
fi

project=$1
source $project/project.sh

mkdir -p $aldir
cd $aldir


subqueue="s#MYQUEUE#$myqueue#g"
submem="s#MYJOBMEM#$myjobmem#g"
subcpu="s#MYCPUS#$myncpus#g"

awkcommand=`echo '{print \$1, \$2, \$3, \$4, \$5, \$6, \$7, \$8, \$9, \$11, \$12, \$14}'`
# 4 == unmapped  256==secondary   0x900 == 0x800 (supplementary) + 0x100 (secondary) 
command=`echo "$mybwa mem -t $myncpus $draftdir/$(basename $mydraft) $myfastq1 $myfastq2 | samtools view -q 1 -F 4 -F 0x900 | grep -v XA:Z | grep -v SA:Z | awk '$awkcommand' > $alfile"`

echo $command > align.sh
chmod +x align.sh
 

if [[ $lfsjobs == 1 ]]; then
    sed $subqueue $myscripts/farm.sh | sed $submem | sed $subcpu > farm.sh
    chmod +x farm.sh
    njobs=`bjobs | wc -l`	   	

    while [ $njobs -ge $maxjobs ]; do
	echo "  Waiting for jobs to finish...sleeping zzz.."
       	sleep 30
	njobs=`bjobs | wc -l`
    done	   	    
    ./farm.sh align.sh
    sleep 1
else
    ./align.sh
fi

sleep 1
waitfor="align"
if [[ $lfsjobs == 1 ]]; then
    echo "   ...Waiting for all jobs to finish...sleeping zzz.."

    njobs=`bjobs | grep $waitfor | wc -l`
    echo $waitfor $njobs
    if [[ $njobs > 0 ]]; then
	while [ $njobs -ge 1 ]; do
	    sleep 30
	    njobs=`bjobs | grep $waitfor  | wc -l`
    	done
    	sleep 5
    fi
    sleep 60
fi

