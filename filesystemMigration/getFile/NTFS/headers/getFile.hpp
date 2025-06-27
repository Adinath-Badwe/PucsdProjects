#pragma once
#include<cstdio>


class NTFSFileSystem{
	// variables
	private:
	public:
		unsigned short bytesPerSector;
		unsigned char sectorsPerClusterBlock;
		unsigned long totalSectors;
		unsigned long mftClusterBlock;
		unsigned long mftClusterBlock1;
		unsigned long mftEntrySize;
		unsigned char indexEntrySize;
		unsigned long bytesPerClusterBlock;
		
		unsigned char* volumeHeader;
		unsigned char* sector;
		unsigned char* clusterBlock;
		unsigned char* mftEntry;
		FILE* fsptr;
		
	// methods
	private:
	public:
		void writeResidentData(unsigned long offset,FILE *outputFile);
		void writeNonResidentData(unsigned long offset,FILE *outputFile);
		void loadClusterBlock(unsigned long clusterIndex);
		void loadmftEntry(unsigned long entryIndex);
		void getData(FILE *outputFile);
		
		NTFSFileSystem();
		~NTFSFileSystem();
};
