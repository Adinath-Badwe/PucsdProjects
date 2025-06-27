#pragma once
#include"../headers/structs.h"
#include<stdlib.h>
#include<stdio.h>

// getFreeBlocks takes a virtual disk file pointer, block size, and a number which gives the block number which we next check to be free
freeBlocks getFreeBlock(FILE* vdFile,unsigned int nextBlockToRead,unsigned int blockSize);
