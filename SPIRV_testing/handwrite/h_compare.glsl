#version 450
layout (location = 0) in flat int a;
layout (location = 1) in flat int b;
layout (location = 2) out int c;
layout (location = 3) out int d;
void main() {
    c = a > b ? 7 : 0;
    d = a > 5 ? 1 : 2;
}