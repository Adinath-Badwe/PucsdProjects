hello:main

./obj/getFile.o:./src/getFile.cpp
	@g++ -g -c ./src/getFile.cpp -o ./obj/getFile.o

./obj:
	@mkdir obj

./obj/main.o:./src/main.cpp ./obj
	@g++ -g -c ./src/main.cpp -o ./obj/main.o

main:./obj/main.o ./obj/getFile.o
	@g++ -g ./obj/main.o ./obj/getFile.o -o main -lm
