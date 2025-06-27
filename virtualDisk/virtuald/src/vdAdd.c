#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<stdbool.h>
#include<errno.h>
#include<string.h>
#include"../headers/miscFunc.h"
#include"../headers/vdMiscFunc.h"
#include"../headers/vdAdd.h"
#include"../headers/vdAddFunc.h"

#include"../headers/define/all.h"

int main(int argc,char* argv[]){
	FILE *vdFile,*iFile;
	unsigned long iFileSize;

	vdFile = fopen(argv[1],"rb+");
	iFile = fopen(argv[2],"rb+");

	if(vdFile == NULL){
		perror("The virtual disk file could not be opened : ");
		return errno;
	}
	if(iFile == NULL){
		perror("The input file could not be inserted : ");
		return errno;
	}

	iFileSize = getFileSize(iFile);
	
	if(iFileSize > getAvailableFreeSpace(vdFile)){
		perror("Not enough free space available in the virtual disk");
		return -1;
	}

	addFile(vdFile,iFile,argv[2],iFileSize);
}

void addFile(FILE* vdFile,FILE* iFile,unsigned char* fileName,unsigned long iFileSize){
	unsigned char *metaData;
	unsigned long temp;
	
	temp = 0;
	metaData = (unsigned char*)malloc(METADATA_SIZE);

	fseek(vdFile,0,SEEK_SET);
	fread(metaData,METADATA_SIZE,1,vdFile);
	fseek(vdFile,METADATA_SIZE,SEEK_SET);
	parseFilePath(fileName);
	
	addFileToVD(vdFile,iFile,((unsigned long*)metaData)[3],iFileSize,fileName,generateFileOffset(iFileSize,((unsigned long*)metaData)[2]),metaData);

	fseek(vdFile,
		METADATA_NEXT_FREE_SPACE_POINTER_LOC,
		SEEK_SET);
		
	fwrite(metaData+METADATA_NEXT_FREE_SPACE_POINTER_LOC,
		METADATA_NEXT_FREE_SPACE_POINTER_SIZE,
		1,
		vdFile);
	
	fseek(vdFile,
		METADATA_END_POINTER_DATA_POINTER_LOC,
		SEEK_SET);
	
	fwrite(metaData+METADATA_END_POINTER_DATA_POINTER_LOC,
		METADATA_END_POINTER_DATA_POINTER_SIZE,
		1,
		vdFile);
	
	memcpy(&temp,
		metaData+METADATA_NUMBER_OF_FILES_POINTER_LOC,
		METADATA_NUMBER_OF_FILES_POINTER_SIZE);
		
	temp += 1;
	
	memcpy(metaData+METADATA_NUMBER_OF_FILES_POINTER_LOC,
		&temp,
		METADATA_NUMBER_OF_FILES_POINTER_SIZE);
	
	fwrite(metaData+METADATA_NUMBER_OF_FILES_POINTER_LOC,
		METADATA_NUMBER_OF_FILES_POINTER_SIZE,
		1,
		vdFile);
		
	free(metaData);
}
