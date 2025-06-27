#pragma once

// if found is true, blockNumber gives the first free block found
// is found is false, blockNumber gives ( last_checked_blockNumber + 1)
typedef struct freeBlocks{
	char found;
	unsigned int blockNumber;
}freeBlocks;
