#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<stdbool.h>
#include<errno.h>
#include"../headers/miscFunc.h"
#include"../headers/dec.h"

int decodeFile(unsigned char* iFilePath,unsigned char* oFilePath){
	unsigned char* sseq;
	FILE *ifile,*ofile;
	unsigned char buffer[4096];
	unsigned long sseqLen,sizeOFile;
	unsigned short bytesRead;

	ifile = fopen(iFilePath,"rb");
	if(ifile == NULL){
		perror("Input File could not be opened : ");
		return errno;
	}
	ofile = fopen(oFilePath,"wb");
	if(ofile == NULL){
		perror("Output File could not be opened : ");
		return errno;
	}

	//sseqLen = getFileSize(ifile);
	sseqLen = 32; // assumption that the total size of the file is found within the first 32 bytes of the file

	sseq = (unsigned char*)malloc(sseqLen);
	fread(sseq,sseqLen,1,ifile);

	sizeOFile = decode(sseq,sseqLen);

	fseek(ifile,getFileSize(ifile)-sizeOFile,SEEK_SET);

	while(sizeOFile){
		bytesRead = fread(buffer,sizeof(char),4096,ifile);
		sizeOFile -= bytesRead;
		fwrite(buffer,sizeof(char),bytesRead,ofile);
	}
}


decodedData decode1(unsigned char* sseq,unsigned long sseqLen){
	unsigned char byte;
	unsigned long currentRead;
	unsigned long current;
	unsigned char bitsLeft;
	unsigned long i = 0;
	unsigned char minval;
	decodedData output;

	byte = sseq[0];
	bitsLeft = 8;
	currentRead = 2;
	current = 0;

	while(i < sseqLen){
		minval = MIN(currentRead,bitsLeft);
		writeFromRight(&current,&byte,&currentRead,&bitsLeft,minval);
		//printf("I : %d\n",i);
		//printBinary(sseq[i]);
		//printf("\n");
		if(bitsLeft == 0){
			i++;
			byte = sseq[i];
			bitsLeft = 8;
		}
		if(currentRead == 0){
			currentRead = current;
			current = 0;
			if(readFromLeft(byte,1) == 0){
				output.bytesRead = i+1;
				i = sseqLen;
			}
		}
	}

	output.length = currentRead;
	//output.bytesRead = i+1;
	return output;
}


unsigned long decode(unsigned char* sseq,unsigned long sseqLen){
	unsigned char byte;
	unsigned long currentRead;
	unsigned long current;
	unsigned char bitsLeft;
	unsigned long i = 0;
	unsigned char minval;

	byte = sseq[0];
	bitsLeft = 8;
	currentRead = 2;
	current = 0;

	while(i < sseqLen){
		minval = MIN(currentRead,bitsLeft);
		writeFromRight(&current,&byte,&currentRead,&bitsLeft,minval);

		if(bitsLeft == 0){
			i++;
			byte = sseq[i];
			bitsLeft = 8;
		}
		if(currentRead == 0){
			currentRead = current;
			current = 0;
			if(readFromLeft(byte,1) == 0){
				i = sseqLen;
			}
		}
	}

	return currentRead;
}

void writeFromRight(unsigned long *current,unsigned char *byte,unsigned long* currentRead,unsigned char *bitsLeft,unsigned char bitsToWrite){
	for(unsigned int i = 0; i < bitsToWrite;i++){
		*current = (*current) << 1;
		if((*byte) & 128) (*current) += 1;
		(*byte) = ((*byte)<<1);
	}
	(*currentRead)	-= bitsToWrite;
	(*bitsLeft)	-= bitsToWrite;
}


