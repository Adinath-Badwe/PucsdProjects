#all: vdLs vdCreate vdAdd vdGet
functions:=vdLs vdCreate vdAdd vdGet

hello:
	@echo "Current Available Functions :" $(functions)
	@mkdir obj
all:vdLs vdCreate vdAdd vdGet

obj/vdMiscFunc.o:src/vdMiscFunc.c
	gcc -c src/vdMiscFunc.c -o obj/vdMiscFunc.o

obj/vdAddFunc.o:src/vdAddFunc.c
	gcc -c src/vdAddFunc.c -o obj/vdAddFunc.o

obj/vdGetFunc.o:src/vdGetFunc.c
	gcc -c src/vdGetFunc.c -o obj/vdGetFunc.o

obj/dec.o:src/dec.c
	gcc -c src/dec.c -o obj/dec.o

obj/miscFunc.o:src/miscFunc.c
	gcc -c src/miscFunc.c -o obj/miscFunc.o

obj/enc.o:src/enc.c
	gcc -c src/enc.c -o obj/enc.o

obj/vdLs.o:src/vdLs.c
	gcc -c src/vdLs.c -o obj/vdLs.o

vdLs:obj/vdLs.o obj/vdMiscFunc.o obj/vdGetFunc.o obj/dec.o obj/enc.o obj/miscFunc.o
	gcc obj/vdLs.o obj/vdMiscFunc.o obj/vdGetFunc.o obj/dec.o obj/enc.o obj/miscFunc.o -o vdLs -lm

obj/vdCreate.o:src/vdCreate.c
	gcc -c src/vdCreate.c -o obj/vdCreate.o

vdCreate:obj/vdCreate.o obj/vdMiscFunc.o obj/dec.o obj/enc.o obj/miscFunc.o
	gcc obj/vdCreate.o obj/vdMiscFunc.o obj/dec.o obj/enc.o obj/miscFunc.o -o vdCreate -lm

obj/vdAdd.o:src/vdAdd.c
	gcc -c src/vdAdd.c -o obj/vdAdd.o

vdAdd:obj/vdAdd.o obj/vdMiscFunc.o obj/vdAddFunc.o obj/dec.o obj/enc.o obj/miscFunc.o
	gcc obj/vdAdd.o obj/vdMiscFunc.o obj/vdAddFunc.o obj/dec.o obj/enc.o obj/miscFunc.o -o vdAdd -lm

obj/vdGet.o:src/vdGet.c
	gcc -c src/vdGet.c -o obj/vdGet.o

vdGet:obj/vdGet.o obj/vdMiscFunc.o obj/vdGetFunc.o obj/dec.o obj/enc.o obj/miscFunc.o
	gcc obj/vdGet.o obj/vdMiscFunc.o obj/vdGetFunc.o obj/dec.o obj/enc.o obj/miscFunc.o -o vdGet -lm

#clean:
#	rm vdGet.o vdMiscFunc.o dec.o enc.o vdGetFunc.o vdAddFunc.o miscFunc.o vdAdd.o vdCreate.o vdLs.o vdGet vdAdd vdCreate vdLs
