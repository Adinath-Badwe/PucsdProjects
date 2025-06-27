#include<stdio.h>
#include<stdbool.h>

typedef struct indexSize {
	unsigned long index;
	unsigned char size;
} indexSize;

unsigned long getAvailableFreeSpace(FILE *vdFile);
unsigned long generateFileOffset(unsigned long fileLength,unsigned long dataStartPointer);
