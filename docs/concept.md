# The Concept

This compiler is based in the idea of DSAs, as talked about in Hennessy & Pattersons Turing Award lecture. In essence, these devices have a highly specialised architecture, that targets one particular domain (think AI, ML, IoT) and provides a device which can perform tasks in that domain with better performance and efficiency.
*[DSAs]: Domain Specific Architectures
*[AI]: Artificial Intelligence
*[ML]: Machine Learning
*[IoT]: Internet of Things

These architectures have to be custom built, and in order to achieve that we have to build some custom hardware. Instead of placing individual transistors down, we can program an FPGA using a HDL like SystemVerilog. Unfortunately, FPGAs do come with a steep learning curve, possibly dissuading people from using it. So why not attempt to make it easier to access, whilst also providing some DSA functionality?
*[FPGA]: Field Programmable Gate Array
*[FPGAs]: Field Programmable Gate Arrays
*[HDL]: Hardware Description Language

Python (and its variants like MicroPython) are growing in popularity, so much so that a recent StackOverflow survey had shown Python as being the 3rd most popular language. It seems like a good language to target due to that, but unfortunately it'll have to be a subset of the language so that it can map onto hardware and to also limit the scope of the compiler.

Using SPIR-V as the intermediate language means that the front-end and back-end of the compiler can be swapped out, and the SPIR-V assembly can be compiled into something that can run on existing GPUs via OpenGL/OpenCL/Vulkan. Furthemore, SPIR-V's assembly structure mimics a dataflow graph, so we can use that to our advantage.
*[SPIR-V]: Standard Portable Intermediate Representation - Vulkan

With this SPIR-V assembly, we can then attempt to assemble some SystemVerilog and output this file to the user. With any luck, this SystemVerilog can be used to program the FPGA and provide the user with some custom hardware.