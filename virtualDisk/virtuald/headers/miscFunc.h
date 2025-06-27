#include<stdio.h>

unsigned long getFileSize(FILE* ifile);
void setBit(unsigned char *sseq,unsigned int bitpos);
void unsetBit(unsigned char *sseq,unsigned int bitpos);
void setBit1(unsigned char* array,unsigned int byte,unsigned char bit);
void unsetBit1(unsigned char* array,unsigned int byte,unsigned char bit);
unsigned char getBit(unsigned char byte,unsigned char currentBit);
unsigned char getBit1(unsigned char byte,unsigned char currentBit);
unsigned int getBits(unsigned int value);
unsigned char readFromLeft(unsigned char byte, unsigned char bits);
unsigned char readFromRight(unsigned char byte, unsigned char bits);
void printBinary(unsigned char byte);
unsigned int bytesRequiredEncoding(unsigned long seqLen);
unsigned int parseFilePath(unsigned char* fileName);
unsigned char bytesRequiredMinimum(unsigned long pointer);
void readBetween(unsigned char* input,unsigned char* output,unsigned int startByte,unsigned char startBit,unsigned int bytesToRead,unsigned char bitsToRead);
void writeBetween(unsigned char* input,unsigned char* output,unsigned int startByte,unsigned char startBit,unsigned int bytesToWrite,unsigned char bitsToWrite);
