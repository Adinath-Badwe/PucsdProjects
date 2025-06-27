hello:
	@echo "main"

./obj/ext4.o:./src/ext4.cpp
	@g++ -g -c ./src/ext4.cpp -o ./obj/ext4.o

./obj:
	@mkdir obj

./obj/main.o:./src/main.cpp ./obj
	@g++ -g -c ./src/main.cpp -o ./obj/main.o

main:./obj/main.o ./obj/ext4.o output
	@g++ -g ./obj/main.o ./obj/ext4.o -o main -lm

output:
	@mkdir output
	
clean:
	@rm ./obj/main.o ./obj/ext4.o main
	@rmdir obj

run:main
	@sudo ./main
