
char *mystrcpy(char *dest, const char *src) {
    char *save = dest;
    while ((*dest++ = *src++));
    return save;
}

int main() {
    return 0;
}
