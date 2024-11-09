hello:
	@echo "getFile"

getFile.o:getFile.cpp
	g++ -g -c getFile.cpp -o getFile.o

#getFile:getFile.o
#	g++ getFile.o -o getFile -lm

main.o:main.cpp
	g++ -g -c main.cpp -o main.o

main:main.o getFile.o
	g++ -g main.o getFile.o -o main -lm
