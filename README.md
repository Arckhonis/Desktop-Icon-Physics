# Warning
Please, do not store anything important on your Desktop while running this program. And even better, try to run it in a virtual machine.
I am not responsible for the consequences of unstable operation of this program.

# Info
This repository contains source code that gives physics for the Desktop File.

It supports two modes that can be swithced by pressing Virtual Key 1 or 2:

1) Classic Physics: File speed is constant.

2) Mouse interaction: Speed decays but you can push file with mouse!

# Compilation Quircks

To compile C DLL I used MinGW compiler with this command:

`gcc -shared -o "Movement API.dll" "Movement API.c" -lole32 -loleaut32 -luuid -mwindows -m32 -std=c90`
(Note C90 stuff :\)

[![Showcase Video](https://img.youtube.com/vi/Un_MgcClTrc/0.jpg)](https://youtu.be/Un_MgcClTrc)
