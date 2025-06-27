
typedef struct nFileData{
	unsigned long fileLength;
	unsigned long fileNameLength;
	unsigned long fileNameLoc;
	unsigned long fileLoc;
	bool valid;
} nFileData;

typedef struct getpointerDataOutput {
	bool found;
	unsigned long docLoc;
	unsigned long fileLength;
} getPointerDataOutput;


// vdGet functions
getPointerDataOutput getPointerData(FILE* vdFile,unsigned char* fileName,unsigned long pointerEnd,unsigned long pointerStart);
nFileData getNthFileData(FILE* vdFile,unsigned int n,unsigned long pointerEnd,unsigned long pointerStart);
