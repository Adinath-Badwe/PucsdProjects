#include<iostream>
#include<NTL/ZZ.h>
#include<stdlib.h>
// solve the discrete log problem using brute force approach

using namespace std;
using namespace NTL;

ZZ discreteLog(ZZ g,ZZ h,ZZ p);

int main(){
	// h = g^x
	// given g and h find x
	ZZ g,h,p;
	g = 3; // generator
	h = 21; //
	p = 101; //
	std::cout << discreteLog(g,h,p) << std::endl;
	return 0;
}

ZZ discreteLog(ZZ g,ZZ h,ZZ p){
	ZZ x,i;
	i = 0;
	for(;i<p;i++){
		if(h == PowerMod(g,i,p)){
			x = i;
		}
	}
	return x;
}
