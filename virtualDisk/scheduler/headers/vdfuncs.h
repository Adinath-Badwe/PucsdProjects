#pragma once
#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>

void readBlock(FILE* vdFile,unsigned char** block,unsigned int blockSize,unsigned int blockNumber);
void writeBlock(FILE* vdFile,unsigned char** block,unsigned int blockSize,unsigned int blockNumber);
