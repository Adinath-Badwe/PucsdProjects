#include<iostream>
#include"../headers/cryptoLib.hpp"

int main(){
	CryptoLibrary crypto;
	c1c2ecComp encoded;
	NTL::ZZ_p message;
	message = 720;
	encoded = crypto.encryptEC(message);
	std::cout << std::endl;
	std::cout << crypto.decryptEC(encoded)<< std::endl;
	//EllipticCurve ec;
	//point P;
	//NTL::ZZ p;
	//p = 11;
	//NTL::ZZ_p::init(p);
	//ec.p = p;
	//ec.a = 1;
	//ec.b = 6;
	//P.x = 2;
	//P.y = 7;
	//point Z;
	//NTL::ZZ_p mess;
	//mess = 7;
	//std::cout << Z.x << std::endl << Z.y << std::endl;
}
