#include<NTL/ZZ.h>
#include<NTL/ZZ_p.h>

#include"../headers/elGamalEllipticCurve.hpp"
//#include"../headers/ellipticCurve.hpp"

ElGamalEC::ElGamalEC(NTL::ZZ p,EllipticCurve ellipticCurve){
	this->p = p;
	this->x = NTL::random_ZZ_p();
	this->ellipticCurve = ellipticCurve;
	this->P = this->ellipticCurve.generatePoint();
	this->Q = this->ellipticCurve.scalarMultiplyPoint(this->P,this->x);
}

c1c2ec ElGamalEC::encrypt(point m){
	c1c2ec output;
	NTL::ZZ_p y;
	y = NTL::random_ZZ_p();
	
	output.c1 = this->ellipticCurve.scalarMultiplyPoint(this->P,y);
	output.c2 = this->ellipticCurve.scalarMultiplyPoint(this->Q,y);
	output.c2 = this->ellipticCurve.addPoint(output.c2,m);
	
	return output;
}

point ElGamalEC::decrypt(c1c2ec encoded){
	point output;
	
	output = this->ellipticCurve.scalarMultiplyPoint(encoded.c1,this->x);
	output.y = -1 * output.y;
	output = this->ellipticCurve.addPoint(output,encoded.c2);
	
	return output;
}

c1c2ecComp ElGamalEC::encrypt(NTL::ZZ_p m){
	c1c2ecComp output;
	NTL::ZZ_p y;
	y = NTL::random_ZZ_p();
	point yQ = this->ellipticCurve.scalarMultiplyPoint(this->Q,y);
	point yP = this->ellipticCurve.scalarMultiplyPoint(this->P,y);
	
	output.x1 = yP.x;
	output.c2 = yQ.x * m;
	
	output.y1 = NTL::IsOdd(NTL::rep(yP.y));
	
	return output;
}

NTL::ZZ_p ElGamalEC::decrypt(c1c2ecComp encoded){
	NTL::ZZ_p output;
	
	point yP;
	yP.x = encoded.x1;
	yP.y = this->ellipticCurve.computey(encoded.x1*encoded.x1*encoded.x1+encoded.x1*this->ellipticCurve.a+this->ellipticCurve.b);
	if(encoded.y1 == 0 and NTL::IsOdd(NTL::rep(yP.y))){
		yP.y = -1 * yP.y;
	}
	
	point yQ = this->ellipticCurve.scalarMultiplyPoint(yP,x);

	output = encoded.c2*NTL::inv(yQ.x);
	std::cout << NTL::inv(yQ.x)*yQ.x << std::endl;
	return output;
}

signatureEC ElGamalEC::sign(NTL::ZZ_p m){
	signatureEC output;
	NTL::ZZ_p k;
	k = NTL::random_ZZ_p();
	point kP = this->ellipticCurve.scalarMultiplyPoint(this->P,k);
	
	while(kP.x == 0 or NTL::inv(k)*(m + this->x*kP.x) == 0){
		k = NTL::random_ZZ_p();
		kP = this->ellipticCurve.scalarMultiplyPoint(this->P,k);
	}
	
	output.r = kP.x;
	output.s = NTL::inv(k)*(m + this->x*output.r);
	
	return output;
}

bool ElGamalEC::verify(NTL::ZZ_p m,signatureEC signA){
	NTL::ZZ_p w,u1,u2;
	point P;
	
	w = NTL::inv(signA.s);
	u1 = m*w;
	u2 = signA.r*w;
	P = this->ellipticCurve.addPoint(this->ellipticCurve.scalarMultiplyPoint(this->P,u1),this->ellipticCurve.scalarMultiplyPoint(this->Q,u2));
	return signA.r == P.x;
}
