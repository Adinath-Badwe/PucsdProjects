#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include<stdbool.h>
#include"../headers/vdMiscFunc.h"
#include"../headers/enc.h"
#include"../headers/dec.h"
#include"../headers/miscFunc.h"

#include"../headers/define/all.h"

// takes filelength and the datapointer and gives out the location to write the file in virtual disk
unsigned long generateFileOffset(unsigned long fileLength,unsigned long dataStartPointer){
	return dataStartPointer - fileLength;
}

// getAvailableFreeSpace takes a vdFile pointer and gives out the available free space in the virtual disk
unsigned long getAvailableFreeSpace(FILE *vdFile){
	unsigned long pointerEnd,dataStart,vdfilepos;

	vdfilepos = ftell(vdFile);
	fseek(vdFile,METADATA_END_POINTER_DATA_POINTER_LOC,SEEK_SET);
	fread(&pointerEnd,METADATA_END_POINTER_DATA_POINTER_SIZE,1,vdFile);
	
	fseek(vdFile,METADATA_NEXT_FREE_SPACE_POINTER_LOC,SEEK_SET);
	fread(&dataStart,METADATA_NEXT_FREE_SPACE_POINTER_SIZE,1,vdFile);
	fseek(vdFile,vdfilepos,SEEK_SET);

	printf("%d\n",pointerEnd);
	printf("%d\n",dataStart);
	if(pointerEnd >= dataStart){
		return 0;
	}
	return dataStart-pointerEnd;
}

