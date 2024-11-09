
// vdAdd functions
unsigned int calculatePointerAndNameLength(unsigned long fileLength,unsigned int nameLength,unsigned long pointer);
void generatePointerAndName(unsigned char* pointerName,unsigned int pointerNameLength,unsigned long fileLength,unsigned char* name,unsigned long offset);
void writeToVD(FILE *vdFile,unsigned long pointerEndStartByte,unsigned char* writeFrom,unsigned long writeFromLength);
void writePointerAndName(FILE* vdFile,unsigned long pointerEndStartByte,unsigned long fileLength,unsigned char* name,unsigned long offset);
void addFileToVD(FILE* vdFile,FILE* iFile,unsigned long pointerEndStartByte,unsigned long fileLength,unsigned char* name,unsigned long offset,unsigned char* metaData);
void writeFile(FILE* vdFile,FILE* iFile,unsigned long offset);
unsigned long generateFileOffset(unsigned long fileLength,unsigned long dataStartPointer);
