#pragma once
#include<cstdio>
#include<cstdlib>
#include<iostream>

typedef struct extentTreeHeader{
	unsigned short magicNumber;
	unsigned short entries;
	unsigned short maxEntries;
	unsigned short depth;
	unsigned int generation;
} extentTreeHeader;

typedef struct leafNodeExtentTree{
	unsigned int firstFileBlock;
	unsigned short len;
	unsigned short startHi;
	unsigned int startLo;
} leafNodeExtentTree;

typedef struct internalNodeExtentTree{
	unsigned int startBlock;
	unsigned int lowerNodeBlockLo;
	unsigned short lowerNodeBlockHi;
	unsigned short unused;
} internalNodeExtentTree;

class Extent {
	private:
	public:
		unsigned int groupNumber;
		unsigned int start; // 0 <= x < BLOCKS_PER_GROUP
		unsigned int freeBlocks; // 0 < x <= BLOCKS_PER_GROUP
		bool init;
		// start + freeBlocks = BLOCKS_PER_GROUP
	
	private:
	public:
		Extent(){
			groupNumber = 0;
			start = 0;
			freeBlocks = 0;
			init = false;
		}
		
		bool operator == (const Extent &other) const {
			if (freeBlocks == other.freeBlocks) return true;
			return false;
		}
		
		bool operator < (const Extent &other) const {
			if (freeBlocks < other.freeBlocks) return true;
			return false;
		}
		
		bool operator <= (const Extent &other) const {
			if (freeBlocks <= other.freeBlocks) return true;
			return false;
		}
		
		bool operator > (const Extent &other) const {
			if (freeBlocks > other.freeBlocks) return true;
			return false;
		}
		
		bool operator >= (const Extent &other) const {
			if (freeBlocks >= other.freeBlocks) return true;
			return false;
		}
};

class ext4FileSystem{
	// variables
	private:
	public:
		FILE* fsptr;
		char *sBlock,*block,*inode,*groupDescriptor;
		
		unsigned short blockSize;
		unsigned short inodeSize;
		unsigned int inodesPerGroup;
		unsigned int inodesPerBlock;
		unsigned short inodeBlocksPerGroup;
		unsigned int blocksPerGroup;
		unsigned int blockGroupSize;
		unsigned int numberOfGroups;
		unsigned long numberOfBlocks;
		unsigned int numberOfInodes;
		unsigned short groupDescriptorSize;
		unsigned char groupsPerFlex;
		bool is64;
	// methods
	private:
	public:
		unsigned short getGroupNumFromInodeNum(unsigned long inodeNumber);
		void setBlock(const unsigned long blockNumber); // set block to input number
		void setInode(const unsigned long inodeNumber); // set inode to input number
		void setGroupDescriptor(const unsigned int groupNumber); // set the group descriptor of groupNumber
		void getFile(unsigned long inodeNumber);
		
		// read from ext4 partition
		void readFromFileExtentTree(unsigned char* iBlock,FILE* ofptr);
		void readLeafNodeExtentTree(leafNodeExtentTree leafNode,FILE* ofptr);
		void readInternalNodeExtentTree(internalNodeExtentTree internalNode,FILE* ofptr);
		void readFromFileExtentTreeBlock(FILE* ofptr);
		
		// write to ext4 partition
		void someFunction1(unsigned long fileSize);
		void constructIBlock();
		void writeExtentTreeHeader(unsigned char* loc,unsigned short validEntries,unsigned short maxEntries,unsigned short depth);
		void writeExtentInternalNode(unsigned char* loc,unsigned int startBlock,unsigned int blockNumberLow32,unsigned short blockNumberHigh16);
		void writeExtentLeafNode(unsigned char* loc,unsigned int firstBlock,unsigned short numberBlock,unsigned int blockNumberLow32,unsigned short blockNumberHigh16);
		
		// incomplete functions
		unsigned int getFreeInode();
		//bool someExtentCondition(unsigned int groupNumber,unsigned long fileSize);
		bool canFitInsideOneGroup(unsigned int groupNumber,unsigned long fileSize,unsigned int extraBlocks);
		void findExtent(unsigned int groupNumber);
		
		ext4FileSystem();
		~ext4FileSystem();
};
