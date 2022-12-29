int main() {

}

int global = 0;

int test(int a, int b) {
    int x = 1;
    bool d = true;
    x = 2;
    a = 3;
    b = 3 * 4;
    b = 14 % 4;

    x = a + b * global;
    

    return x;
}