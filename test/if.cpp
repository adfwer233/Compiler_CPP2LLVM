int printf(char* a, ...);

int main() {

    int x = 10;
    if (x != 0) {
        x = x + 10;
    }
    printf("%d\n", x);
    return 0;
}