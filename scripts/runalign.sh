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


######################################################
##################  ALIGN HI-C READS  ################
######################################################

already_there="Yes"
if [ ! -f  $alfile  ]; then 
    if [[ $aligner == "bwa" ]]; then
	already_there="No"
	$myscripts/align_bwa.sh $project 
    fi
fi

if [ -f  $alfile  ]; then 
    echo "  3. Created alignment file (Already there?" $already_there")"
    cd $aldir
    $mysrcs/map_reads/map_reads $alfile $draftdir/scaffolds_lenghts.txt
else
    echo "  Error: Something went wrong during bwa"
    echo "  (Already there?" $already_there")"
    exit 
fi

exit

if [ ! -f $file ]; then
    for ofile in $aldir/split_$firstal/*.out; do
	if [[ $aligner == "smalt" ]]; then
	    awk '{print $3"\t"$4"\t"$11"\t"$2"\t"20"\t"1"\t"$5"\t"$6"\t"$7"\t"$8"\t"0.0"\t"$12"\t"$9}' $ofile  >> $aldir/$firstal.al
	elif [[ $aligner == "minimap2" ]]; then
	    cat $ofile | awk '{print $1"\t"$6"\t"$12"\t"0"\t"0"\t"0"\t"$3"\t"$4"\t"$8"\t"$9"\t"0"\t"$11"\t"$5}'  | sed 's#\t+#\tF#g' | sed 's#\t-#\tR#g' >> $aldir/$firstal.al 	
	else # bwa
	    cat $ofile   >> $aldir/$firstal.bwatemp
	    $srcdir/als_frombwa/als_frombwa $aldir/$firstal.bwatemp

	    ## do somehing with $aldir/$firstal.bwatemp and get  $aldir/$firstal.al 	
	    
	fi
    done
fi
exit

checkfile=`$scriptdir/checkfile.sh $file $location`
err=`echo $checkfile | tail -1`
if [[ $err > 0 ]]; then  echo; echo "   " $checkfile; exit; fi
echo " 4. First alignment done! "
echo


#######################################################
### SECOND ALIGNMENT: ALL FORWARD, SHRED AND ALIGN  ###
#######################################################
### create fasta with all forward scaffold:
file=$fastadir/$forwnotshred; location="Five"
if [ ! -f  $file ]; then
    $scriptdir/allforw.sh $aldir/$firstal.al $forwnotshred 
fi
checkfile=`$scriptdir/checkfile.sh $file $location`
err=`echo $checkfile | tail -1`
if [[ $err > 0 ]]; then  echo; echo "   " $checkfile; exit; fi
echo " 5. All contigs/scaffolds forward now "
echo


### create shreded fasta from all_forward_fasta
file=$forwshred; location="Six"
if [ ! -f $file ]; then 
    $scriptdir/createshred.sh  $forwnotshred 
fi
checkfile=`$scriptdir/checkfile.sh $file $location`
err=`echo $checkfile | tail -1`
if [[ $err > 0 ]]; then echo; echo "   " $checkfile; exit; fi
echo " 6. Forward shreded draft assembly split in multiple fastas for faster alignment in parallel "
echo

### split shreded fasta in fasta of 1M contigs ###
file=$fastadir/splitforw/split0_$(basename $forwshred); location="Seven"
if [ ! -f  $file ]; then 
    if [[ $aligner == "smalt" ]]; then
	$scriptdir/splitshred.sh $fastadir/splitforw  $forwshred 
	#$scriptdir/splitshred.sh $fastadir/splitforw  $(basename $forwshred)  
    else
	$scriptdir/splitshred.sh  $fastadir/splitforw  $forwshred $splitlen
    fi
fi
checkfile=`$scriptdir/checkfile.sh $file $location`
err=`echo $checkfile | tail -1`
if [[ $err > 0 ]]; then echo; echo "   " $checkfile; exit; fi
echo " 7. Forward draft shreded "
echo
## align  fastas
file=$forwal; location="Eigth"
if [ ! -f  $aldir/split_$secal/split0_$secal.out  ]; then 
    if [[ $aligner == "smalt" ]]; then
	$scriptdir/splitalign.sh $fastadir/splitforw $secal 
    else
    	$scriptdir/splitalign_minimap.sh  $fastadir/splitforw $secal  #c not needed
    fi
fi

if [ ! -f $file ]; then
    for ofile in $aldir/split_$secal/*.out; do
	if [[ $aligner == "smalt" ]]; then
	    cat $ofile | sed 's#:# #g' | awk '{print $5"\t"$6"\t"$13"\t"$4"\t"22"\t"1"\t"$7"\t"$8"\t"$9"\t"$10"\t"0.0"\t"$14"\t"$3}' >> $forwal  ## need to check this
	    #awk '{print $3"\t"$4"\t"$11"\t"$2"\t"20"\t"1"\t"$5"\t"$6"\t"$7"\t"$8"\t"0.0"\t"$12}' $ofile >> $forwal
	else
	    cat $ofile | awk '{print $1"\t"$6"\t"$10*100/$11"\t"0"\t"0"\t"0"\t"$3"\t"$4"\t"$8"\t"$9"\t"0"\t"$11"\t"$12}' >>  $forwal
	fi
    done
fi

checkfile=`$scriptdir/checkfile.sh $file $location`
err=`echo $checkfile | tail -1`
if [[ $err > 0 ]]; then echo; echo "   " $checkfile; exit; fi
echo " 8. Second alignment done!"
echo
#######################################################
##################  FIX AL POSITIONS  #################
#######################################################


#######################################################
################ CREATE SINGLE FASTAS  ################
#######################################################
cd $thisdir
if [ ! -d $singlefolder ]; then
    $scriptdir/singlefasta.sh $fastadir/$forwnotshred  
fi
if [ ! -d $singlefolder ]; then
    echo; echo " Error! Single fasta folder not found in"  $singlefolder; exit
else
    check=`ls $singlefolder | wc -l`
    shouldbe=`$srcdir/n50/n50 $fastadir/$forwnotshred | awk '{print $4}'`
    if [ ! $check -eq $shouldbe ]; then 
	echo; echo " Error! too many or too few single fastas in" $singlefolder; exit
    fi
    # contig sizes file
    check=`wc -l $contigsizes | awk '{print $1}'`
    if [ ! $check -eq $shouldbe ]; then 
	echo; echo " Error! too many or too few contigs in" $contigsizes; exit
    fi
fi
echo " 9. Prepared draft contigs"
echo


#### fix positions of shred ctg/scaffold:  (only if not using Zemin tabs) [ it changes ctg names from ctg1_1, ctg1_100000, ... in ctg1,...]
file=$workdir/$thirdal.al; location="Ten"
if [ ! -f $workdir/$thirdal.al ]; then
    $scriptdir/fixpos.sh $forwshred $forwal $thirdal 
fi
checkfile=`$scriptdir/checkfile.sh $file $location`
err=`echo $checkfile | tail -1`
if [[ $err > 0 ]]; then echo; echo "   " $checkfile; exit; fi
echo " 10. Prepared draft contigs order and positions"
echo
echo "   "All done! You can now proceed with \" $ ./mypipeline.sh prepfiles \"
echo
