#!/bin/bash



if [ $# -lt 1 ]; then
    echo; echo " runalign.sh: Some errors in your pipeline.sh script!"
    exit
fi

project=$1
source $project/project.sh

mkdir -p  $wdir
cd $wdir

#######################################################
#################   PREPARE DRAFT    ##################
#######################################################
mkdir -p $draftdir
cd $draftdir

if [[ $aligner == "bwa" ]]; then	
    
    already_there="Yes"
    if [[ ! -f  $draftdir/$(basename $mydraft).bwt ]] ; then

	if [[ -f $mydraft.bwt ]] ; then
	    cd $draftdir
	    ln -sf $mydraft.* .
	else
	    cd $draftdir
	    ln -sf $mydraft .
	    already_there="No"
	    
	    command=`$mybwa index $(basename $mydraft)`
	    if [[ $debug == 1 ]]; then
		$command
	    else
		$command &> /dev/null
	    fi
	fi
	
	if [[ -f  $draftdir/$(basename $mydraft).bwt ]] ; then
	    echo "  1. Bwa indexing done  (Already there?" $already_there")"
	else
	    echo "  Error: Something went wrong while indexing" $(basename $mydraft) in $draftdir
	    echo "  (Already there?" $already_there")"
	    exit
	fi
    fi
fi

already_there="Yes"
if [[ ! -f $draftdir/myn50.dat ]] || [[ ! -s $draftdir/myn50.dat ]] || [[ ! -s $draftdir/scaffolds_lenghts.txt ]]; then
    $mysrcs/n50/n50 $mydraft > $draftdir/myn50.dat
    already_there="No"
fi
if [[ -f $draftdir/myn50.dat ]] && [[ -s $draftdir/myn50.dat ]]; then
    echo "  2. Assembly stats checked  (Already there?" $already_there")"
else
    echo "  Error: Something went wrong while checking" $(basename $mydraft) stats
    echo "  (Already there?" $already_there")"
    exit
fi


echo "  Step 1 Done: draft assembly ready! "
echo


#######################################################
#################   PREPARE REF    ##################
#######################################################
mkdir -p $refdir
cd $refdir

if [[ $aligner == "bwa" ]]; then	
    
    already_there="Yes"
    if [[ ! -f  $refdir/$(basename $myref).bwt ]] ; then

	if [[ -f $myref.bwt ]] ; then
	    cd $refdir
	    ln -sf $myref.* .
	else
	    cd $refdir
	    ln -sf $myref .
	    already_there="No"
	    
	    command=`$mybwa index $(basename $myref)`
	    if [[ $debug == 1 ]]; then
		$command
	    else
		$command &> /dev/null
	    fi
	fi
	
	if [[ -f  $refdir/$(basename $myref).bwt ]] ; then
	    echo "  2. Bwa ref indexing done  (Already there?" $already_there")"
	else
	    echo "  Error: Something went wrong while indexing" $(basename $myref) in $refdir
	    echo "  (Already there?" $already_there")"
	    exit
	fi
    fi
fi

already_there="Yes"
if [[ ! -f $refdir/myn50.dat ]] || [[ ! -s $refdir/myn50.dat ]] || [[ ! -s $refdir/scaffolds_lenghts.txt ]]; then
    $mysrcs/n50/n50 $myref > $refdir/myn50.dat
    already_there="No"
fi
if [[ -f $refdir/myn50.dat ]] && [[ -s $refdir/myn50.dat ]]; then
    echo "  3. Ref  stats checked  (Already there?" $already_there")"
else
    echo "  Error: Something went wrong while checking" $(basename $myref) stats
    echo "  (Already there?" $already_there")"
    exit
fi


echo "  Step 2 Done: ref assembly ready! "
echo

#############################################################
##################  ALIGN HI-C READS TO REF  ################
#############################################################

already_there="Yes"
if [ ! -f  $refalfile  ]; then 
    if [[ $aligner == "bwa" ]]; then
	already_there="No"
	$myscripts/align_bwa.sh $project ref
    fi
fi

if [ -f  $refalfile ] && [ ! -f $refaldir/paired_hic_reads.als ]; then 
    echo "  4. Created ref alignment file (Already there?" $already_there")"
    cd $refaldir
    $mysrcs/map_reads/map_reads $refalfile $refdir/scaffolds_lenghts.txt
else
    echo "  Error: Something went wrong during bwa"
    echo "  (Already there?" $already_there")"
    exit 
fi

#############################################################
##################  ALIGN HI-C READS TO DRAFT  ################
#############################################################

already_there="Yes"
if [ ! -f  $alfile  ]; then 
    if [[ $aligner == "bwa" ]]; then
	already_there="No"
	$myscripts/align_bwa.sh $project draft
    fi
fi

exit

# here need to have new map_reads.cpp that takes draft alignment and ref alignment and create vectors 
if [ -f  $alfile  ] && [ ! -f $aldir/paired_hic_reads.als ]; then 
    echo "  5. Created draft alignment file (Already there?" $already_there")"
    cd $aldir
#    $mysrcs/map_reads/map_reads $alfile $draftdir/scaffolds_lenghts.txt
else
    echo "  Error: Something went wrong during bwa"
    echo "  (Already there?" $already_there")"
    exit 
fi


