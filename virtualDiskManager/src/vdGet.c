#include<stdio.h>
#include"../headers/vdGet.h"
#include"../headers/vdMiscFunc.h"
#include"../headers/vdGetFunc.h"
#include"../headers/miscFunc.h"

int main(int argc,char* argv[]){
	FILE *vdFile,*oFile;
	vdFile = fopen(argv[1],"rb");
	oFile = fopen(argv[3],"wb");
	getFileVD(vdFile,argv[2],oFile);
}

void getFileVD(FILE* vdFile,unsigned char* iFileName,FILE* oFile){
	unsigned long metaDataSize,pointerEnd;
	getPointerDataOutput output1;
	fread(&metaDataSize,sizeof(long),1,vdFile);
	fseek(vdFile,24,SEEK_SET);
	fread(&pointerEnd,sizeof(long),1,vdFile);
	fseek(vdFile,metaDataSize,SEEK_SET);

	output1 = getPointerData(vdFile,iFileName,pointerEnd,metaDataSize);
	if(output1.found == true){
		fseek(vdFile,output1.docLoc,SEEK_SET);
		unsigned long length1;

		char buffer[1024];
		while(true){
			if(1024 < output1.fileLength){
				length1 = fread(buffer,sizeof(char),1024,vdFile);
				fwrite(buffer,sizeof(char),length1,oFile);
				output1.fileLength -= 1024;
			}else{
				fread(buffer,sizeof(char),output1.fileLength,vdFile);
				fwrite(buffer,sizeof(char),output1.fileLength,oFile);
				output1.fileLength = 0;
				break;
			}
		}
	}
}
