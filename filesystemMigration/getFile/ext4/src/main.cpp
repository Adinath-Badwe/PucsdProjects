#include"../headers/ext4.hpp"
#include<iostream>
#include<math.h>

int main(){
	ext4FileSystem fileSystem;
	//FILE* inputFile = fopen("./output/fileOutput123.txt","r");
	fileSystem.findExtent(0);
	
	//fwrite(fileSystem.block,1,fileSystem.blockSize,ofile);
	//printf("fileSystem : %d",fileSystem.inodesPerGroup);
	
	//fileSystem.getFile((long)2369331);
}
