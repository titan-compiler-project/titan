#version 450
layout (location = 0) in flat int a;
layout (location = 1) in flat int b;
layout (location = 2) out int c;
void main() {
    c = a + b;
}