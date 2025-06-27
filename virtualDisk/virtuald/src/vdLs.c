#include<stdio.h>
#include<stdlib.h>
#include"../headers/vdMiscFunc.h"
#include"../headers/vdLs.h"
#include"../headers/vdGetFunc.h"
#include"../headers/miscFunc.h"

int main(int argc, char* argv[]){
	FILE* vdFile;
	vdFile = fopen(argv[1],"rb");
	nFileData file1;
	unsigned int numFiles;
	unsigned long pointerEnd,metaDataSize;
	unsigned char* fileName;

	fread(&metaDataSize,sizeof(long),1,vdFile);
	fseek(vdFile,24,SEEK_SET);
	fread(&pointerEnd,sizeof(long),1,vdFile);
	fseek(vdFile,32,SEEK_SET);
	fread(&numFiles,sizeof(int),1,vdFile);
	fseek(vdFile,metaDataSize,SEEK_SET);

	for(unsigned int i = 0; i < numFiles;i++){
		file1 = getNthFileData(vdFile,i,pointerEnd,metaDataSize);
		fileName = (unsigned char*)malloc(file1.fileNameLength+1);
		fileName[file1.fileNameLength] = 0;
		fseek(vdFile,file1.fileNameLoc,SEEK_SET);
		fread(fileName,sizeof(char),file1.fileNameLength,vdFile);
		printf("%u : %s\n",i+1,fileName);
		free(fileName);
	}
}
