#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include"../headers/vdAddFunc.h"
#include"../headers/miscFunc.h"
#include"../headers/enc.h"

// calculatePointerNameLength takes filelength(length of file in bytes) and nameLength(length of name string in bytes) and gives out the space required to encode both of them together in bytes.

unsigned int calculatePointerAndNameLength(unsigned long fileLength,unsigned int nameLength,unsigned long pointer){
	unsigned int spaceRequired;
	spaceRequired = bytesRequiredEncoding(fileLength) + bytesRequiredEncoding(nameLength) + nameLength + bytesRequiredMinimum(pointer) + bytesRequiredEncoding(bytesRequiredMinimum(pointer));
	return spaceRequired;
}

void generatePointerAndName(unsigned char* pointerName,unsigned int pointerNameLength,unsigned long fileLength,unsigned char* name,unsigned long offset){
	unsigned int currOffset = 0;

	encodeSeqLen(pointerName + currOffset,strlen(name)); // copy the filename length encoding

	currOffset += (bytesRequiredEncoding(strlen(name)));
	memcpy(pointerName+currOffset,name,strlen(name)); // copy the file name

	currOffset += strlen(name);
	encodeSeqLen(pointerName+currOffset,fileLength); // copy the encoded filelength

	currOffset += (bytesRequiredEncoding(fileLength));
	encodeSeqLen(pointerName+currOffset,bytesRequiredMinimum(offset)); // copy encoded location/address size

	currOffset += (bytesRequiredEncoding(bytesRequiredMinimum(offset)));
	memcpy(pointerName+currOffset,&offset,bytesRequiredMinimum(offset)); // copy the location/address of the file
}

// writeToVD takes a file pointer and a pointerEndStartByte(address/location to write to, in file) and writeFrom(encoded sequence which contains filelength,nameLength,name) and (writeFromLength) and writes the contents of writeFrom to filepointer at location starting from pointerEndStartByte
void writeToVD(FILE *vdFile,unsigned long pointerEndStartByte,unsigned char* writeFrom,unsigned long writeFromLength){
	fseek(vdFile,pointerEndStartByte,SEEK_SET);
	fwrite(writeFrom,sizeof(char),writeFromLength,vdFile);
}

void addFileToVD(FILE* vdFile,FILE* iFile,unsigned long pointerEndStartByte,unsigned long fileLength,unsigned char* name,unsigned long offset,unsigned char* metaData){
	writePointerAndName(vdFile,pointerEndStartByte,fileLength,name,offset);
	writeFile(vdFile,iFile,offset);

	((unsigned long*)metaData)[3] += calculatePointerAndNameLength(fileLength,strlen(name),offset);
	((unsigned long*)metaData)[2] = offset;
}

void writeFile(FILE* vdFile,FILE* iFile,unsigned long offset){
	unsigned char buffer[4096];
	unsigned short bytesRead;
	fseek(vdFile,offset,SEEK_SET);

	while(bytesRead = fread(buffer,sizeof(char),4096,iFile)){
		fwrite(buffer,sizeof(char),bytesRead,vdFile);
	}

}

// writePointerAndName takes a filepointer, the end of pointerdata, the filelength,name of file,and file offset(from start)
void writePointerAndName(FILE* vdFile,unsigned long pointerEndStartByte,unsigned long fileLength,unsigned char* name,unsigned long offset){
	unsigned char* pointerName;
	unsigned int pointerNameLength = calculatePointerAndNameLength(fileLength,strlen(name),offset);
	pointerName = (unsigned char*)malloc(pointerNameLength);
	generatePointerAndName(pointerName,pointerNameLength,fileLength,name,offset);
	writeToVD(vdFile,pointerEndStartByte,pointerName,pointerNameLength);
	free(pointerName);
}

