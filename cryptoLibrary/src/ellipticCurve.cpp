#include<iostream>
#include<NTL/ZZ.h>
#include<NTL/ZZ_p.h>

#include"../headers/ellipticCurve.hpp"

EllipticCurve::EllipticCurve(NTL::ZZ p){
	this->p = p;
	NTL::ZZ_p D;
	D = 0;
	
	while(D == 0){
		this->a = NTL::random_ZZ_p();
		this->b = NTL::random_ZZ_p();
		this->a = 1;
		this->b = 6;
		D = 4 * NTL::power(this->a,3) + 27 * NTL::power(this->b,2);
	}
}

point EllipticCurve::addPoint(point p1, point p2){
	point output;
	NTL::ZZ_p lambda;
	
	if(p1.x == p2.x and p1.y == -1*p2.y){
		output.x = 0;
		output.y = 1;
	}
	
	if(p1.x == p2.x){
		return this->doublePoint(p1);
	}
	
	if(p1.x == 0 and p1.y == 1){
		output = p2;
		return output;
	}
	
	if(p2.x == 0 and p2.y == 1){
		output = p1;
		return output;
	}
	
	lambda = (p2.y - p1.y)*inv(p2.x-p1.x);
	output.x = lambda*lambda - (p1.x + p2.x);
	output.y = lambda*(p1.x - output.x) - p1.y;
	
	return output;
}

point EllipticCurve::doublePoint(point p1){
	if(p1.x == 0 and p1.y == 1){
		return p1;
	}
	
	point output;
	NTL::ZZ_p lambda;
	
	lambda = (3*p1.x*p1.x+this->a) * inv(2*p1.y);
	output.x = lambda*lambda - (p1.x + p1.x);
	output.y = lambda*(p1.x - output.x) - p1.y;
	
	return output;
}

bool EllipticCurve::isQuadraticResidue(NTL::ZZ_p a){
	return NTL::power(a,(this->p - 1)/2) == 1;
}

NTL::ZZ_p EllipticCurve::computey(NTL::ZZ_p a){
	// a1 = x^3 + ax + b
	// y = a1^((p+1)/4)
	NTL::ZZ_p output;
	
	output = NTL::power(a,(this->p+1)/4);
	
	return output;
}

point EllipticCurve::generatePoint(){
	NTL::ZZ_p x,a1; 
	point P;

	x = NTL::random_ZZ_p();
	a1 = NTL::power(x,3) + this->a*x + this->b;
	
	while(this->isQuadraticResidue(a1) != 1){
		x = NTL::random_ZZ_p();
		a1 = NTL::power(x,3) + this->a*x + this->b;
	}
	P.x = x;
	P.y = this->computey(a1);
	
	return P;
}

point EllipticCurve::scalarMultiplyPoint(point p1, NTL::ZZ_p m){
	long bits = NTL::NumBits(NTL::rep(m));
	NTL::ZZ tempM = NTL::rep(m);
	point output = p1;
	long bitVal;
	
	for(long i = bits-2; i >= 0; i--){
		output = this->doublePoint(output);
		bitVal = NTL::SetBit(tempM,i);
		if(bitVal == 1){
			output = this->addPoint(output,p1);
		}
	}
	return output;
}

