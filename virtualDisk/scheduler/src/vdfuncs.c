#include"../headers/vdfuncs.h"

void readBlock(FILE* vdFile,unsigned char** block,unsigned int blockSize,unsigned int blockNumber){
	fseek(vdFile,blockNumber*blockSize,SEEK_SET);
	fread(*block,blockSize,1,vdFile);
}

void writeBlock(FILE* vdFile,unsigned char** block,unsigned int blockSize,unsigned int blockNumber){
	//printf("Writing to block Number : %d\n",blockNumber);
	fseek(vdFile,blockNumber*blockSize,SEEK_SET);
	fwrite(*block,blockSize,1,vdFile);
}
