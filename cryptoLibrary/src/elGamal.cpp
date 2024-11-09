#include<iostream>
#include<NTL/ZZ.h>
#include<NTL/ZZ_p.h>
#include<time.h>

#include"../headers/person.hpp"
#include"../headers/elGamal.hpp"

void ElGamal::setGenerator(NTL::ZZ_p g1){
	this->g = g1;
}

void ElGamal::setp(NTL::ZZ p1){
	this->p = p1;
	NTL::ZZ_p::init(p1);
}

ElGamal::ElGamal(NTL::ZZ p1,NTL::ZZ_p g1){
	this->setGenerator(g1);
	this->setp(p1);
}


//void ElGamal::generateKeys(PersonEG& A){
//	NTL::ZZ_p x;
//	pkey pubkey;
//
//	A.generateSecretKey();
//	pubkey.p = this->p;
//	pubkey.g = this->g;
//	pubkey.h = A.generategx(this->g);
//	A.setPublicKey(pubkey);
//}

c1c2 ElGamal::encrypt(NTL::ZZ_p m,PersonEG& A){
	NTL::ZZ_p y,gy,s;
	c1c2 output;

	y = NTL::random_ZZ_p();
	while(NTL::IsZero(y)) y = NTL::random_ZZ_p();

	gy = NTL::power(this->g,NTL::rep(y));
	s = NTL::power(A.publicKey.h,NTL::rep(y));

	output.c1 = gy;
	output.c2 = s*m;
	return output;
}

NTL::ZZ_p ElGamal::decrypt(c1c2 encoded,PersonEG& A){
	NTL::ZZ_p output;
	output = encoded.c2 * NTL::inv(A.generategx(encoded.c1));
	return output;
}

signature ElGamal::sign(NTL::ZZ_p m,PersonEG& A){
	signature output;
	NTL::ZZ_p::init(this->p-1);
	NTL::ZZ_p y;

	y = NTL::random_ZZ_p();
	while(NTL::GCD(NTL::rep(y),this->p-1) != 1) y = NTL::random_ZZ_p();

	NTL::ZZ_p::init(this->p);
	output.gamma = NTL::power(this->g,NTL::rep(y));
	NTL::ZZ_p::init(this->p-1);

	y = NTL::inv(y);
	output.delta = (m - A.multSecretKey(output.gamma))*y;

	NTL::ZZ_p::init(this->p);
	return output;
}

bool ElGamal::verify(PersonEG& A,NTL::ZZ_p m,signature signA){
	return NTL::power(A.publicKey.h,NTL::rep(signA.gamma))*NTL::power(signA.gamma,NTL::rep(signA.delta)) == NTL::power(this->g,NTL::rep(m));
}

