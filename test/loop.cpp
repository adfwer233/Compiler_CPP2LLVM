int printf(char* a, ...);

int main() {
    int x = 0;
    int i = 0;
    for (i = 1; i < 10; i=i+1) {
        x = x + 1;
    }
    printf("%d\n", x);
    while (i > 0) {
        i = i -1;
    }
    printf("%d\n", i);
    return 0;
}