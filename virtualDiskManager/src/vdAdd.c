#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<stdbool.h>
#include<errno.h>
#include"../headers/miscFunc.h"
#include"../headers/vdMiscFunc.h"
#include"../headers/vdAdd.h"
#include"../headers/vdAddFunc.h"

typedef union tempData{
	unsigned long l;
	unsigned int ui[2];
	unsigned short us[4];
	unsigned char uc[8];
} tempData;

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

void addFile(FILE* vdFile,FILE* iFile,unsigned char* fileName,unsigned long iFileSize ){
	tempData temp;
	unsigned char *metaData;

	fread(&(temp.l),sizeof(long),1,vdFile);
	fseek(vdFile,0,SEEK_SET);
	metaData = (unsigned char*)malloc(temp.l);
	fread(metaData,temp.l,1,vdFile);
	fseek(vdFile,((long*)metaData)[0],SEEK_SET);
	parseFilePath(fileName);
	
	addFileToVD(vdFile,iFile,((unsigned long*)metaData)[3],iFileSize,fileName,generateFileOffset(iFileSize,((unsigned long*)metaData)[2]),metaData);

	fseek(vdFile,2*(sizeof(long)),SEEK_SET);
	fwrite(((unsigned long*)metaData)+2,sizeof(long),1,vdFile);
	fseek(vdFile,3*(sizeof(long)),SEEK_SET);
	fwrite(((unsigned long*)metaData)+3,sizeof(long),1,vdFile);
	((unsigned long*)metaData)[4] += 1;
	fwrite(((unsigned long*)metaData)+4,sizeof(unsigned int),1,vdFile);
	free(metaData);
}
