#include<stdio.h>
#include<stdlib.h>

    // struct abcd {
    //     int a;
    //     int b;
    // };

    // struct abcd a;
    
    // *((int*)&a) = 10;
    // *((int*)&a+1) = 20;

    // int a = 10;
    // int b = 20;
    // {
    //     int a = 30;
    //     int b = 40;
    // }
    // float h = 20;
    // while(a > 10){
    //     int e = 20;
    //     while(a > 5){
    //         a = 20;
    //         while(a>0){
    //             a = 10;
    //         }
    //     }
    //     e = a + b;
    // }
    // int c = 20;

    // int a;
    // a = 30;
    // while(a > 10 && a < 20 || a == 45){
    //     a = 40;
    //     while(a > 10 && a < 20 || a == 45){
    //         a = 40;
    //         while(a > 10 && a < 20 || a == 45){
    //             a = 40; 
    //     }   
    //     }
    // }
    // a = 50;


    // i = 50;
    // int k,m;
    // k = 0;

    // while(i < 100){
    //     a = 100 * b * c;
    //     b = c * b;
    //     c = a + b;
    //     e = c * b * a;
    //     j = 0;
    //     while(j*j < e){
    //         d = c * c;
    //         b = c + d;
    //         a = a + b;
    //         if(j < e){
    //             j = j + a;
    //         }
    //         k = 0;
    //         while(k < j*j){
    //             m = a + b;
    //             k = k + m;
    //         }

    //         j = j + b;
    //     }
    //     i = i + 1;
    // }



    // while(i < 10000){
    //     a = a + 20;
    //     b = b + a;
    //     i = i + b;
    // }


int main(){
    int i,a;
    i = 0;
    a = 0;
    while(i < 100){
        while(i < 50){
            while(i < 20){
                i = i + 1;
            }
            i = i + 1;
        }
        i = i + 1;
    }
    a = i;
    printf("%d",a);
}

// int something(int a,int b,int c,int d,int e,int f,int g,int h,int i,int j,int k,int l){
//     a = a + b;
//     b = b * c;
//     c = c + d;
//     d = d + d * e;
//     f = f * f + g;
    
//     if (h > 0){
//     return h;
//     }else{
//         return something(10,20,30,40,50,60,70,80,90,100,110,120);
//     }
// }

// i = something(i*i, 2*i, 3*i, i+4, 5+5, 6*i, 7+i, 8+7, i+a*i, a, 20, 30);


// int something1(int a,int b,int c,int d,int e,int f,int g,int h,int i,int j,int k,int l){
//     a = a + b;
//     b = b * c;
//     c = c + d;
//     d = d + d * e;
//     f = f * f + g;
    
//     if (h > 0){
//     return h;
//     }else{
//         return something1(10,20,30,40,50,60,70,80,90,100,110,120);
//     }
// }


// int something(int a,int b,int c,int d,int e,int f,int g,int h,int i,int j,int k,int l){
//     a = a + b;
//     b = b * c;
//     c = c + d;
//     d = d + d * e;
//     f = f * f + g;
    
//     if (h > 0){
//     return h;
//     }else{
//         return something(10,20,30,40,50,60,70,80,90,100,110,120);
//     }
// }

//                 i = something(i*i, 2*i, 3*i, i+4, 5+5, 6*i, 7+i, 8+7, i+a*i, a, 20, 30);
//                 i = something1(i*i, 2*i, 3*i, i+4, 5+5, 6*i, 7+i, 8+7, i+a*i, a, 20, 30);

// int something3(){
//     int a,b,c;
//     a = 10;
//     b = 30;
//     c = 40;
//     return a+b*c;
// }

// int something(int a,int b,int c,int d,int e,int f,int g,int h,int i,int j,int k,int l){
//     a = a + b;
//     b = b * c;
//     c = c + d;
//     d = d + d * e;
//     f = f * f + g;
    
//     if (h > 0){
//     return h;
//     }else{
//         return something(a*2,b*20,30*c,40*d,50*e,60*f,70*g,80*h,90*i,100*j,110*k,120*l);
//     }
// }

// int something1(int a,int b,int c,int d,int e,int f,int g,int h,int i,int j,int k,int l){
//     a = a + b;
//     b = b * c;
//     c = c + d;
//     d = d + d * e;
//     f = f * f + g;
    
//     if (h > 0){
//     return h;
//     }else{
//         return something1(a*2,b*20,30*c,40*d,50*e,60*f,70*g,80*h,90*i,100*j,110*k,120*l);
//     }
// }

// int main(){
//     int i,a;
//     i = 110;
//     a = 20;
    
//     while(i < 100){
//         a = a + 10;
//         i = i + i;
//         while(i < 50){
//             a = a + 10;        
//             while(i < 20){
//                 i = i * a;
//                 i = something(i*i, 2*i, 3*i, i+4, 5+5, 6*i, 7+i, 8+7, i+a*i, a, 20, 30);
//                 i = something1(i*i, 2*i, 3*i, i+4, 5+5, 6*i, 7+i, 8+7, i+a*i, a, 20, 30);
//                 i = i * something3();
//                 something(i*i, 2*i, 3*i, i+4, 5+5, 6*i, 7+i, 8+7, i+a*i, a, 20, 30);
//                 something1(i*i, 2*i, 3*i, i+4, 5+5, 6*i, 7+i, 8+7, i+a*i, a, 20, 30);
//                 i * something3();
//             }
//             i = i + 1;
//         }
//         i = i + 1;
//     }
//     a = i;

//     if (i < 100){
//         i = 200;
//     }else{
//         i = 300;
//     }
//     a = i * i * i;
//     if (a > 0){
//         return a;
//     }
// }


// int something1(){
//     int a,b,f;
//     a = 20;
//     b = 30;
//     f = 20;
//     return a+b+f;
// }


// int something2(int c, int d,int e){
//     int a,b,f;
//     a = c;
//     b = d;
//     f = e;
//     return a+b+c+d+f+e;
// }

// int main(){
//     int i,a;
//     a = 20;
//     i = 10;
    
//     while(i < 20){
//         i = i +1;
//     }

//     a = something1();
//     a = something2(a,55,i+a*i);
//     return a;
// }
