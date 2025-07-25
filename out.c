#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    int _t1;
    int _t2;
    int _t3;
    double _t4;
    double _t5;
    double _t6;
    char* _t7;
    double pi;
    double tau;
    double _t8;
    double r;
    double a;
    double _t9;
    double _t10;
    int c;
    int _t11;
    int d;
    int _t12;
    int _t13;
    int _t14;
    int _t15;
    double _t16;
    int n;
    int _t17;
    int _t18;
    int _t19;
    int _t20;
    int _t21;
    _t1 = -5;
    _t2 = 4 * _t1;
    _t3 = 3 + _t2;
    printf("%d\n", _t3);
    _t4 = -7.8;
    _t5 = 5.6 / _t4;
    _t6 = 3.4 - _t5;
    printf("%f\n", _t6);
    _t7 = strdup("x");
    printf("%s\n", _t7);
    printf("\n");
    pi = 3.14159;
    _t8 = 2.0 * pi;
    tau = _t8;
    r = 2.0;
    _t9 = pi * r;
    _t10 = _t9 * r;
    a = _t10;
    c = 1;
    _t11 = a < 100.0;
    c = _t11;
    _t12 = a > 0.0;
    _t13 = a < 10.0;
    _t14 = _t12 && _t13;
    d = _t14;
    printf("%d\n", d);
    _t15 = a > 0.0;
    if (!_t15) goto L1;
    printf("%f\n", a);
    goto L2;
    L1: ;
    _t16 = -a;
    printf("%f\n", _t16);
    L2: ;
    n = 0;
    L3:
    _t17 = n < 10;
    if (!_t17) goto L4;
    printf("%d\n", n);
    _t18 = n + 1;
    n = _t18;
    goto L3;
    L4:
    n = 0;
    L5:
    if (!1) goto L6;
    _t19 = n + 1;
    n = _t19;
    _t20 = n > 10;
    if (!_t20) goto L7;
    goto L6;
    goto L8;
    L7: ;
    L8: ;
    _t21 = n == 5;
    if (!_t21) goto L9;
    goto L5;
    goto L10;
    L9: ;
    L10: ;
    printf("%d\n", n);
    goto L5;
    L6:
    return 0;
}
