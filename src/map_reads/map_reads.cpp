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
static  string myname = "paired_hic_reads.als";
static gzFile fp;

static  std::map<string, long int> lenmap;
static  std::map<string, std::tuple<string,long int, string, long int, long int, long int, long int >> alsmap;

int readals(char* file);
int readscaff(char* file);

int main(int argc, char *argv[])
{ 
  
  if (argc == 1) {
   fprintf(stderr, "Usage: %s  <alignments> <scaffolds_length> \n", argv[0]);   
   return 1;
  }	
  if((fp = gzopen(argv[1],"r")) == NULL){ 
    printf("ERROR main:: missing input file 1 !! \n");
    return 1;
  }
  gzclose(fp);
  if((fp = gzopen(argv[2],"r")) == NULL){ 
    printf("ERROR main:: missing input file 1 !! \n");
    return 1;
  }
  gzclose(fp);

  string alfile = argv[1];

   
  //scaffolds lengths
  fp = gzopen(argv[2],"r");
  readscaff(argv[2]);
  
  myals.open(myname.c_str()); // written in readals
  readals(argv[1]);
  myals.close();
   
  return 0;
}

int readscaff(char* file){
  std::ifstream infile(file);
  string line;

  while(getline(infile,line)){
    std::stringstream ss(line);
    string scaff;
    long int length;
    ss >> scaff >> length;
    lenmap[scaff] = length;

  }
}


int readals(char* file){
  std::ifstream infile(file);
  string line;


  string prevctg="";
  string prevchr="";

  while(getline(infile,line)){
        std::stringstream ss(line);
        string read, scaffold, cigar, mate;
	int flag, pos, mapq, mate_pos, insert;

        ss >> read >> flag >> scaffold >> pos 
	   >> mapq >> cigar >> mate >> mate_pos >> insert;

	if( alsmap.count(read) ) continue;

	if ( mate == "=" )
	  mate = scaffold;
	
	// filter on flag and mapq?
	std::tuple<string,long int, string, long int, long int, long int, long int > 
	  thistuple=std::make_tuple(scaffold, pos, mate, mate_pos, insert, lenmap[scaffold], lenmap[mate]);
       	if( !alsmap.count(read) ) {
	  alsmap[read] = thistuple;
	  
	  myals << read << " " << scaffold << " " <<  pos << " " 
		<< mate<< " " << mate_pos<< " " << insert << endl; //<< " " << lenmap[scaffold]<< " " << lenmap[mate] << endl;
	}

  }
}

