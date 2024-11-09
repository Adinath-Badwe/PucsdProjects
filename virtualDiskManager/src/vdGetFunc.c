#include<string.h>
#include"../headers/vdMiscFunc.h"
#include"../headers/vdGetFunc.h"
#include<stdio.h>
#include<stdlib.h>
#include"../headers/dec.h"

// getNthFileData takes vdFile which is the virtual disk file pointer
// n, which is the file number. 0 <= n < noOfFiles
// pointerEnd, which marks the end of the pointerData
// pointerStart, the location to start searching ahead from in the vdfile.
// it gives out the data of the nth file in the vdfile.
nFileData getNthFileData(FILE* vdFile,unsigned int n,unsigned long pointerEnd,unsigned long pointerStart){
	fseek(vdFile,pointerStart,SEEK_SET);
	nFileData output1;
	unsigned long location;
	unsigned char* someSpace = (unsigned char*)malloc(32);
	decodedData dec1;
	output1.valid = false;

	for(unsigned int i = 0; i < n+1; i++){
		output1.valid = true;
		location = ftell(vdFile);
		if( location > pointerEnd){
			break;
		}
		fread(someSpace,sizeof(char),32,vdFile);
		fseek(vdFile,location,SEEK_SET);
		dec1 = decode1(someSpace,32);

		output1.fileNameLength = dec1.length;
		output1.fileNameLoc = location + dec1.bytesRead;

		fseek(vdFile,dec1.bytesRead+dec1.length,SEEK_CUR);

		location = ftell(vdFile);
		fread(someSpace,sizeof(char),32,vdFile);
		fseek(vdFile,location,SEEK_SET);
		dec1 = decode1(someSpace,32);
		output1.fileLength = dec1.length;

		//fseek(vdFile,dec1.bytesRead,SEEK_CUR);
		//fread(&(output1.fileLoc),sizeof(long),1,vdFile);
		fseek(vdFile,dec1.bytesRead,SEEK_CUR);
		location = ftell(vdFile);
		fread(someSpace,sizeof(char),32,vdFile);
		fseek(vdFile,location,SEEK_SET);
		dec1 = decode1(someSpace,32);
		fseek(vdFile,dec1.bytesRead,SEEK_CUR);
		fread(&(output1.fileLoc),dec1.length,1,vdFile);
	}

	free(someSpace);
	return output1;
}

// getPointerData takes a vdFile, file pointer to the virtual disk.
// filename, to match
// pointerEnd marks the end of the pointerData
// pointerStart gives the location to start searching for in the virtual disk
getPointerDataOutput getPointerData(FILE* vdFile,unsigned char* fileName,unsigned long pointerEnd,unsigned long pointerStart){
	fseek(vdFile,pointerStart,SEEK_SET);
	bool found = false;
	unsigned int length1;
	unsigned long location;
	unsigned char* someSpace = (unsigned char*)malloc(32);
	decodedData dec1;
	getPointerDataOutput dataOutput;
	bool endloop = false;
	unsigned char *fileNameSpace;

	location = ftell(vdFile);

	dataOutput.found = false;

	fread(someSpace,sizeof(char),32,vdFile);
	fseek(vdFile,location,SEEK_SET);

	while (location <= pointerEnd && (found == false)){
		location = ftell(vdFile);
		fread(someSpace,sizeof(char),32,vdFile);
		fseek(vdFile,location,SEEK_SET);
		dec1 = decode1(someSpace,32);

		fseek(vdFile,dec1.bytesRead,SEEK_CUR);
		fileNameSpace = (unsigned char*)malloc(dec1.length+1);
		fileNameSpace[dec1.length] = 0;

		fread(fileNameSpace,sizeof(char),dec1.length,vdFile);

		if (strcmp(fileNameSpace,fileName) == 0 ){
			found = true;
		}

		location = ftell(vdFile);
		fread(someSpace,sizeof(char),32,vdFile);
		fseek(vdFile,location,SEEK_SET);
		dec1 = decode1(someSpace,32);
		fseek(vdFile,dec1.bytesRead,SEEK_CUR);

		if(found == true){
			dataOutput.found = true;
			dataOutput.fileLength = dec1.length;
			//fread(&(dataOutput.docLoc),sizeof(long),1,vdFile);
			location = ftell(vdFile);
			fread(someSpace,sizeof(char),32,vdFile);
			fseek(vdFile,location,SEEK_SET);
			dec1 = decode1(someSpace,32);
			fseek(vdFile,dec1.bytesRead,SEEK_CUR);
			fread(&(dataOutput.docLoc),dec1.length,1,vdFile);
		}else{
			//fseek(vdFile,8,SEEK_CUR);
			location = ftell(vdFile);
			fread(someSpace,sizeof(char),32,vdFile);
			fseek(vdFile,location,SEEK_SET);
			dec1 = decode1(someSpace,32);
			fseek(vdFile,dec1.bytesRead+dec1.length,SEEK_CUR);
		}
		free(fileNameSpace);
	}

	free(someSpace);
	return dataOutput;
}
