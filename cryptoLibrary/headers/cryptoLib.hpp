#pragma once
#include<NTL/ZZ.h>
#include<NTL/ZZ_p.h>
#include"../headers/person.hpp"
#include"../headers/elGamal.hpp"
#include"../headers/cryptoLib.hpp"
#include"../headers/diffieHelman.hpp"
#include"../headers/elGamalEllipticCurve.hpp"

class CryptoLibrary{
	private:
	public:
		ElGamal elgamal;
		EllipticCurve ellipticcurve;
		ElGamalEC elgamalec;
		DiffieHelman diffiehelman;
		
		PersonEG personeg;
		PersonDH persondh;

		NTL::ZZ_p g;
	public:
		NTL::ZZ p;
		CryptoLibrary();
		
		c1c2 encrypt(NTL::ZZ_p m);
		NTL::ZZ_p decrypt(c1c2 encoded);
		
		c1c2ecComp encryptEC(NTL::ZZ_p m);
		NTL::ZZ_p decryptEC(c1c2ecComp encoded);
		
		signatureEC signEC(NTL::ZZ_p m);
		bool verifyEC(NTL::ZZ_p m,signatureEC signA);
	private:
	
	public:
	
};
