#pragma once
#include"../headers/structs.h"

// runScheduler takes a virtual disk file pointer and state file pointer and starts the execution of tasks
void runScheduler(FILE* vdFile,FILE* stateFile);
// scheduleTask schedules task in the jobQueue depending on given input parameters
void scheduleTask(unsigned char* jobQueue,unsigned char* nextJobIndex,unsigned char* jobsInQueue,unsigned char* lastAssignedTask);
// executeTask executes the task at jobQueue[*nextJobIndex] and modifies stateFile accordingly
void executeTask(FILE* stateFile,unsigned char* jobQueue,unsigned char *nextJobIndex,unsigned char* jobsInQueue);
void dummyTask();

// load the state of given processCode from stateFile into the stateArr
void loadState(FILE *stateFile,unsigned char *stateArr,unsigned char processCode);
// store the state of given processCode from stateArr into the stateFile
void storeState(FILE *stateFile,unsigned char *stateArr,unsigned char processCode);
unsigned long getProcessStateLoc(unsigned char processCode);
unsigned long getProcessStateSpace(unsigned char processCode);
// initialise the stateFile with the given process codes in the processCodeList
void initialiseStateFile(FILE* stateFile,unsigned char *processCodeList,unsigned char numberOfProcesses);
