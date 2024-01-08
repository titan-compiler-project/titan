

# Class Vtop\_\_Syms



[**ClassList**](annotated.md) **>** [**Vtop\_\_Syms**](classVtop____Syms.md)








Inherits the following classes: VerilatedSyms


















## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**Vtop\_\_\_024root**](classVtop______024root.md) | [**TOP**](#variable-top)  <br> |
|  VerilatedHierarchy | [**\_\_Vhier**](#variable-__vhier)  <br> |
|  bool | [**\_\_Vm\_activity**](#variable-__vm_activity)   = = false<br>_Trace class for $dump\*._  |
|  uint32\_t | [**\_\_Vm\_baseCode**](#variable-__vm_basecode)   = = 0<br>_Used by trace routines when tracing multiple models._  |
|  bool | [**\_\_Vm\_didInit**](#variable-__vm_didinit)   = = false<br> |
|  VerilatedMutex | [**\_\_Vm\_dumperMutex**](#variable-__vm_dumpermutex)  <br> |
|  bool | [**\_\_Vm\_dumping**](#variable-__vm_dumping)   = = false<br> |
|  Vtop \*const | [**\_\_Vm\_modelp**](#variable-__vm_modelp)  <br> |
|  VerilatedScope | [**\_\_Vscope\_TOP**](#variable-__vscope_top)  <br> |
|  VerilatedScope | [**\_\_Vscope\_dut\_param\_mux**](#variable-__vscope_dut_param_mux)  <br> |
|  VerilatedScope | [**\_\_Vscope\_dut\_param\_mux\_\_uut\_pmux**](#variable-__vscope_dut_param_mux__uut_pmux)  <br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  VerilatedVcdC \*\_\_Vm\_dumperp | [**VL\_GUARDED\_BY**](#function-vl_guarded_by) (\_\_Vm\_dumperMutex) <br> |
|   | [**Vtop\_\_Syms**](#function-vtop__syms) (VerilatedContext \* contextp, const char \* namep, Vtop \* modelp) <br> |
|  void | [**\_traceDump**](#function-_tracedump) () <br> |
|  void | [**\_traceDumpClose**](#function-_tracedumpclose) () <br> |
|  void | [**\_traceDumpOpen**](#function-_tracedumpopen) () <br> |
|  const char \* | [**name**](#function-name) () <br> |
|   | [**~Vtop\_\_Syms**](#function-vtop__syms) () <br> |




























## Public Attributes Documentation




### variable TOP 

```C++
Vtop___024root Vtop__Syms::TOP;
```






### variable \_\_Vhier 

```C++
VerilatedHierarchy Vtop__Syms::__Vhier;
```






### variable \_\_Vm\_activity 

_Trace class for $dump\*._ 
```C++
bool Vtop__Syms::__Vm_activity;
```



Used by trace routines to determine change occurred 


        



### variable \_\_Vm\_baseCode 

```C++
uint32_t Vtop__Syms::__Vm_baseCode;
```






### variable \_\_Vm\_didInit 

```C++
bool Vtop__Syms::__Vm_didInit;
```






### variable \_\_Vm\_dumperMutex 

```C++
VerilatedMutex Vtop__Syms::__Vm_dumperMutex;
```






### variable \_\_Vm\_dumping 

```C++
bool Vtop__Syms::__Vm_dumping;
```






### variable \_\_Vm\_modelp 

```C++
Vtop* const Vtop__Syms::__Vm_modelp;
```






### variable \_\_Vscope\_TOP 

```C++
VerilatedScope Vtop__Syms::__Vscope_TOP;
```






### variable \_\_Vscope\_dut\_param\_mux 

```C++
VerilatedScope Vtop__Syms::__Vscope_dut_param_mux;
```






### variable \_\_Vscope\_dut\_param\_mux\_\_uut\_pmux 

```C++
VerilatedScope Vtop__Syms::__Vscope_dut_param_mux__uut_pmux;
```



## Public Functions Documentation




### function VL\_GUARDED\_BY 

```C++
VerilatedVcdC *__Vm_dumperp Vtop__Syms::VL_GUARDED_BY (
    __Vm_dumperMutex
) 
```






### function Vtop\_\_Syms 

```C++
Vtop__Syms::Vtop__Syms (
    VerilatedContext * contextp,
    const char * namep,
    Vtop * modelp
) 
```






### function \_traceDump 

```C++
void Vtop__Syms::_traceDump () 
```






### function \_traceDumpClose 

```C++
void Vtop__Syms::_traceDumpClose () 
```






### function \_traceDumpOpen 

```C++
void Vtop__Syms::_traceDumpOpen () 
```






### function name 

```C++
inline const char * Vtop__Syms::name () 
```






### function ~Vtop\_\_Syms 

```C++
Vtop__Syms::~Vtop__Syms () 
```




------------------------------
The documentation for this class was generated from the following file `titan/comms/verilog/tests/sim_build/Vtop__Syms.h`

