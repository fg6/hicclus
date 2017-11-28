#include <iomanip>  //setprecision
#include <algorithm>    // sort, reverse
#include <gzstream.h>
#include <vector>  //setprecision
#include <tuple> // C++11, for std::tie
#include <numeric> // accumulate
#include <zlib.h>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <map>
#include <tuple> // C++11, for std::tie


using std::cout;
using std::endl;
using std::vector;
using std::string;

static  vector<int> seqpos;
static  vector<string> seqname;

static  std::ofstream myals;
static gzFile fp;

static  std::map<string, long int> lenmap;
static  std::map<string, long int> refmap;
static  std::map<string, long int>  samechr_map;
static  std::map<string, long int>  samescaff_map;
//static  std::map<string, std::tuple<string,long int, string, long int, long int, long int, long int >> samechr_map;

int read_refals(char* file);
int read_draftals(char* file);
std::map<string, long int> readscaff(char* file);
int read_hicmap(string file);


static int step2=0;

int main(int argc, char *argv[])
{   
  if (argc < 5 ) {
    fprintf(stderr, "Usage: %s  <ref_alignments> <chr_lengths> <alignments> <scaffolds_lengths>  \n", argv[0]);   
    return 1;
  }	
  for (int i=0; i<argc; i++){
    if((fp = gzopen(argv[i],"r")) == NULL){ 
      cout << " ERROR main:: missing input file " << i << " !! " << endl;
      return 1;
    }
    gzclose(fp);
  }
  
  //Read Chr lengths
  fp = gzopen(argv[4],"r");
  lenmap=readscaff(argv[4]);
  cout << "  Read Chr lengths " << endl;

  //Read Scaffold lengths
  fp = gzopen(argv[2],"r");
  refmap=readscaff(argv[2]);
  cout << "  Read Scaffolds lengths " << endl;


  // Map HiC reads to Ref and get samechr_map
  string myname = "hic_to_chr.als";
  if((fp = gzopen(myname.c_str(),"r")) == NULL){ 
    myals.open(myname.c_str()); 
    read_refals(argv[1]);
    myals.close();
    cout <<  " Chr-Map Created and file written" << endl;
  }else{ // hic_to_chr.als file already there! Read that only (it's faster!)
    read_hicmap(myname);
    cout <<  "  Chr-Map Created" << endl;
  }



  // Map HiC reads to Draft
  myname = "hic_to_scaff.als";
  myals.open(myname.c_str()); 
  read_draftals(argv[3]);
  myals.close();


  return 0;
}

int read_draftals(char* file){
  std::ifstream infile(file);
  string line;

  int readnum=0, sscaffnum=0, schrnum=0;
  int not_found_in_chr=0;
  int same_chr_diff_scaff = 0;

  while(getline(infile,line)){
        std::stringstream ss(line);
        string read, scaffold, cigar, mate;
	int flag, mapq;
	long int pos, mate_pos, insert;
	int same_scaff=0;

        ss >> read >> flag >> scaffold >> pos 
	   >> mapq >> cigar >> mate >> mate_pos >> insert;
	
	readnum++;

	if( samescaff_map.count(read) ) continue;
	if( !samechr_map.count(read) ) {
	  //cout << " Warning! read " << read << " not found in the Ref read-map, was it unmapped?" << endl;
	  not_found_in_chr++;
	  continue;
	}

	if ( mate == "=" ){
	  mate = scaffold;
	  same_scaff=1;
	  sscaffnum++;
	}else{
	  //if(samechr_map[read]) 
	  same_chr_diff_scaff++;
	}
	
	schrnum+=samechr_map[read];

       

	// filter on flag and mapq?
	samescaff_map[read] = same_scaff;
	  
	myals << read << " " << scaffold << " " <<  pos << " " 
	      << mate<< " " << mate_pos<< " " << insert << " " 
	      << same_scaff << " " << samechr_map[read] << endl; 
  }

  cout << " Mapping done, I found: " 
       << readnum << " reads, " << not_found_in_chr << " reads which were not mapped to the Ref, \n"
       << "  " << schrnum << " mapping to the same chromosome (" <<  schrnum*100./readnum <<  "%) \n"
       << "  " << sscaffnum << " mapped to the same scaffold (" <<  sscaffnum*100./readnum <<  "%) \n"
       << "  " << same_chr_diff_scaff << " mapped to same chr but different scaffolds (" <<  same_chr_diff_scaff*100./readnum <<  "%)"
       << endl;
}


std::map<string, long int>  readscaff(char* file){
  std::ifstream infile(file);
  string line;
  std::map<string, long int> tempmap;

  while(getline(infile,line)){
    std::stringstream ss(line);
    string scaff;
    long int length;
    ss >> scaff >> length;
    tempmap[scaff] = length;
  }
  return tempmap;
}

int read_hicmap(string file){  
  std::ifstream infile(file.c_str());
  string line;

  while(getline(infile,line)){
    std::stringstream ss(line);
    string read, scaffold, cigar, mate;
    int flag, mapq;
    long int pos, mate_pos, insert;
    int same_scaff;
    ss >> read >> scaffold >> pos >>
      mate >> mate_pos >> insert >> same_scaff ;

    if ( scaffold == mate )  same_scaff =1; // take this out when rerunning
    samechr_map[read] = same_scaff;
  }
 
  return 0;
}




int read_refals(char* file){
  std::ifstream infile(file);
  string line;

  while(getline(infile,line)){
        std::stringstream ss(line);
        string read, scaffold, cigar, mate;
	int flag, mapq;
	long int pos, mate_pos, insert;
	int same_scaff=0;

        ss >> read >> flag >> scaffold >> pos 
	   >> mapq >> cigar >> mate >> mate_pos >> insert;

	if( samechr_map.count(read) ) continue;
	
	if ( mate == "=" ){
	  mate = scaffold;
	  same_scaff=1;
	}
	
	// filter on flag and mapq?
	//std::tuple<string,long int, string, long int, long int, long int, long int > 
	// thistuple=std::make_tuple(scaffold, pos, mate, mate_pos, insert, lenmap[scaffold], lenmap[mate]);
	
	samechr_map[read] = same_scaff;
 
	  
	myals << read << " " << scaffold << " " <<  pos << " " 
	      << mate<< " " << mate_pos<< " " << insert << " " << same_scaff << endl; 
	

  }
}

