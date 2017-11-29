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
    fi
	
    if [[ -f  $draftdir/$(basename $mydraft).bwt ]] ; then
	echo "  1. Draft Bwa indexing done  (Already there?" $already_there")"
    else
	echo "  Error: Something went wrong while indexing" $(basename $mydraft) in $draftdir
	echo "  (Already there?" $already_there")"
	exit
    fi
fi

already_there="Yes"
if [[ ! -f $draftdir/myn50.dat ]] || [[ ! -s $draftdir/myn50.dat ]] || [[ ! -s $draftdir/scaffolds_lenghts.txt ]]; then
    $mysrcs/n50/n50 $mydraft > $draftdir/myn50.dat
    already_there="No"
fi
if [[ -f $draftdir/myn50.dat ]] && [[ -s $draftdir/myn50.dat ]]; then
    echo "  2. Assembly Stats checked  (Already there?" $already_there")"
else
    echo "  Error: Something went wrong while checking" $(basename $mydraft) stats
    echo "  (Already there?" $already_there")"
    exit
fi


echo "  Step 1 Done: Draft assembly ready! "
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
    fi

    if [[ -f  $refdir/$(basename $myref).bwt ]] ; then
	echo "  1. Ref Bwa ref indexing done  (Already there?" $already_there")"
    else
	echo "  Error: Something went wrong while indexing" $(basename $myref) in $refdir
	echo "  (Already there?" $already_there")"
	exit
    fi
fi

already_there="Yes"
if [[ ! -f $refdir/myn50.dat ]] || [[ ! -s $refdir/myn50.dat ]] || [[ ! -s $refdir/scaffolds_lenghts.txt ]]; then
    $mysrcs/n50/n50 $myref > $refdir/myn50.dat
    already_there="No"
fi
if [[ -f $refdir/myn50.dat ]] && [[ -s $refdir/myn50.dat ]]; then
    echo "  2. Ref Stats checked  (Already there?" $already_there")"
else
    echo "  Error: Something went wrong while checking" $(basename $myref) stats
    echo "  (Already there?" $already_there")"
    exit
fi


echo "  Step 2 Done: Ref assembly ready! "
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

if [ -f  $refalfile ]; then 
    echo "  1. Alignment against Ref done (Already there?" $already_there")"
else
    echo "  Error: Something went wrong during bwa against ref"
    echo "  (Already there?" $already_there")"
    exit 
fi

#############################################################
##################  ALIGN HI-C READS TO DRAFT  ##############
#############################################################

already_there="Yes"
if [ ! -f  $alfile  ]; then 
    if [[ $aligner == "bwa" ]]; then
	already_there="No"
	$myscripts/align_bwa.sh $project draft
    fi
fi

if [ -f  $alfile  ]; then 
    echo "  2. Alignment against Draft done (Already there?" $already_there")"
else
    echo "  Error: Something went wrong during bwa against draft"
    echo "  (Already there?" $already_there")"
    exit 
fi

echo "  Step 3 Done: BWA mapping done! "
echo


#############################################################
#####################   HI-C ANALYSIS  ######################
#############################################################
mkdir -p $hicdir

already_there="Yes"
if [ ! -f  $hictochr  ] || [ ! -f $hictoscaff ]; then 
    cd $hicdir
    already_there="No"
    $mysrcs/map_reads/map_reads $refalfile $refdir/scaffolds_lenghts.txt  $alfile $draftdir/scaffolds_lenghts.txt 
    echo
fi

if [ ! -f  $hictochr  ] || [ ! -f $hictoscaff ]; then 
    echo "  Error: Something went wrong during map_reads"
    echo "  (Already there?" $already_there")"
    exit 
fi

exit
already_there="Yes"
if [ ! -f $sortedhictoscaff ]; then 
    cd $hicdir
    already_there="No"
    $mysrcs/sort_hiclinks/sort_hiclinks $hictoscaff $draftdir/scaffolds_lenghts.txt 

fi

if [ ! -f  $sortedhictoscaff  ]; then 
    echo "  Error: Something went wrong during sorting links"
    echo "  (Already there?" $already_there")"
    exit 
fi




echo "  Step 4 Done: HIC links found and sorted! "
echo
