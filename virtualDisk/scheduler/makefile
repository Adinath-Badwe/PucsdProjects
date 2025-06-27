
hello:
	@echo"main"

obj/main.o:src/main.c obj
	@gcc -c -g src/main.c -o obj/main.o
	
obj/scheduler.o:src/scheduler.c obj
	@gcc -c -g src/scheduler.c -o obj/scheduler.o

obj/vdfuncs.o:src/vdfuncs.c obj
	@gcc -c -g src/vdfuncs.c -o obj/vdfuncs.o

obj/getFreeBlocks.o:src/getFreeBlocks.c obj
	@gcc -c -g src/getFreeBlocks.c -o obj/getFreeBlocks.o

obj/createVirtualDisk.o:src/createVirtualDisk.c obj virtualDisk
	@gcc -c -g src/createVirtualDisk.c -o obj/createVirtualDisk.o

main:obj/main.o obj/createVirtualDisk.o obj/vdfuncs.o obj/scheduler.o obj/getFreeBlocks.o
	@gcc -g obj/main.o obj/createVirtualDisk.o obj/vdfuncs.o obj/scheduler.o obj/getFreeBlocks.o -o main

obj:
	@mkdir obj

virtualDisk:
	@mkdir virtualDisk
