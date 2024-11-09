#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include"../headers/vdMiscFunc.h"
#include"../headers/enc.h"
#include"../headers/dec.h"
#include"../headers/miscFunc.h"
#include<stdbool.h>

// takes filelength and the datapointer and gives out the location to write the file in virtual disk
unsigned long generateFileOffset(unsigned long fileLength,unsigned long dataStartPointer){
	return dataStartPointer - fileLength;
}

// getAvailableFreeSpace takes a vdFile pointer and gives out the available free space in the virtual disk
unsigned long getAvailableFreeSpace(FILE *vdFile){
	unsigned long pointerEnd,dataStart,vdfilepos;

	vdfilepos = ftell(vdFile);
	fseek(vdFile,24,SEEK_SET);
	fread(&pointerEnd,sizeof(long),1,vdFile);
	fseek(vdFile,16,SEEK_SET);
	fread(&dataStart,sizeof(long),1,vdFile);
	fseek(vdFile,vdfilepos,SEEK_SET);

	if(pointerEnd >= dataStart){
		return 0;
	}
	return dataStart-pointerEnd;
}

