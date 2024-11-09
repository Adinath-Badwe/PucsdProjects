#pragma once
#include<cstdio>

/* current partition works on 64bit mode disabled */
/* therefore 64bit enabled fields are not applicable */
/* assumption is that this program works on 64bit disabled partition */

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

class FileSystem{
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
		bool is64;
	// methods
	private:
	public:
		unsigned short getGroupNumFromInodeNum(unsigned long inodeNumber);
		void setBlock(const unsigned long blockNumber); // set block to input number
		void setInode(const unsigned long inodeNumber); // set inode to input number
		void setGroupDescriptor(const unsigned int groupNumber); // set the group descriptor of groupNumber
		void getFile(unsigned long inodeNumber);
		void writeToFileExtentTree(unsigned char* blockMap,FILE* ofptr);
		void writeLeafNodeExtentTree(leafNodeExtentTree leafNode,FILE* ofptr);
		void writeInternalNodeExtentTree(internalNodeExtentTree internalNode,FILE* ofptr);
		void writeToFileExtentTreeBlock(FILE* ofptr);
		FileSystem();
		~FileSystem();
};
