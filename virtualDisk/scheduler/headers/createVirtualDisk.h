#pragma once
#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>

// creates a virtual disk of size = blockSize*numberBlocks
void createVirtualDisk(unsigned int blockSize,unsigned int numberBlocks);
