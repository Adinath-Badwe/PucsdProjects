#include"../headers/define/miscFunc.h"
#include"../headers/miscFunc.h"
#include<stdio.h>
#include<math.h>
#include<stdlib.h>
#include<string.h>

//parseFilePath takes a malloced filename pointer and length of its.
// and gives out only the file name
unsigned int parseFilePath(unsigned char* fileName){
	unsigned int length = strlen(fileName);
	int i = length - 1;
	int k = 0;
	for(;i >= 0;i--){
		if (fileName[i] == DELIMITER_SLASH) break;
	}
	i++;
	for(;i < length;i++){
		fileName[k] = fileName[i];
		k++;
	}
	fileName[k] = 0;
}

// getFileSize takes a file pointer and returns the size of the file in bytes
unsigned long getFileSize(FILE* ifile){
	unsigned long seqLen;
	fseek(ifile,0,SEEK_END);
	seqLen = ftell(ifile);
	fseek(ifile,0,SEEK_SET);
	return seqLen;
}

// getBits takes a value and gives out how many bits does it take to represent that value
unsigned int getBits(unsigned int value){
	unsigned int br = 0;

	while(value >= 1){
		br++;
		value = value >> 1;
	}
	return br;
}

// setBit takes a unsigned char array and sets the bit located at bitpos to 1
// assumption is that bitpos lies within mallocced sseq
void setBit(unsigned char *sseq,unsigned int bitpos){
	unsigned int byte = bitpos/8;
	sseq[byte] = sseq[byte] | 128 >> (bitpos%8) ;
}

// setBit takes a unsigned char array and sets the bit located at bitpos to 0
// assumption is that bitpos lies within mallocced sseq
void unsetBit(unsigned char *sseq,unsigned int bitpos){
	unsigned int byte = bitpos/8;
	sseq[byte] = sseq[byte] & (255 - (128 >> (bitpos%8))) ;
}

// bytesRequiredEncoding takes the length of the sequence in bytes and returns the total number of bytes required to store that sequence including the count
unsigned int bytesRequiredEncoding(unsigned long seqLen){
	unsigned oa = seqLen;
	unsigned int bitsReq = 0; // bits required to store count
	while(1){
		if(seqLen == 2){
			break;
		}
		bitsReq += getBits(seqLen);
		seqLen = getBits(seqLen);
	}
	bitsReq += 1; // extra bit for the delimiter
	unsigned int sizeSseq = ceil((float)bitsReq/8);
	return sizeSseq;
}

// get bit takes a byte and returns if the 'currentBit' bit from the left (1-8) is 1 or 0
unsigned char getBit(unsigned char byte,unsigned char currentBit){
	if( byte & (1 << (currentBit-1))) return 1;
	return 0;
}

unsigned char getBit1(unsigned char byte,unsigned char currentBit){
	if( byte & (1 << (currentBit))) return 1;
	return 0;
}

// readFromLeft takes a byte and a value 'bits' and gives 'bits' number of bits from the left (most significant bits)
unsigned char readFromLeft(unsigned char byte, unsigned char bits){
	return (byte >> (8-bits));
}
// readFromRight takes a byte and a value 'bits' and gives 'bits' number of bits from the right (least significant bits)
unsigned char readFromRight(unsigned char byte, unsigned char bits){
	return (byte << (8-bits))>>(8-bits);
}
// printBinary takes a byte and prints it in binary form
void printBinary(unsigned char byte){
	for(int i = 0; i<8;i++){
		if(byte & 128){
			printf("1");
		}else{
			printf("0");
		}
		byte = byte << 1;
	}
}

// take an unsigned long and gives out how many bytes are actually required to represent the given value
unsigned char bytesRequiredMinimum(unsigned long pointer){
	unsigned char br = 0;
	for(unsigned char i = 0;i < 8;i++){
		if(0xFF & pointer){
			br = i;
		}
		pointer = pointer >> 8;
	}
	return br+1;
}

void writeBetween(unsigned char* input,unsigned char* output,unsigned int startByte,unsigned char startBit,unsigned int bytesToWrite,unsigned char bitsToWrite){
	unsigned int currentByte = startByte;
	unsigned char currentBit = startBit;
	unsigned int i;
	for(i = 0;i<bytesToWrite;i++){
		for(unsigned char j = 0;j<8;j++){
			if(getBit(input[i],j)){
				setBit1(output,currentByte,currentBit);
			}else{
				unsetBit1(output,currentByte,currentBit);
			}
			currentBit++;
			if(currentBit == 8){
					currentBit = 0;
					currentByte++;
			}
		}
	}
	
	for(unsigned char j = 0; j < bitsToWrite;j++){
		if(getBit(input[i],j)){
			setBit1(output,currentByte,currentBit);
		}else{
			unsetBit1(output,currentByte,currentBit);
		}
		currentBit++;
		if(currentBit == 8){
				currentBit = 0;
				currentByte++;
		}
	}
}

void readBetween(unsigned char* input,unsigned char* output,unsigned int startByte,unsigned char startBit,unsigned int bytesToRead,unsigned char bitsToRead){
	unsigned int currentByte = startByte;
	unsigned char currentBit = startBit;
	unsigned int i;
	unsigned char j;
	i = 0;
	j = 0;
	for(j = 0; i < bytesToRead; i++){
		for(j = 0; j<8; j++){
			if(getBit(input[currentByte],currentBit)){
				setBit1(output,i,j);
			}else{
				unsetBit1(output,i,j);
			}
			currentBit++;
			if(currentBit == 8){
				currentByte++;
				currentBit = 0;
			}
		}
	}
	j = 0;
	for(unsigned char k = 0; k < bitsToRead;k++){
		if(getBit(input[currentByte],currentBit)){
			setBit1(output,i,j);
		}else{
			unsetBit1(output,i,j);
		}
		currentBit++;
		if(currentBit == 8){
				currentBit = 0;
				currentByte++;
		}
		j++;
		if(j == 8){
			j = 0;
			i++;
		}
	}
	
}
void setBit1(unsigned char* array,unsigned int byte,unsigned char bit){
	array[byte] = array[byte] | (1<<bit) ;
}

void unsetBit1(unsigned char* array,unsigned int byte,unsigned char bit){
	array[byte] = array[byte] & (255 - (1<<bit)) ;
}
