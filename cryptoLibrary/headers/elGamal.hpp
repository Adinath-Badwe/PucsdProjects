# pragma once
//#include<NTL/ZZ.h>
//#include<NTL/ZZ_p.h>
//#include"person.hpp"

class ElGamal;

//typedef struct pkey{
//	NTL::ZZ p;
//	NTL::ZZ_p g;
//	NTL::ZZ_p h;
//} pkey;

typedef struct c1c2 {
	NTL::ZZ_p c1;
	NTL::ZZ_p c2;
} c1c2;

typedef struct signature{
	NTL::ZZ_p gamma;
	NTL::ZZ_p delta;
}signature ;

class ElGamal{
	private:
		NTL::ZZ p;
		NTL::ZZ_p g;

		void setGenerator(NTL::ZZ_p g1);
		void setp(NTL::ZZ p1);

	public:
		ElGamal(NTL::ZZ p1,NTL::ZZ_p g1);
		ElGamal() = default;
		
		//void generateKeys(PersonEG& A);
		c1c2 encrypt(NTL::ZZ_p m,PersonEG& A);
		NTL::ZZ_p decrypt(c1c2 encoded,PersonEG& A);
		signature sign(NTL::ZZ_p m,PersonEG& A);
		bool verify(PersonEG& A,NTL::ZZ_p m,signature signA);
};
