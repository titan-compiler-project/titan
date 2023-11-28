#version 450
layout (location = 0) in flat int a;
layout (location = 1) out int c;

void main() { 

    c = a >= 10 ? 5 : 0;

}