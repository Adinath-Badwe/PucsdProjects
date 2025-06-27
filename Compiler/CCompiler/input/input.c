#include "stdio.h"
#include <stdlib.h>

int something1(){
    int a,b,f;
    a = 20;
    b = 30;
    f = 20;
    return a+b+f;
}

int main(){
    int i,a;
    a = 20;
    i = 10;
    
    while(i < 20){
        i = i +1;
    }

    int k[rand()];
    
    a = something1();
    printf("%d",a*i);
    return a*i;
}
