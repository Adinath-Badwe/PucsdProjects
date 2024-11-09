#include<iostream>
#include<NTL/ZZ.h>
#include<NTL/ZZ_p.h>

#include"../headers/cryptoLib.hpp"

// use dev/pool for selecting random seed for NTL

CryptoLibrary::CryptoLibrary(){
	srand(time(NULL));
	NTL::ZZ p;
	this->p = NTL::GenPrime_ZZ(100,80);

	NTL::ZZ_p::init(this->p);
	this->g = NTL::random_ZZ_p();
	
	this->elgamal = ElGamal(this->p,this->g);
	this->ellipticcurve = EllipticCurve(this->p);
	this->elgamalec = ElGamalEC(this->p,this->ellipticcurve);
	
	this->diffiehelman = DiffieHelman(this->p,this->g);
	
	this->personeg = PersonEG(this->p,this->g);
	this->persondh = PersonDH(this->p);
}

c1c2 CryptoLibrary::encrypt(NTL::ZZ_p m){
	return this->elgamal.encrypt(m,this->personeg);
}

NTL::ZZ_p CryptoLibrary::decrypt(c1c2 encoded){
	return this->elgamal.decrypt(encoded,this->personeg);
}

c1c2ecComp CryptoLibrary::encryptEC(NTL::ZZ_p m){
	return this->elgamalec.encrypt(m);
}

NTL::ZZ_p CryptoLibrary::decryptEC(c1c2ecComp encoded){
	return this->elgamalec.decrypt(encoded);
}

signatureEC CryptoLibrary::signEC(NTL::ZZ_p m){
	return this->elgamalec.sign(m);
}

bool CryptoLibrary::verifyEC(NTL::ZZ_p m,signatureEC signA){
	return this->elgamalec.verify(m,signA);
}
