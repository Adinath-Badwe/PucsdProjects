#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include"../headers/vdfuncs.h"
#include"../headers/scheduler.h"
#include"../headers/define/scheduler.h"
#include"../headers/define/all.h"
#include"../headers/getFreeBlocks.h"
#include"../headers/structs.h"

void runScheduler(FILE* vdFile,FILE* stateFile){
	// jobQueue is an array of characters where each character represents the job id
	// processCodeList is an array of characters which is used in initialisation of each process' state
	unsigned char* jobQueue,*processCodeList;
	// nextJobIndex gives the index value in jobQueue to be executed next
	// jobsInQueue gives how many tasks in jobQueue have been scheduled
	unsigned char running,nextJobIndex,jobsInQueue;
	
	// initialise the values of nextJobIndex and jobsInQueue
	nextJobIndex = 0;
	jobsInQueue = 0;
	
	// allocate memory for jobQueue and processCodeList and initialise values 
	jobQueue = (unsigned char*)malloc(MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE);
	processCodeList = (unsigned char*)malloc(MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE);
	memset(jobQueue,0,MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE);
	
	processCodeList[0] = 0;
	processCodeList[1] = 1;
	
	// initialise the states of each process in the stateFile
	initialiseStateFile(stateFile,processCodeList,DISTINCT_NUMBER_OF_TASKS);
	
	running = 1;
	while(running){
		// execute the task with id given at jobQueue[nextJobIndex]
		executeTask(stateFile,jobQueue,&nextJobIndex,&jobsInQueue);
		// decrement the number of tasks present in the queue
		jobsInQueue = (jobsInQueue - 1) % MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE;
		// increment the job index
		nextJobIndex = (nextJobIndex + 1) % MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE;
	}
}

void scheduleTask(unsigned char* jobQueue,unsigned char* nextJobIndex,unsigned char* jobsInQueue,unsigned char* lastAssignedTask){
	// i is an iterator
	// jobsInQueueAtStart stores the number of jobs that were present in jobQueue at start of this function
	unsigned char i,jobsInQueueAtStart;
	
	jobsInQueueAtStart = *jobsInQueue;
	
	/*
	if((*jobsInQueue) == 0){
		(*jobsInQueue) += 1;
		jobQueue[(*nextJobIndex) % MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE] = TASK_ID_GET_FREE_BLOCKS;
		(*lastAssignedTask) = TASK_ID_GET_FREE_BLOCKS;
	}
	*/
	i = 0;
	
	while(((*jobsInQueue) < MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE) && (i < 5)){
		//printf("TASK TO BE SCHEDULED : %d\n",((*lastAssignedTask) + 1) % DISTINCT_NUMBER_OF_TASKS);
		
		// schedule a task 
		jobQueue[(*nextJobIndex)+ jobsInQueueAtStart - 1 + i % MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE] = ((*lastAssignedTask) + 1) % DISTINCT_NUMBER_OF_TASKS;
		
		(*jobsInQueue) += 1;
		(*jobsInQueue) = (*jobsInQueue) % MAXIMUM_NUMBER_OF_TASKS_ENQUEUEABLE;
		(*lastAssignedTask) += 1;
		(*lastAssignedTask) = (*lastAssignedTask) % DISTINCT_NUMBER_OF_TASKS;
		i += 1;
	}
}

void executeTask(FILE* stateFile,unsigned char* jobQueue,unsigned char *nextJobIndex,unsigned char* jobsInQueue){
	// stateArr is an array which contains the state of a process at given time
	unsigned char* stateArr;
	// stateArrInit is a flag which stores whether stateArr has been allocated. In case some functions do not require state maintenance
	unsigned char stateArrInit;
	// open the virtual disk
	FILE* vdFile = fopen("./virtualDisk/virtualDisk.vbin","rb");
	
	
	stateArrInit = 0;
	switch (jobQueue[*nextJobIndex]){
		// task of scheduling tasks
		case TASK_ID_SCHEDULE_TASK:
			unsigned char lastAssignedTask;
			
			lastAssignedTask = 0;
			stateArr = (unsigned char*)malloc(TASK_STATE_SPACE_REQUIRED_SCHEDULE_TASK);
			stateArrInit = 1;
			
			// load the last state of this task
			loadState(stateFile,stateArr,TASK_ID_SCHEDULE_TASK);
			
			// load important variables from the stateArray
			memcpy(&lastAssignedTask,stateArr+TASK_STATE_SCHEDULE_TASK_LAST_ASSIGNED_TASK_LOC,TASK_STATE_SCHEDULE_TASK_LAST_ASSIGNED_TASK_SIZE);
			
			// run the task
			scheduleTask(jobQueue,nextJobIndex,jobsInQueue,&lastAssignedTask);
			
			// store important variables back into the stateArray
			memcpy(stateArr+TASK_STATE_SCHEDULE_TASK_LAST_ASSIGNED_TASK_LOC,&lastAssignedTask,TASK_STATE_SCHEDULE_TASK_LAST_ASSIGNED_TASK_SIZE);
			
			// store the state back to the state file
			storeState(stateFile,stateArr,TASK_ID_SCHEDULE_TASK);
			break;
			
		// task of finding the first free block
		case TASK_ID_GET_FREE_BLOCKS:
			freeBlocks freeB;
			unsigned int nextBlockToRead;
			
			// inititalise stateArray
			stateArr = (unsigned char*)malloc(TASK_STATE_SPACE_REQUIRED_GET_FREE_BLOCKS);
			stateArrInit = 1;
			nextBlockToRead = 0;
			
			// load the stateArr from stateFile
			loadState(stateFile,stateArr,TASK_ID_GET_FREE_BLOCKS);
			
			// load important variables from the stateArray
			memcpy(&nextBlockToRead,
				stateArr+TASK_STATE_GET_FREE_BLOCKS_NEXT_BLOCK_TO_READ_LOC,
				TASK_STATE_GET_FREE_BLOCKS_NEXT_BLOCK_TO_READ_SIZE);
			
			
			// run the task and generate output
			freeB = getFreeBlock(vdFile,nextBlockToRead,64);
			
			// if free block is found
			if(freeB.found){
				freeB.blockNumber += 1;
			}
			
			// store important variables back into the state array
			memcpy(stateArr+TASK_STATE_GET_FREE_BLOCKS_NEXT_BLOCK_TO_READ_LOC,
				&(freeB.blockNumber),TASK_STATE_GET_FREE_BLOCKS_NEXT_BLOCK_TO_READ_SIZE);
			
			// store the stateArray back into the stateFile
			storeState(stateFile,stateArr,TASK_ID_GET_FREE_BLOCKS);
			break;
		
		case TASK_ID_DUMMY_TASK:
			dummyTask();
			
			break;
		default:
			printf("Invalid TASK ID\n");
			return;
		
	}
	
	// free the stateArray space if it was allocated
	if(stateArrInit) free(stateArr);
	
	fclose(vdFile);
}

void loadState(FILE *stateFile,unsigned char *stateArr,unsigned char processCode){
	if(processCode < DISTINCT_NUMBER_OF_TASKS){
		fseek(stateFile,getProcessStateLoc(processCode),SEEK_SET);
		fread(stateArr,getProcessStateSpace(processCode),1,stateFile);
	}else{
		printf("INVALID CODE\n");
	}
}

void storeState(FILE *stateFile,unsigned char *stateArr,unsigned char processCode){
	if(processCode < DISTINCT_NUMBER_OF_TASKS){
		fseek(stateFile,getProcessStateLoc(processCode),SEEK_SET);
		fwrite(stateArr,getProcessStateSpace(processCode),1,stateFile);
	}else{
		printf("INVALID CODE\n");
	}
}

// getProcessStateLoc takes proccessCode(ID) and gives the byte number in stateFile from where the state of given process starts
unsigned long getProcessStateLoc(unsigned char processCode){
	switch (processCode){
		case TASK_ID_SCHEDULE_TASK:
			return TASK_STATE_SCHEDULE_TASK_LOC;
		case TASK_ID_GET_FREE_BLOCKS:
			return TASK_STATE_GET_FREE_BLOCKS_LOC;
	}
}

// getProcessStateSize takes proccessCode(ID) and gives the number of bytes taken by given process' state
unsigned long getProcessStateSpace(unsigned char processCode){
	switch (processCode){
		case TASK_ID_SCHEDULE_TASK:
			return TASK_STATE_SPACE_REQUIRED_SCHEDULE_TASK;
		case TASK_ID_GET_FREE_BLOCKS:
			return TASK_STATE_SPACE_REQUIRED_GET_FREE_BLOCKS;
	}
}

// initialiseStateFile takes initialises the state of processes', the id of which is store in processCodeList, in the stateFile
void initialiseStateFile(FILE* stateFile,unsigned char *processCodeList,unsigned char numberOfProcesses){
	unsigned char *stateArr;
	unsigned long temp;
	temp = 0;
	for(unsigned char i = 0; i < numberOfProcesses;i++){
		switch (processCodeList[i]){
		
		case TASK_ID_SCHEDULE_TASK:
			temp = 0;
			stateArr = (unsigned char*)malloc(TASK_STATE_SPACE_REQUIRED_SCHEDULE_TASK);
			
			// lastAssignedTask written to state
			temp = 0;
			memcpy(stateArr+TASK_STATE_SCHEDULE_TASK_LAST_ASSIGNED_TASK_LOC,&temp,TASK_STATE_SCHEDULE_TASK_LAST_ASSIGNED_TASK_SIZE);
			
			// write state array to state file 
			fseek(stateFile,getProcessStateLoc(TASK_ID_SCHEDULE_TASK),SEEK_SET);
			fwrite(stateArr,TASK_STATE_SPACE_REQUIRED_SCHEDULE_TASK,1,stateFile);
			
			break;
		case TASK_ID_GET_FREE_BLOCKS:
			stateArr = (unsigned char*)malloc(TASK_STATE_SPACE_REQUIRED_GET_FREE_BLOCKS);
			
			// next block to read written to state
			temp = 0;
			memcpy(stateArr+TASK_STATE_GET_FREE_BLOCKS_NEXT_BLOCK_TO_READ_LOC,&temp,TASK_STATE_GET_FREE_BLOCKS_NEXT_BLOCK_TO_READ_SIZE);
			
			// write state array to state file
			fseek(stateFile,getProcessStateLoc(TASK_ID_GET_FREE_BLOCKS),SEEK_SET);
			fwrite(stateArr,TASK_STATE_SPACE_REQUIRED_GET_FREE_BLOCKS,1,stateFile);
			
			break;
		default:
			return;
		}
	}
	
	free(stateArr);
}

void dummyTask(){
	return;
}
