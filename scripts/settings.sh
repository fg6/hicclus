#### Parameters to set: ####
aligner=bwa
debug=1

# lfs jobs parameters:
lfsjobs=1  
myqueue=normal
maxjobs=50  #maximum number of jobs to run at a time
myjobmem=5000
myncpus=15

########################
mymain=MYMAIN
myref=MYREF
mydraft=MYDRAFT
myfastq1=MYFQ1
myfastq2=MYFQ2
project=MYDESTDIR

myscripts=$mymain/scripts
mysrcs=$mymain/src
mybin=$mymain/bin

# Aligner
mybwa=$mybin/bwa
wdir=$project/$aligner\_temp
draftdir=$wdir/draft
refdir=$wdir/ref
refaldir=$wdir/refalign
refalfile=$refaldir/bwa.sam
aldir=$wdir/align
alfile=$aldir/bwa.sam

hicdir=$wdir/hicana
hictochr=$hicdir/hic_to_chr.als
hictoscaff=$hicdir/hic_to_scaff.als
sortedhictoscaff=$hicdir/hic_to_scaff_sorted.als


