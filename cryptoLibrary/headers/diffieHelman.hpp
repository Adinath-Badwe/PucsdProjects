class PersonDH;
class DiffieHelman;

class DiffieHelman{
	private:
	NTL::ZZ_p g;
	NTL::ZZ p;

	public:
		DiffieHelman(NTL::ZZ p,NTL::ZZ_p g);
		DiffieHelman() = default;
		
		NTL::ZZ_p generateGSecret(PersonDH& A);
		void generateSharedKey(PersonDH& A,NTL::ZZ_p B1);
		bool verifySharedKey(PersonDH& A,PersonDH& B);
};
