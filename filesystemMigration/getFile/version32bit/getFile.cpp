#pragma once
#include"getFile.hpp"
#include<cstdio>
#include<cstdlib>
#include<cstring>
#include<math.h>
#include<iostream>

FileSystem::FileSystem(){
	/*load sblock*/
	this->fsptr = fopen("/dev/sda5","rb");
	this->sBlock = (char*)malloc(1024);
	fseek(this->fsptr,1024,SEEK_SET);
	fread(this->sBlock,sizeof(char),1024,this->fsptr);
	/*load important variables*/
	this->inodeSize = ((unsigned short *)(this->sBlock+0x58))[0];
	this->inodesPerGroup = ((unsigned int*)(this->sBlock+0x28))[0];
	this->numberOfBlocks = ((unsigned int*)(this->sBlock+0x4))[0];
	this->numberOfInodes = ((unsigned int*)(this->sBlock))[0];
	this->blockSize = pow(2,((double)(10+(((unsigned int*)(this->sBlock+0x18))[0]))));
	this->blocksPerGroup = ((unsigned int*)(this->sBlock+0x20))[0];
	this->blockGroupSize = this->blockSize * this->blocksPerGroup;
	
	this->inodeBlocksPerGroup = (this->inodeSize*this->inodesPerGroup)/(this->blockSize);
	this->numberOfGroups = (unsigned int)(ceil((float)(this->numberOfBlocks)/(float)(this->blocksPerGroup)));
	this->inodesPerBlock = this->blockSize/this->inodeSize;
	
	/*malloc a space for block*/
	this->block = (char*)malloc(this->blockSize);
	this->inode = (char*)malloc(this->inodeSize);
	this->groupDescriptor = (char*)malloc(32);
}

FileSystem::~FileSystem(){
	free(this->sBlock);
	free(this->block);
	free(this->inode);
	free(this->groupDescriptor);
}

void FileSystem::getFile(unsigned int inodeNumber){
	FILE* ofptr = fopen("./fileOutput","wb");
	unsigned char* blockMap = (unsigned char*)malloc(60);
	
	this->setGroupDescriptor(this->getGroupNumFromInodeNum(inodeNumber)); 
	this->setInode(inodeNumber);
	//unsigned char buffer[this->blockSize];
	unsigned long fileSize = *(unsigned int*)(this->inode+0x4);
	
	unsigned int flags = *(unsigned int*)(this->inode+0x20);
	memcpy(blockMap,(this->inode)+0x28,60);
	
	this->writeToFileExtentTree(blockMap,ofptr);
	free(blockMap);
}

void FileSystem::writeToFileExtentTree(unsigned char* blockMap,FILE* ofptr){
	extentTreeHeader header;
	memcpy(&header,blockMap,12);
	std::cout << "----Inside header node----" << std::endl;
	std::cout << "header.entries " <<header.entries << std::endl;
	std::cout << "header.maxEntries " << header.maxEntries << std::endl;
	std::cout << "header.depth "<< header.depth << std::endl;
	std::cout << "----Exiting header node----" << std::endl;
	
	if(header.depth > 0){
		internalNodeExtentTree internalNode;
		for(int i = 0;i < header.entries; i++){
			memcpy(&internalNode,(blockMap+12)+(i*12),12);
			writeInternalNodeExtentTree(internalNode,ofptr);
		}
	}else{
		leafNodeExtentTree leafNode;
		for(int i = 0;i < header.entries;i++){
			memcpy(&leafNode,(blockMap+12)+(i*12),12);
			writeLeafNodeExtentTree(leafNode,ofptr);
		}
	}
}

//void FileSystem::writeToFileExtentTree60Bytes(unsigned char* blockMap,FILE* ofptr){
//
//}

void FileSystem::writeToFileExtentTreeBlock(FILE* ofptr){
	extentTreeHeader header;
	unsigned char currentBlock[this->blockSize];
	memcpy(currentBlock,this->block,this->blockSize);
	memcpy(&header,currentBlock,12);
	std::cout << "----Inside header node----" << std::endl;
	std::cout << "header.entries " <<header.entries << std::endl;
	std::cout << "header.maxEntries " << header.maxEntries << std::endl;
	std::cout << "header.depth "<< header.depth << std::endl;
	std::cout << "----Exiting header node----" << std::endl;
	if(header.depth > 0){
		internalNodeExtentTree internalNode;
		for(int i = 0;i < header.entries; i++){
			memcpy(&internalNode,(currentBlock+12)+(i*12),12);
			writeInternalNodeExtentTree(internalNode,ofptr);
		}
	}else{
		leafNodeExtentTree leafNode;
		for(int i = 0;i < header.entries;i++){
			memcpy(&leafNode,(currentBlock+12)+(i*12),12);
			writeLeafNodeExtentTree(leafNode,ofptr);
		}
	}
}

void FileSystem::writeLeafNodeExtentTree(leafNodeExtentTree leafNode,FILE* ofptr){
	std::cout << "----Inside leaf node----" << std::endl;
	std::cout << "leafNode.firstFileBlock " <<leafNode.firstFileBlock << std::endl;
	std::cout << "leafNode.startLo " <<leafNode.startLo << std::endl;
	std::cout << "leafNode.startHi " << leafNode.startHi << std::endl;
	std::cout << "leafNode.len "<< leafNode.len << std::endl;
	std::cout << "----Exiting leaf node----" << std::endl;
	for(int i = 0 ; i < leafNode.len;i++){
		this->setBlock(leafNode.startLo+i);
		fwrite(this->block,sizeof(char),this->blockSize,ofptr);
	}
}

void FileSystem::writeInternalNodeExtentTree(internalNodeExtentTree internalNode,FILE* ofptr){
	std::cout << "----Inside internal node----" << std::endl;
	std::cout << "start block " << internalNode.startBlock << std::endl;
	std::cout << "lower block lo " << internalNode.lowerNodeBlockLo<< std::endl;
	std::cout << "lower block hi " << internalNode.lowerNodeBlockHi << std::endl;
	std::cout << "----Exiting internal node----" << std::endl;
	this->setBlock(internalNode.lowerNodeBlockLo);
	this->writeToFileExtentTreeBlock(ofptr);
}

void FileSystem::setBlock(unsigned int blockNumber){
	fseek(this->fsptr,blockNumber*blockSize,SEEK_SET);
	fread(this->block,sizeof(char),this->blockSize,this->fsptr);
}

void FileSystem::setInode(unsigned int inodeNumber){
	unsigned int groupNumber,inodeTableBlock,inodePositionInTable ;
	groupNumber = this->getGroupNumFromInodeNum(inodeNumber); 
	
	this->setGroupDescriptor(groupNumber);
	inodeTableBlock = (((unsigned int*)(this->groupDescriptor + 0x8))[0]);
	inodePositionInTable = (inodeNumber-1) % this->inodesPerGroup;
	inodeTableBlock += (inodePositionInTable) / this->inodesPerBlock;
	this->setBlock(inodeTableBlock);
	inodePositionInTable = inodePositionInTable % this->inodesPerBlock; 
	memcpy(this->inode,(this->block+inodePositionInTable*this->inodeSize),this->inodeSize);
}

void FileSystem::setGroupDescriptor(unsigned short groupNumber){
	fseek(this->fsptr,this->blockSize+(32*groupNumber),SEEK_SET);
	fread(this->groupDescriptor,sizeof(char),32,this->fsptr);
}

unsigned short FileSystem::getGroupNumFromInodeNum(unsigned int inodeNumber){
	return (inodeNumber-1)/(this->inodesPerGroup);
}