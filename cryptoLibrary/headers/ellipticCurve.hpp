
//class EllipticCurve;
// point at infinity is (0,1);

typedef struct point{
	NTL::ZZ_p x;
	NTL::ZZ_p y;
} point;

class EllipticCurve{
	private:
	public:
		NTL::ZZ p;
		NTL::ZZ_p a;
		NTL::ZZ_p b;
		
	private:
	
	public:
		point generatePoint();
		bool isQuadraticResidue(NTL::ZZ_p a);
		NTL::ZZ_p computey(NTL::ZZ_p a);
		
		EllipticCurve(NTL::ZZ p);
		EllipticCurve() = default;
		point doublePoint(point p1);
		point addPoint(point p1,point p2);
		point scalarMultiplyPoint(point p1,NTL::ZZ_p m);
};
