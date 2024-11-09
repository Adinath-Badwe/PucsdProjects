hello:
	@echo "getFile64"

./obj/getFile64.o:./src/getFile64.cpp
	@g++ -g -c ./src/getFile64.cpp -o ./obj/getFile64.o

#getFile:getFile.o
#	g++ getFile.o -o getFile -lm

./obj:
	@mkdir obj

./obj/main64.o:./src/main64.cpp ./obj
	@g++ -g -c ./src/main64.cpp -o ./obj/main64.o

main64:./obj/main64.o ./obj/getFile64.o
	@g++ -g ./obj/main64.o ./obj/getFile64.o -o main64 -lm

clean:
	@rm ./obj/main64.o ./obj/getFile64.o main64
	@rmdir obj
	@rm sBlock.txt
	@rm block.txt
	@rm gd.txt
	@rm inode.txt

run:main64
	@sudo ./main64
