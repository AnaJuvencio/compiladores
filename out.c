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
    char* _t8;
    double pi;
    double tau;
    double _t9;
    double r;
    double a;
    double _t10;
    double _t11;
    int c;
    int _t12;
    int d;
    int _t13;
    int _t14;
    int _t15;
    int _t16;
    double _t17;
    int n;
    int _t18;
    int _t19;
    int _t20;
    int _t21;
    int _t22;
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
    _t8 = strdup("\n");
    printf("%s\n", _t8);
    pi = 3.14159;
    _t9 = 2.0 * pi;
    tau = _t9;
    r = 2.0;
    _t10 = pi * r;
    _t11 = _t10 * r;
    a = _t11;
    c = 1;
    _t12 = a < 100.0;
    c = _t12;
    _t13 = a > 0.0;
    _t14 = a < 10.0;
    _t15 = _t13 && _t14;
    d = _t15;
    printf("%d\n", d);
    _t16 = a > 0.0;
    if (!_t16) goto L1;
    printf("%f\n", a);
    goto L2;
    L1: ;
    _t17 = -a;
    printf("%f\n", _t17);
    L2: ;
    n = 0;
    L3:
    _t18 = n < 10;
    if (!_t18) goto L4;
    printf("%d\n", n);
    _t19 = n + 1;
    n = _t19;
    goto L3;
    L4:
    n = 0;
    L5:
    if (!1) goto L6;
    _t20 = n + 1;
    n = _t20;
    _t21 = n > 10;
    if (!_t21) goto L7;
    goto L6;
    goto L8;
    L7: ;
    L8: ;
    _t22 = n == 5;
    if (!_t22) goto L9;
    goto L5;
    goto L10;
    L9: ;
    L10: ;
    printf("%d\n", n);
    goto L5;
    L6:
    return 0;
}
