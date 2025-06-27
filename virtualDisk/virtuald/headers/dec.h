
# define MIN(a,b) ((a) < (b) ? (a): (b))

typedef struct decoded {
	unsigned long length;
	unsigned long bytesRead;
} decodedData;

void writeFromRight(unsigned long *current,unsigned char *byte,unsigned long* currentRead,unsigned char *bitsLeft,unsigned char bitsToWrite);
unsigned long decode(unsigned char* sseq,unsigned long sseqLen);
decodedData decode1(unsigned char* sseq,unsigned long sseqLen);
int decodeFile(unsigned char* iFilePath,unsigned char* oFilePath);
