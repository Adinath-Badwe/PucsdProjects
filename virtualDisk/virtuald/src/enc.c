#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<time.h>
#include<errno.h>
#include"../headers/miscFunc.h"
#include"../headers/enc.h"
#include"../headers/define/all.h"

int encodeFile(unsigned char* iFilePath,unsigned char* oFilePath){
	FILE *ifile,*ofile;
	unsigned int seqLen;
	unsigned char *sseq,buffer[BUFFER_SIZE];
	unsigned short bytesRead;

	ifile = fopen(iFilePath,"rb");
	if (ifile == NULL){
		perror("Input file invalid : ");
		return errno;
	}

	ofile = fopen(oFilePath,"wb");
	if (ofile == NULL){
		perror("Output file invalid : ");
		return errno;
	}
	seqLen = getFileSize(ifile);
	sseq = (unsigned char*)malloc(bytesRequiredEncoding(seqLen));
	encodeSeqLen(sseq,seqLen);
	fwrite(sseq,sizeof(char),bytesRequiredEncoding(seqLen),ofile);

	while(bytesRead = fread(buffer,sizeof(char),BUFFER_SIZE,ifile)){
		fwrite(buffer,sizeof(char),bytesRead,ofile);
	}

	free(sseq);
}

// encodeSeqLen takes a malloced memory space, the size of which is calculated using the bytesRequiredEncoding function,
// and a seqlen (the length of the sequence in bytes) and writes into sseq the encoded sequence to represent the length.

void encodeSeqLen(unsigned char* sseq, unsigned int seqLen){
	unsigned int somevalue = seqLen;
	unsigned int bitsReq = 0; // bits required to store count
	unsigned int bitsLeft; // bits left in the byte, which writes to memory

	while(1){
		if(somevalue == 2){
			break;
		}
		bitsReq += getBits(somevalue);
		somevalue = getBits(somevalue);
	}
	bitsReq += 1; // extra bit for the delimiter
	bitsLeft = bitsReq-1;
	unsigned int current,currentVal;
	current = seqLen;
	currentVal = current;

	while(bitsLeft > 0){
		if(current % 2){
			setBit(sseq,bitsLeft-1);
		}
		bitsLeft -= 1;
		current = current >> 1;
		if(current == 0){
			current = getBits(currentVal);
			currentVal = current;
		}
	}
}

void setBitSeq(unsigned char* sseq,unsigned char byte,unsigned int bitStart){
	for(int i = 0; i < 8;i++){
		if( byte & (128 >> i)){
			setBit(sseq,bitStart+i-1);
		}
	}
}

