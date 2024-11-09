class PersonDH;
class PersonEG;
class ElGamal;
class DiffieHelman;

typedef struct pkey{
	NTL::ZZ p;
	NTL::ZZ_p g;
	NTL::ZZ_p h;
} pkey;

class PersonDH{
	private:
		NTL::ZZ_p secretKey;
		NTL::ZZ_p sharedKey;

		void generateSecretKey();
		void generateSharedKey(NTL::ZZ_p A1);

		friend DiffieHelman;
	public:
		PersonDH() = default;
		PersonDH(NTL::ZZ p);
		NTL::ZZ_p generateA(NTL::ZZ_p g);
};

class PersonEG{
	private:
		NTL::ZZ_p secretKey;
		pkey publicKey;

		NTL::ZZ_p multSecretKey(NTL::ZZ_p y);

		friend ElGamal;
	public:
		PersonEG() = default;
		PersonEG(NTL::ZZ p,NTL::ZZ_p g);
		NTL::ZZ_p generategx(NTL::ZZ_p g);
};
