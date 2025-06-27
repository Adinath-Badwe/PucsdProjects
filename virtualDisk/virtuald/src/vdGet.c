#include<stdio.h>
#include"../headers/vdGet.h"
#include"../headers/vdMiscFunc.h"
#include"../headers/vdGetFunc.h"
#include"../headers/miscFunc.h"

#include"../headers/define/all.h"

int main(int argc,char* argv[]){
	FILE *vdFile,*oFile;
	vdFile = fopen(argv[1],"rb");
	oFile = fopen(argv[3],"wb");
	getFileVD(vdFile,argv[2],oFile);
}

void getFileVD(FILE* vdFile,unsigned char* iFileName,FILE* oFile){
	unsigned long pointerEnd;
	getPointerDataOutput output1;
	
	fseek(vdFile,METADATA_END_POINTER_DATA_POINTER_LOC,SEEK_SET);
	fread(&pointerEnd,METADATA_END_POINTER_DATA_POINTER_SIZE ,1,vdFile);
	fseek(vdFile,METADATA_SIZE,SEEK_SET);

	output1 = getPointerData(vdFile,iFileName,pointerEnd,METADATA_SIZE);
	
	if(output1.found == true){
		fseek(vdFile,output1.docLoc,SEEK_SET);
		unsigned long length1;

		char buffer[BUFFER_SIZE];
		while(true){
			if(BUFFER_SIZE < output1.fileLength){
				length1 = fread(buffer,sizeof(char),BUFFER_SIZE,vdFile);
				fwrite(buffer,sizeof(char),length1,oFile);
				output1.fileLength -= BUFFER_SIZE;
			}else{
				fread(buffer,sizeof(char),output1.fileLength,vdFile);
				fwrite(buffer,sizeof(char),output1.fileLength,oFile);
				output1.fileLength = 0;
				break;
			}
		}
	}
}
