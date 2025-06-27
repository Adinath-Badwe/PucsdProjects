#include"../headers/vdfuncs.h"
#include"../headers/createVirtualDisk.h"
#include"../headers/define/createVirtualDisk.h"
#include"../headers/define/all.h"
#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>

void createVirtualDisk(unsigned int blockSize,unsigned int numberBlocks){

	// create a file of size : blockSize * numberBlocks
	// declare a virtual disk file pointer and state file pointer
	FILE *vdFile,*stateFile; 
	unsigned long temp;
	// block holds data of one blockSize bytes
	unsigned char* block;
	// bitmap block gives us the block number from where the bitmap starts
	unsigned int bitmapBlock,currentBlock;
	char hasWritten;
	
	// initialise state file and virtual disk
	stateFile = fopen("./virtualDisk/processState.sts","wb");
	vdFile = fopen("./virtualDisk/virtualDisk.vbin", "w+"); 
	
	// allocate memory for one blockSize bytes
	block = (unsigned char*)malloc(blockSize);
	
	char buffer[blockSize];
	memset(buffer,0,blockSize);
	for(unsigned int i = 0;i<numberBlocks;i++){
		fwrite(buffer,1,blockSize,vdFile);
	}
	
	// store the number of blocks present in virtual disk
	temp = numberBlocks;
	fseek(vdFile,METADATA_NUMBER_OF_BLOCKS_LOC,SEEK_SET);
	fwrite(&temp,1,METADATA_NUMBER_OF_BLOCKS_SIZE,vdFile);
	
	// store the block size present in virtual disk
	temp = blockSize;
	fseek(vdFile,METADATA_BLOCK_SIZE_LOC,SEEK_SET);
	fwrite(&temp,1,METADATA_BLOCK_SIZE_SIZE,vdFile);
	
	// store the block bitmap location
	temp = 1;
	fseek(vdFile,METADATA_BLOCK_BITMAP_BLOCK_LOC,SEEK_SET);
	fwrite(&temp,1,METADATA_BLOCK_BITMAP_BLOCK_SIZE,vdFile);
	
	// store number of bitmap blocks
	temp = (numberBlocks>>3)/blockSize;
	if(temp == 0) temp = 1;
	fseek(vdFile,METADATA_BLOCK_BITMAP_NUMBER_OF_BLOCKS_LOC,SEEK_SET);
	fwrite(&temp,1,METADATA_BLOCK_BITMAP_NUMBER_OF_BLOCKS_SIZE,vdFile);
	
	// populate the bitmap
	temp += 1; // for the first metadata block
	
	bitmapBlock = 0;
	fseek(vdFile,METADATA_BLOCK_BITMAP_BLOCK_LOC,SEEK_SET);
	fread(&bitmapBlock,1,METADATA_BLOCK_BITMAP_BLOCK_SIZE,vdFile);
	
	// load the bitmap block into out memory block
	readBlock(vdFile,&block,blockSize,bitmapBlock);
	
	// currentBlock is our block iterator
	currentBlock = bitmapBlock;
	
	hasWritten = 0;
	// populate the bitmap and write it back to the virtual disk
	for(unsigned int i = 0;i < temp;i++){
		if(((unsigned int)(i/8) != 0 ) && (((unsigned int)(i/8) % blockSize) == 0) && ((1<<(i%8)) == 128) ){
			writeBlock(vdFile,&block,blockSize,currentBlock);
			currentBlock += 1;
			readBlock(vdFile,&block,blockSize,currentBlock);
			hasWritten=1;
		}
		block[(i/8)%blockSize] = block[(i/8)%blockSize] | (1<<(i%8));
	}
	writeBlock(vdFile,&block,blockSize,currentBlock);
	
	// close all file pointers and free allocated memory
	fclose(vdFile);
	fclose(stateFile);
	free(block);
}


