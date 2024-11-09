#include<iostream>
#include<NTL/ZZ.h>
#include<NTL/ZZ_p.h>

#include"../headers/person.hpp"

// diffieHelman
PersonDH::PersonDH(NTL::ZZ p){
	this->secretKey = NTL::random_ZZ_p();
}

void PersonDH::generateSharedKey(NTL::ZZ_p A1){
	this->sharedKey = NTL::power(A1,NTL::rep(this->secretKey));
}

NTL::ZZ_p PersonDH::generateA(NTL::ZZ_p g){
	return NTL::power(g,NTL::rep(this->secretKey));
}

//elGamal

PersonEG::PersonEG(NTL::ZZ p,NTL::ZZ_p g){
	pkey publicKey;
	publicKey.g = g;
	publicKey.p = p;
	this->secretKey = NTL::random_ZZ_p();
	
	publicKey.h = this->generategx(g);
	this->publicKey = publicKey;
}

NTL::ZZ_p PersonEG::generategx(NTL::ZZ_p g){
	return NTL::power(g,NTL::rep(this->secretKey));
}

NTL::ZZ_p PersonEG::multSecretKey(NTL::ZZ_p g){
	return this->secretKey*g;
}
