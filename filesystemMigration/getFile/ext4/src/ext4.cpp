#pragma once
#include"../headers/ext4.hpp"
#include"../headers/define/ext4.hpp"
#include<cstdio>
#include<cstdlib>
#include<cstring>
#include<math.h>
#include<iostream>
#include<queue>

ext4FileSystem::ext4FileSystem(){
	/*load sblock*/
	this->fsptr = fopen("/dev/sda5","rb");
	this->sBlock = (char*)malloc(SUPER_BLOCK_SIZE);
	fseek(this->fsptr,SUPER_BLOCK_SIZE,SEEK_SET);
	fread(this->sBlock,sizeof(char),SUPER_BLOCK_SIZE,this->fsptr);

	/*load important variables*/
	this->inodeSize = ((unsigned short *)(this->sBlock+SUPER_BLOCK_INODE_SIZE_LOC))[0];
	this->inodesPerGroup = ((unsigned int*)(this->sBlock+SUPER_BLOCK_INODES_PER_GROUP_LOC))[0];
	
	this->numberOfBlocks = ((unsigned int*)(this->sBlock+SUPER_BLOCK_NUMBER_OF_BLOCKS_LOC))[0];
	this->numberOfInodes = ((unsigned int*)(this->sBlock+SUPER_BLOCK_NUMBER_OF_INODES_LOC))[0];
	this->blockSize = pow(2,((double)(10+(((unsigned int*)(this->sBlock+SUPER_BLOCK_BLOCK_SIZE_LOC))[0]))));
	this->blocksPerGroup = ((unsigned int*)(this->sBlock+SUPER_BLOCK_BLOCKS_PER_GROUP_LOC))[0];
	this->blockGroupSize = this->blockSize * this->blocksPerGroup;
	this->groupDescriptorSize = ((unsigned short*)(this->sBlock+SUPER_BLOCK_GROUP_DESCRIPTOR_SIZE_LOC))[0];
	this->inodeBlocksPerGroup = (this->inodeSize*this->inodesPerGroup)/(this->blockSize);
	this->numberOfGroups = (unsigned int)(ceil((float)(this->numberOfBlocks)/(float)(this->blocksPerGroup)));
	this->inodesPerBlock = this->blockSize/this->inodeSize;
	memcpy(&this->groupsPerFlex,this->sBlock+SUPER_BLOCK_GROUPS_PER_FLEX,1);
	
	/*malloc a space for block*/
	this->block = (char*)malloc(this->blockSize);
	this->inode = (char*)malloc(this->inodeSize);
	this->groupDescriptor = (char*)malloc(this->groupDescriptorSize);
	
	// 64bit version changes
	this->is64 = FEATURE_INCOMPAT_64_BIT & ((unsigned int*)(this->sBlock+SUPER_BLOCK_FEATURES_INCOMPAT_LOC))[0];
	
	unsigned long temp = 0;
	temp = ((unsigned int*)(this->sBlock+SUPER_BLOCK_NUMBER_OF_BLOCKS_HIGH_32_LOC))[0];
	temp = temp << 32;
	this->numberOfBlocks = temp | this->numberOfBlocks ;
}

ext4FileSystem::~ext4FileSystem(){
	free(this->sBlock);
	free(this->block);
	free(this->inode);
	free(this->groupDescriptor);
}

void ext4FileSystem::getFile(unsigned long inodeNumber){
	FILE* ofptr = fopen("./output/fileOutput.txt","wb");
	unsigned char* iBlock = (unsigned char*)malloc(INODE_I_BLOCK_SIZE);
	unsigned long fileSize ;
	this->setGroupDescriptor(this->getGroupNumFromInodeNum(inodeNumber)); 
	this->setInode(inodeNumber);
	
	if(this->is64){
		fileSize = *(unsigned int*)(this->inode+INODE_FILE_SIZE_HIGH_32_LOC);
		fileSize = fileSize << 32;
		fileSize = fileSize | *(unsigned int*)(this->inode+INODE_FILE_SIZE_LOC);
	}else{
		fileSize = *(unsigned int*)(this->inode+INODE_FILE_SIZE_LOC);
	}
	
	unsigned int flags = *(unsigned int*)(this->inode+INODE_FLAGS_LOC);
	memcpy(iBlock,(this->inode)+INODE_I_BLOCK_LOC,INODE_I_BLOCK_SIZE);
	
	this->readFromFileExtentTree(iBlock,ofptr);
	FILE *inodefptr = fopen("output/inode.txt","wb");
	fwrite(this->inode,1,256,inodefptr);
	free(iBlock);
}

void ext4FileSystem::readFromFileExtentTree(unsigned char* iBlock,FILE* ofptr){
	extentTreeHeader header;
	memcpy(&header,iBlock,INODE_I_BLOCK_EXTENT_TREE_HEADER_SIZE);
	
	if(header.depth > 0){
		internalNodeExtentTree internalNode;
		for(int i = 0;i < header.entries; i++){
			memcpy(&internalNode,
				(iBlock+INODE_I_BLOCK_EXTENT_TREE_HEADER_SIZE)+(i*INODE_I_BLOCK_EXTENT_TREE_INTERNAL_NODE_SIZE),
				INODE_I_BLOCK_EXTENT_TREE_INTERNAL_NODE_SIZE);
			readInternalNodeExtentTree(internalNode,ofptr);
		}
	}else{
		leafNodeExtentTree leafNode;
		for(int i = 0;i < header.entries;i++){
			memcpy(&leafNode,
				(iBlock+INODE_I_BLOCK_EXTENT_TREE_HEADER_SIZE)+(i*INODE_I_BLOCK_EXTENT_TREE_LEAF_NODE_SIZE ),
				INODE_I_BLOCK_EXTENT_TREE_LEAF_NODE_SIZE );
			readLeafNodeExtentTree(leafNode,ofptr);
		}
	}
}

void ext4FileSystem::readFromFileExtentTreeBlock(FILE* ofptr){
	extentTreeHeader header;
	unsigned char currentBlock[this->blockSize];
	memcpy(currentBlock,this->block,this->blockSize);
	memcpy(&header,currentBlock,INODE_I_BLOCK_EXTENT_TREE_HEADER_SIZE);
	
	if(header.depth > 0){
		internalNodeExtentTree internalNode;
		for(int i = 0;i < header.entries; i++){
			memcpy(&internalNode,
				(currentBlock+INODE_I_BLOCK_EXTENT_TREE_HEADER_SIZE)+(i*INODE_I_BLOCK_EXTENT_TREE_INTERNAL_NODE_SIZE),
				INODE_I_BLOCK_EXTENT_TREE_INTERNAL_NODE_SIZE);
			readInternalNodeExtentTree(internalNode,ofptr);
		}
	}else{
		leafNodeExtentTree leafNode;
		for(int i = 0;i < header.entries;i++){
			memcpy(&leafNode,
				(currentBlock+INODE_I_BLOCK_EXTENT_TREE_HEADER_SIZE)+(i*INODE_I_BLOCK_EXTENT_TREE_LEAF_NODE_SIZE),
				INODE_I_BLOCK_EXTENT_TREE_LEAF_NODE_SIZE);
			readLeafNodeExtentTree(leafNode,ofptr);
		}
	}
}

void ext4FileSystem::readLeafNodeExtentTree(leafNodeExtentTree leafNode,FILE* ofptr){
	for(int i = 0 ; i < leafNode.len;i++){
		this->setBlock(leafNode.startLo+i);
		fwrite(this->block,sizeof(char),this->blockSize,ofptr);
	}
}

void ext4FileSystem::readInternalNodeExtentTree(internalNodeExtentTree internalNode,FILE* ofptr){
	this->setBlock(internalNode.lowerNodeBlockLo);
	this->readFromFileExtentTreeBlock(ofptr);
}

void ext4FileSystem::setBlock(unsigned long blockNumber){
	fseek(this->fsptr,blockNumber*this->blockSize,SEEK_SET);
	fread(this->block,sizeof(char),this->blockSize,this->fsptr);
}

void ext4FileSystem::setInode(unsigned long inodeNumber){
	unsigned long groupNumber,inodeTableBlock,inodePositionInTable ;
	groupNumber = this->getGroupNumFromInodeNum(inodeNumber); 
	this->setGroupDescriptor(groupNumber);
	if(this->is64){
		inodeTableBlock = (((unsigned int*)(this->groupDescriptor + GROUP_DESCRIPTOR_INODE_TABLE_BLOCK_HIGH_32_LOC))[0]);
		inodeTableBlock = inodeTableBlock << 32;
		inodeTableBlock = inodeTableBlock | (((unsigned int*)(this->groupDescriptor + GROUP_DESCRIPTOR_INODE_TABLE_BLOCK_LOC))[0]);
	}else{
		inodeTableBlock = (((unsigned int*)(this->groupDescriptor + GROUP_DESCRIPTOR_INODE_TABLE_BLOCK_LOC))[0]);
	}
	
	inodePositionInTable = (inodeNumber-1) % this->inodesPerGroup;
	inodeTableBlock += (inodePositionInTable) / this->inodesPerBlock;
	this->setBlock(inodeTableBlock);
	inodePositionInTable = inodePositionInTable % this->inodesPerBlock; 
	memcpy(this->inode,(this->block+inodePositionInTable*this->inodeSize),this->inodeSize);
}

void ext4FileSystem::setGroupDescriptor(unsigned int groupNumber){
	fseek(this->fsptr,this->blockSize+(this->groupDescriptorSize*groupNumber),SEEK_SET);
	fread(this->groupDescriptor,sizeof(char),this->groupDescriptorSize,this->fsptr);
}

unsigned short ext4FileSystem::getGroupNumFromInodeNum(unsigned long inodeNumber){
	return (inodeNumber-1)/(this->inodesPerGroup);
}

//-----------------------------------------------------------------------------------------------------------------------------------------------
//-----------------------------------------------------------------------------------------------------------------------------------------------
// write functions start here

void ext4FileSystem::someFunction1(unsigned long fileSize){
	memset(this->inode,0,this->inodeSize);
	unsigned short inodeMode = 0;
	unsigned int fileSizeHigh32 = (fileSize >> 32) & 0xFFFFFFFF;
	unsigned int inodeFlags = 0;
	unsigned int inodeNumber,freeInodeCount;
	
	memcpy(this->inode+INODE_FILE_SIZE_LOC,
		&fileSize,
		INODE_FILE_SIZE_SIZE);
	memcpy(this->inode+INODE_FILE_SIZE_HIGH_32_LOC,
		&fileSizeHigh32,
		INODE_FILE_SIZE_SIZE);
	memcpy(this->inode+INODE_FLAGS_LOC,
		&inodeFlags,
		INODE_FLAGS_SIZE);
}

void ext4FileSystem::writeExtentTreeHeader(unsigned char* loc,unsigned short validEntries,unsigned short maxEntries,unsigned short depth){
	unsigned short magicNumber = 0xF30A;
	memcpy(loc,&magicNumber,2);
	memcpy(loc+2,&validEntries,2);
	memcpy(loc+4,&maxEntries,2);
	memcpy(loc+6,&depth,2);
}

void ext4FileSystem::writeExtentInternalNode(unsigned char* loc,unsigned int startBlock,unsigned int blockNumberLow32,unsigned short blockNumberHigh16){
	memcpy(loc,&startBlock,4);
	memcpy(loc+4,&blockNumberLow32,4);
	memcpy(loc+8,&blockNumberHigh16,2);
}

void ext4FileSystem::writeExtentLeafNode(unsigned char* loc,unsigned int firstBlock,unsigned short numberBlock,unsigned int blockNumberLow32,unsigned short blockNumberHigh16){
	memcpy(loc,&firstBlock,4);
	memcpy(loc+4,&numberBlock,2);
	memcpy(loc+6,&blockNumberHigh16,2);
	memcpy(loc+8,&blockNumberLow32,4);
}

void ext4FileSystem::constructIBlock(){
	// function incomplete
}

unsigned int ext4FileSystem::getFreeInode(){
	unsigned long inodeBitmapBlock = 0;
	unsigned int temp;
	unsigned long counter = 0;
	unsigned short flags = 0;
	unsigned int usedInodes = 0;
	unsigned int freeInodes = 0;
	unsigned int freeInodes1 = 0;
	unsigned int totalInodes;
	unsigned int totalFreeInodes;
	
	memcpy(&totalInodes,this->sBlock+SUPER_BLOCK_NUMBER_OF_INODES_LOC,4);
	memcpy(&totalFreeInodes,this->sBlock+SUPER_BLOCK_NUMBER_OF_FREE_INODES_LOC,4);
	
	for(unsigned int i = 0; i < this->numberOfGroups;i++){
		//freeInodes1 = 0;
		this->setGroupDescriptor(i);
		memcpy(&flags,this->groupDescriptor + GROUP_DESCRIPTOR_FLAGS_LOC,GROUP_DESCRIPTOR_FLAGS_SIZE);

		if(flags & GROUP_DESCRIPTOR_FLAG_INODE_UNINT) continue;
		
		usedInodes = 0;
		temp = 0;
		memcpy(&temp,this->groupDescriptor+GROUP_DESCRIPTOR_FREE_INODE_COUNT_HIGH_16_LOC,GROUP_DESCRIPTOR_FREE_INODE_COUNT_SIZE);
		freeInodes = temp;
		freeInodes = freeInodes << 16;
		memcpy(&temp,this->groupDescriptor+GROUP_DESCRIPTOR_FREE_INODE_COUNT_LOW_16_LOC,GROUP_DESCRIPTOR_FREE_INODE_COUNT_SIZE);
		freeInodes += temp;
		
		memcpy(&temp,
			this->groupDescriptor+GROUP_DESCRIPTOR_INODE_BITMAP_BLOCK_HIGH_32_LOC,
			GROUP_DESCRIPTOR_INODE_BITMAP_BLOCK_HIGH_32_SIZE);
		inodeBitmapBlock = temp;
		inodeBitmapBlock = (inodeBitmapBlock << 32);
		memcpy(&temp,
			this->groupDescriptor+GROUP_DESCRIPTOR_INODE_BITMAP_BLOCK_LOW_32_LOC,
			GROUP_DESCRIPTOR_INODE_BITMAP_BLOCK_LOW_32_SIZE);
		
		inodeBitmapBlock += temp;
		this->setBlock(inodeBitmapBlock);
		
		for(unsigned int j = 0;j<this->inodesPerGroup;j++){
			//printf("%d\n",j);
			if(((this->block[j/8])&(1<<(j%8)))){
				//printf("%d ",i*this->inodesPerGroup+j+1);
				counter += 1;
				usedInodes += 1;
			}
		}
		/*
		if(usedInodes + freeInodes != this->inodesPerGroup){
			printf("Discrepancy : %d\n",this->inodesPerGroup-(usedInodes + freeInodes));
		}
		*/
	}
	//printf("%d\n",totalInodes-totalFreeInodes);
	//printf("%d\n",counter);
	//printf("%d\n",totalInodes-totalFreeInodes-counter);
}

bool ext4FileSystem::canFitInsideOneGroup(unsigned int groupNumber,unsigned long fileSize,unsigned int extraBlocks){
	unsigned int freeBlocks,temp;
	temp = 0;
	this->setGroupDescriptor(groupNumber);
	memcpy(&freeBlocks,this->groupDescriptor+GROUP_DESCRIPTOR_FREE_BLOCK_COUNT_HIGH_16_LOC,GROUP_DESCRIPTOR_FREE_BLOCK_COUNT_SIZE);
	freeBlocks = freeBlocks << 16;
	memcpy(&temp,this->groupDescriptor+GROUP_DESCRIPTOR_FREE_BLOCK_COUNT_LOW_16_LOC,GROUP_DESCRIPTOR_FREE_BLOCK_COUNT_SIZE);
	freeBlocks += temp;
	
	if((unsigned long)((unsigned long)(freeBlocks)*(unsigned long)this->blockSize) >= fileSize+(unsigned long)(extraBlocks)*(unsigned long)(this->blockSize)) return true;
	return false;
}

void ext4FileSystem::findExtent(unsigned int groupNumber){
	unsigned long blockBitmap,start,number; // blockBitmap holds blockNumber of bitmap block in ext4, start gives the start of a particular extent, number gives number of blocks in an extent
	unsigned int temp;
	bool currExtent;
	Extent extent;
	std::priority_queue<Extent> extentHeap;
	
	extent.groupNumber = groupNumber;
	this->setGroupDescriptor(groupNumber);
	
	// load bitmap blocknumber into blockBitmap (64 bit)
	memcpy(&blockBitmap,this->groupDescriptor+GROUP_DESCRIPTOR_BLOCK_BITMAP_HIGH_32_LOC,GROUP_DESCRIPTOR_BLOCK_BITMAP_SIZE);
	blockBitmap = blockBitmap << 32;
	memcpy(&temp,this->groupDescriptor+GROUP_DESCRIPTOR_BLOCK_BITMAP_LOW_32_LOC,GROUP_DESCRIPTOR_BLOCK_BITMAP_SIZE);
	blockBitmap += temp;
	
	// load blockBitmap into block
	this->setBlock(blockBitmap);
	currExtent = false;
	
	for(unsigned int i = 0;i < this->blocksPerGroup;i++){
		if(this->block[(unsigned int)i/8]&(1<<(i%8))){
			if(currExtent == true){ // if current extent exists
				// write current extent to the heap
				extent.groupNumber = groupNumber;
				extent.freeBlocks = number;
				extent.start = start;
				extent.init = true;
				extentHeap.push(extent);
				Extent extent;
			}
			
			currExtent = false;
		}else{
			if(currExtent == false){ // if there is no current extent
				start = i;
				number = 0;
			}
			number += 1;
			currExtent = true; // current extent exists
		}
	}
	
	std::cout << extentHeap.size() << std::endl;
}

