#!/bin/bash


mymain=$1
myref=$2
mydraft=$3
myfastq1=$4
myfastq2=$5
project=$6

if [ $# -lt 6 ]; then
    echo; echo " Something wrong in your setup.sh script!"
    exit
fi

myscripts=$mymain/scripts
mysrcs=$mymain/src
mybin=$mymain/bin

mkdir -p $project
mkdir -p $project/history

sub1="s#MYMAIN#$mymain#g"
sub2="s#MYREF#$myref#g"
sub3="s#MYDRAFT#$mydraft#g"
sub4="s#MYFQ1#$myfastq1#g"
sub5="s#MYFQ2#$myfastq2#g"
sub6="s#MYDESTDIR#$project#g"

sed $sub1 $myscripts/settings.sh | sed $sub2 | sed $sub3 | sed $sub4 | sed $sub5  | sed $sub6 > $project/project.sh
cp $myscripts/launch.sh $project/launch.sh


# Saving setup information
setup_time=`date | awk '{print $6$2$3"_"$4}' | sed 's#:#.#g'`
echo $mymain/launchme.sh setup $2 $3 $4 $5 $6  > $project/history/$setup_time.txt
rm -f $project/setupas.txt
ln -sf $project/history/$setup_time.txt $project/setupas.txt



chmod +x $project/*.sh
echo; echo  " Your new project is set in folder: " $project
echo " Modify relevant paramters in " $project/project.sh
