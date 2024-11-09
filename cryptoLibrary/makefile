hello:
	@echo "Available : cryptoLib"

./obj:
	@mkdir obj

obj/diffieHelman.o:src/diffieHelman.cpp ./obj
	@g++ -c src/diffieHelman.cpp -o obj/diffieHelman.o

obj/elGamal.o:src/elGamal.cpp ./obj
	@g++ -c src/elGamal.cpp -o obj/elGamal.o

obj/cryptoLib.o:src/cryptoLib.cpp ./obj
	@g++ -c src/cryptoLib.cpp -o obj/cryptoLib.o

obj/person.o:src/person.cpp ./obj
	@g++ -c src/person.cpp -o obj/person.o

obj/main.o:src/main.cpp ./obj
	@g++ -c src/main.cpp -o obj/main.o

obj/ellipticCurve.o:src/ellipticCurve.cpp ./obj
	@g++ -c src/ellipticCurve.cpp -o obj/ellipticCurve.o

obj/elGamalEllipticCurve.o:src/elGamalEllipticCurve.cpp ./obj
	@g++ -c src/elGamalEllipticCurve.cpp -o obj/elGamalEllipticCurve.o

cryptoLib:obj/cryptoLib.o obj/elGamal.o obj/diffieHelman.o obj/person.o ./obj obj/ellipticCurve.o obj/elGamalEllipticCurve.o obj/main.o
	@g++ obj/cryptoLib.o obj/elGamal.o obj/diffieHelman.o obj/person.o obj/ellipticCurve.o obj/elGamalEllipticCurve.o obj/main.o -o cryptoLib -lntl -lgmp -lm
