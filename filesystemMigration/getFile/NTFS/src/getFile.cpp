#pragma once
#include"../headers/getFile.hpp"
#include"../headers/define/getFile.hpp"
#include<cstdio>
#include<cstdlib>
#include<cstring>
#include<math.h>
#include<iostream>

NTFSFileSystem::NTFSFileSystem(){
	this->fsptr = fopen("/dev/sdb8","rb");
	FILE *ofile = fopen("output/volumeHeader","wb");
	FILE *ofile1 = fopen("output/mft","wb");
	FILE *outputFile = fopen("output/outputFile","wb");
	this->volumeHeader = (unsigned char*)malloc(VOLUME_HEADER_SIZE);
	
	fread(this->volumeHeader,VOLUME_HEADER_SIZE,1,this->fsptr);
	fwrite(this->volumeHeader,VOLUME_HEADER_SIZE,1,ofile);
	
	memcpy(&this->bytesPerSector,
		this->volumeHeader+VOLUME_HEADER_BYTES_PER_SECTOR_LOC,
		VOLUME_HEADER_BYTES_PER_SECTOR_SIZE);
	memcpy(&this->sectorsPerClusterBlock,
		this->volumeHeader+VOLUME_HEADER_SECTORS_PER_CLUSTER_BLOCK_LOC,
		VOLUME_HEADER_SECTORS_PER_CLUSTER_BLOCK_SIZE);
	memcpy(&this->mftClusterBlock,
		this->volumeHeader+VOLUME_HEADER_MFT_CLUSTER_BLOCK_LOC,
		VOLUME_HEADER_MFT_CLUSTER_BLOCK_SIZE);
	memcpy(&this->mftClusterBlock1,
		this->volumeHeader+VOLUME_HEADER_MFT_COPY_CLUSTER_BLOCK_LOC,
		VOLUME_HEADER_MFT_COPY_CLUSTER_BLOCK_SIZE);
	memcpy(&this->mftEntrySize,
		this->volumeHeader+VOLUME_HEADER_MFT_ENTRY_SIZE_LOC,
		VOLUME_HEADER_MFT_ENTRY_SIZE_SIZE);
	memcpy(&this->totalSectors,
		this->volumeHeader+VOLUME_HEADER_TOTAL_SECTORS_LOC,
		VOLUME_HEADER_TOTAL_SECTORS_SIZE);
	memcpy(&this->indexEntrySize,
		this->volumeHeader+VOLUME_HEADER_INDEX_ENTRY_SIZE_LOC,
		VOLUME_HEADER_INDEX_ENTRY_SIZE_SIZE);
	
	this->bytesPerClusterBlock = this->bytesPerSector*this->sectorsPerClusterBlock;
	this->mftEntrySize = (2 << (256-this->mftEntrySize-1));
	
	this->sector = (unsigned char*)malloc(this->bytesPerSector);
	this->clusterBlock = (unsigned char*)malloc(this->bytesPerClusterBlock);
	this->mftEntry = (unsigned char*)malloc(this->mftEntrySize);
	
	this->loadmftEntry(65);
	fwrite(this->mftEntry,this->mftEntrySize,1,ofile1);
	this->getData(outputFile);
}

NTFSFileSystem::~NTFSFileSystem(){
	free(this->volumeHeader);
	free(this->sector);
	free(this->clusterBlock);
	free(this->mftEntry);
}

void NTFSFileSystem::loadClusterBlock(unsigned long clusterIndex){
	fseek(this->fsptr,this->bytesPerClusterBlock*clusterIndex,SEEK_SET);
	fread(this->clusterBlock,this->bytesPerClusterBlock,1,this->fsptr);
}

void NTFSFileSystem::loadmftEntry(unsigned long entryIndex){
	unsigned long clusterBlock;
	
	clusterBlock = this->mftClusterBlock;
	clusterBlock += (unsigned long)((entryIndex * this->mftEntrySize)/this->bytesPerClusterBlock);
	this->loadClusterBlock(clusterBlock);
	memcpy(this->mftEntry,
		this->clusterBlock+(entryIndex % (unsigned long)(this->bytesPerClusterBlock/this->mftEntrySize))*this->mftEntrySize,
		this->mftEntrySize);
}

void NTFSFileSystem::writeResidentData(unsigned long offset,FILE *outputFile){
	unsigned int dataSize;
	unsigned short dataOffset;
	unsigned long dataStart;
	
	memcpy(&dataSize,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_SIZE+MFT_RESIDENT_ATTRIBUTE_DATA_DATA_SIZE_LOC,
		MFT_RESIDENT_ATTRIBUTE_DATA_DATA_SIZE_SIZE);
	memcpy(&dataOffset,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_SIZE+MFT_RESIDENT_ATTRIBUTE_DATA_DATA_OFFSET_LOC,
		MFT_RESIDENT_ATTRIBUTE_DATA_DATA_OFFSET_SIZE);
	
	dataStart = offset+dataOffset;
	fwrite(this->mftEntry+dataStart,dataSize,1,outputFile);
}

void NTFSFileSystem::writeNonResidentData(unsigned long offset,FILE *outputFile){
	unsigned long firstVCN,lastVCN;
	unsigned short dataRunsOffset;
	unsigned long allocatedDataSize,dataSize;
	unsigned long numClusters,dataOffset1;
	unsigned char dataRunTemp;
	char buffer[this->bytesPerClusterBlock];
	unsigned int bytesRead;
	
	numClusters = 0;
	dataOffset1 = 0;
	
	memcpy(&firstVCN,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_SIZE+MFT_NON_RESIDENT_ATTRIBUTE_DATA_FIRST_VCN_LOC,
		MFT_NON_RESIDENT_ATTRIBUTE_DATA_FIRST_VCN_SIZE);
	memcpy(&lastVCN,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_SIZE+MFT_NON_RESIDENT_ATTRIBUTE_DATA_LAST_VCN_LOC,
		MFT_NON_RESIDENT_ATTRIBUTE_DATA_LAST_VCN_SIZE);
	memcpy(&dataRunsOffset,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_SIZE+MFT_NON_RESIDENT_ATTRIBUTE_DATA_DATA_RUNS_OFFSET_LOC,
		MFT_NON_RESIDENT_ATTRIBUTE_DATA_DATA_RUNS_OFFSET_SIZE);
	memcpy(&allocatedDataSize,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_SIZE+MFT_NON_RESIDENT_ATTRIBUTE_DATA_ALLOCATED_DATA_SIZE_LOC,
		MFT_NON_RESIDENT_ATTRIBUTE_DATA_ALLOCATED_DATA_SIZE_SIZE);
	memcpy(&dataSize,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_SIZE+MFT_NON_RESIDENT_ATTRIBUTE_DATA_DATA_SIZE_LOC,
		MFT_NON_RESIDENT_ATTRIBUTE_DATA_DATA_SIZE_SIZE);
	memcpy(&dataRunTemp,this->mftEntry+offset+dataRunsOffset,1);
	
	while(dataRunTemp != 0){
		numClusters = 0;
		dataOffset1 = 0;
		memcpy(&numClusters,this->mftEntry+offset+dataRunsOffset+1,(dataRunTemp&0x0F));
		memcpy(&dataOffset1,this->mftEntry+offset+dataRunsOffset+1+(dataRunTemp&0x0F),(dataRunTemp&0xF0>>4));
		fseek(this->fsptr,dataOffset1*this->bytesPerClusterBlock,SEEK_SET);
		
		while(numClusters != 0){
			bytesRead = fread(buffer,1,this->bytesPerClusterBlock,this->fsptr);
			numClusters -= 1;
			fwrite(buffer,bytesRead,1,outputFile);
		}
		dataRunsOffset += (dataRunTemp&0x0F) + (dataRunTemp&0xF0>>4);
		memcpy(&dataRunTemp,this->mftEntry+offset+dataRunsOffset+1,1);
	}
}

void NTFSFileSystem::getData(FILE* outputFile){
	unsigned long offset = 0;
	unsigned long temp = 0;
	unsigned int attributeCode = 0;
	bool nonResidentData;
	
	memcpy(&offset,
		this->mftEntry+MFT_ENTRY_HEADER_ATTRIBUTE_OFFSET_LOC,
		MFT_ENTRY_HEADER_ATTRIBUTE_OFFSET_SIZE);
	memcpy(&attributeCode,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_ATTRIBUTE_TYPE_LOC,
		MFT_ATTRIBUTE_HEADER_ATTRIBUTE_TYPE_SIZE);
	
	while(attributeCode != 128){
		memcpy(&temp,
			this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_ATTRIBUTE_SIZE_LOC,
			MFT_ATTRIBUTE_HEADER_ATTRIBUTE_SIZE_SIZE);
		offset += temp;
		memcpy(&attributeCode,
			this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_ATTRIBUTE_TYPE_LOC,
			MFT_ATTRIBUTE_HEADER_ATTRIBUTE_TYPE_SIZE);
	}
	memcpy(&nonResidentData,
		this->mftEntry+offset+MFT_ATTRIBUTE_HEADER_NON_RESIDENT_FLAG_LOC,
		MFT_ATTRIBUTE_HEADER_NON_RESIDENT_FLAG_SIZE);
	
	if(nonResidentData){
		this->writeNonResidentData(offset,outputFile);
	}else{
		this->writeResidentData(offset,outputFile);
	}
}
