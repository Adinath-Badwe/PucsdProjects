#include"../headers/getFreeBlocks.h"
#include"../headers/define/getFreeBlocks.h"
#include"../headers/define/all.h"
#include"../headers/vdfuncs.h"
#include"../headers/structs.h"
#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>

// state save requirements : current_block_number : 4 bytes,
freeBlocks getFreeBlock(FILE* vdFile,unsigned int nextBlockToRead,unsigned int blockSize){
	freeBlocks output;
	// block holds a block of space at given time
	unsigned char* block;
	// bitmapBlock gives the block number in the virtual disk from where the bitmap block starts
	// numberblocks gives the total number of blocks in the virtual disks
	// currentBlock is the blocknumber which we check if it is free
	unsigned int bitmapBlock,numberBlocks,currentBlock;
	unsigned char upperLimit;
	
	// allocate memory for the block
	block = (unsigned char*)malloc(blockSize);
	
	// set free block found to be 0
	output.found = 0;
	
	// load the bitmap block number 
	printf("%p\n",vdFile);
	fseek(vdFile,METADATA_BLOCK_BITMAP_BLOCK_LOC,SEEK_SET);
	fread(&bitmapBlock,1,METADATA_BLOCK_BITMAP_BLOCK_SIZE,vdFile);
	
	// load total number of blocks
	fseek(vdFile,METADATA_NUMBER_OF_BLOCKS_LOC,SEEK_SET);
	fread(&numberBlocks,1,METADATA_NUMBER_OF_BLOCKS_SIZE,vdFile);
	
	// load current bitmap block
	currentBlock = nextBlockToRead;
	
	// load the block bitmap block which contains the currentBlock
	readBlock(vdFile,&block,blockSize,bitmapBlock+(unsigned int)((currentBlock)/(blockSize*8)));
	
	// upper limit gives us the number of blocks to check for if they are free, at each run of this process
	upperLimit = 5;
	for(unsigned char i = 0;i < upperLimit;i++){
		
		// read the next block in our allocated block space if our current block has been exhausted of search
		if((unsigned int)((currentBlock+i)/8) != 0 && (((currentBlock+i) % blockSize) == 0)){
			readBlock(vdFile,&block,blockSize,bitmapBlock+(unsigned int)((currentBlock+i)/(blockSize*8)));
		}
		
		// if a free block is found, generate the output
		if((block[((currentBlock+i)/8)%blockSize] & ((1<<((currentBlock+i)%8)))) == 0){
			output.found = 1;
			output.blockNumber = currentBlock+i;
			currentBlock = currentBlock+i+1;
			i = upperLimit;
		}
	}

	if(output.found != 1){
		// is free block is not found, set the next block to search as the output block number
		currentBlock += upperLimit;
		output.blockNumber = currentBlock;
	}
	
	// free our allocated block space
	free(block);
	return output;
}
