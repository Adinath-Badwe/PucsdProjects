
#include"../headers/ellipticCurve.hpp"

typedef struct c1c2ec {
	point c1;
	point c2;
} c1c2ec ;

typedef struct c1c2ecComp {
	NTL::ZZ_p x1;
	bool y1;
	NTL::ZZ_p c2;
} c1c2ecComp ;

typedef struct signatureEC {
	NTL::ZZ_p r;
	NTL::ZZ_p s;
} signatureEC;

class ElGamalEC;

class ElGamalEC{
	private:
		NTL::ZZ p;
		NTL::ZZ_p x; // secret key
		EllipticCurve ellipticCurve;
		point P; // the generator
		point Q; // x*P
		
	public:
	
	private:
	
	public:
		ElGamalEC() = default;
		ElGamalEC(NTL::ZZ p,EllipticCurve ellipticCurve);
		
		c1c2ec encrypt(point m);
		c1c2ecComp encrypt(NTL::ZZ_p m);
		point decrypt(c1c2ec encoded);
		NTL::ZZ_p decrypt(c1c2ecComp encoded);
		signatureEC sign(NTL::ZZ_p m);
		bool verify(NTL::ZZ_p m,signatureEC signA);
};
