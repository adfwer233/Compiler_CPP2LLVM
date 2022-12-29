int printf(char* a, ...);
int scanf(char* a, ...);

int test(int a, int b) {
    int x = 1;
    int y = 2;
    bool d = true;
    x = 2;
    a = 3;
    b = 3 * 4;
    scanf("%d", &y);
    printf("%d\n", x);
    printf("%d\n", a);
    printf("%d\n", y);
    return x;
}

int main() {
    test(1, 2)
    return 0;
}
