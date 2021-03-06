#include <stdio.h>

#ifdef _MSC_VER
#  define DLLIMPORT  __declspec(dllimport)
#else
#  define DLLIMPORT  extern
#endif

DLLIMPORT int add_rec(int, int);
DLLIMPORT int (*my_callback)(int);

static int some_callback(int x)
{
    printf("some_callback(%d)\n", x);
    fflush(stdout);
    return add_rec(x, 9);
}

int main(void)
{
    int x, y;
    my_callback = some_callback;
    x = add_rec(40, 2);
    y = add_rec(100, -5);
    printf("got: %d %d\n", x, y);
    return 0;
}
