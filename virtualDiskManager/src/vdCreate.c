#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

int main(int argc,char* argv[]){
	FILE *vdFile;
	unsigned long tSize; // the size of the virtual disk
	unsigned long metaSize; // the size of the metadata

	metaSize = 8 + 8 + 8 + 8 + 4;
	tSize = atoi(argv[2])*1024 + metaSize;

	vdFile = fopen(argv[1],"wb+");

	ftruncate(fileno(vdFile),tSize);

	fwrite(&metaSize,sizeof(metaSize),1,vdFile); // set the metadata size
	fwrite(&tSize,sizeof(tSize),1,vdFile); // set the size of the file
	fwrite(&tSize,sizeof(tSize),1,vdFile); // the pointer for next available free space
	fwrite(&metaSize,sizeof(tSize),1,vdFile); // the pointer for end of the pointer space

}
