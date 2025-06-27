#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include"../headers/scheduler.h"

int main(int argc,char* argv[]){
	//createVirtualDisk(64,1024*8);
	FILE* vdFile = fopen("./virtualDisk/virtualDisk.vbin","rb");
	FILE* stateFile= fopen("./virtualDisk/stateFile.sts","wb+");
	runScheduler(vdFile,stateFile);
}
