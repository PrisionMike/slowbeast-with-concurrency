void* alok(int* a) {
    *a = 8;
}

int main() {
    int b;
    alok(&b);
    return 0;
}