#include<iostream>
#include<NTL/ZZ.h>
#include<NTL/ZZ_p.h>
#include<time.h>
#include"gmp.h"

#include"../headers/person.hpp"
#include"../headers/diffieHelman.hpp"

DiffieHelman::DiffieHelman(NTL::ZZ p,NTL::ZZ_p g){
	this->p = p;
	this->g = g;
}

NTL::ZZ_p DiffieHelman::generateGSecret(PersonDH& A){
	return A.generateA(this->g);
}

void DiffieHelman::generateSharedKey(PersonDH& A,NTL::ZZ_p B1){
	A.generateSharedKey(B1);
}

bool DiffieHelman::verifySharedKey(PersonDH& A,PersonDH& B){
	return A.sharedKey == B.sharedKey;
}
