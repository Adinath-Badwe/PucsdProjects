#include"getFile.hpp"
#include<iostream>
#include<math.h>

int main(){
	FileSystem fileSystem;
	std::cout << fileSystem.getGroupNumFromInodeNum(12) << std::endl;
	std::cout << fileSystem.inodeBlocksPerGroup << std::endl;
	std::cout << fileSystem.numberOfGroups << std::endl;
	std::cout << fileSystem.numberOfBlocks << std::endl;
	std::cout << fileSystem.blockSize << std::endl;
	//fileSystem.getFile(13);
	//fileSystem.getFile(2359759);
	//fileSystem.getFile(57);
	
	//std::cout << ((unsigned int*)(fileSystem.inode+0x4))[0] << std::endl;
	
	//FILE* gdFile = fopen("allgd","wb");
	
	//fileSystem.setBlock(1048576);
	//fileSystem.setGroupDescriptor(1048576/fileSystem.blocksPerGroup);
	
	//for(int i = 0; i < 1048576/fileSystem.blocksPerGroup;i++){
	//	std::cout << i << std::endl;
	//	fileSystem.setGroupDescriptor(i);
	//	fwrite(fileSystem.groupDescriptor,sizeof(char),32,gdFile);
	//}
	
	//std::cout << "Number of blocks 1048576 " << fileSystem.numberOfBlocks << std::endl;
	fwrite(fileSystem.inode,1,fileSystem.inodeSize,fopen("inode.txt","wb"));
	fwrite(fileSystem.block,1,fileSystem.blockSize,fopen("block.txt","wb"));
	fwrite(fileSystem.groupDescriptor,1,32,fopen("gd.txt","wb"));
	fwrite(fileSystem.sBlock,1,1024,fopen("sBlock.txt","wb"));
	
	//std::cout << ((unsigned int*)(fileSystem.groupDescriptor + 0x8))[0] << std::endl;
}
