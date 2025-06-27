#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include"../headers/define/all.h"

int main(int argc,char* argv[]){
	FILE *vdFile;
	unsigned long tSize; // the size of the virtual disk
	unsigned long metaSize; // the size of the metadata

	tSize = atoi(argv[2])*1024 + METADATA_SIZE;

	vdFile = fopen(argv[1],"wb+");

	ftruncate(fileno(vdFile),tSize);

	fwrite(&tSize,sizeof(tSize),1,vdFile); // set the size of the file
	fwrite(&tSize,sizeof(tSize),1,vdFile); // the pointer for next available free space
	metaSize = METADATA_SIZE;
	fwrite(&metaSize,sizeof(tSize),1,vdFile); // the pointer for end of the pointer space
}
