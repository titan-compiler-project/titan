

# File Vtop\_\_Syms.h



[**FileList**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_Syms.h**](Vtop____Syms_8h.md)

[Go to the source code of this file](Vtop____Syms_8h_source.md)



* `#include "verilated.h"`
* `#include "verilated_vcd_c.h"`
* `#include "Vtop.h"`
* `#include "Vtop___024root.h"`
* `#include "Vtop___024unit.h"`















## Classes

| Type | Name |
| ---: | :--- |
| class | [**Vtop\_\_Syms**](classVtop____Syms.md) <br> |






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
|  [**Vtop\_\_Syms**](classVtop____Syms.md) VerilatedSyms | [**VL\_ATTR\_ALIGNED**](#function-vl_attr_aligned) (VL\_CACHE\_LINE\_BYTES) <br> |
|  VerilatedVcdC \*\_\_Vm\_dumperp | [**VL\_GUARDED\_BY**](#function-vl_guarded_by) (\_\_Vm\_dumperMutex) <br> |
|   | [**Vtop\_\_Syms**](#function-vtop__syms) (VerilatedContext \* contextp, const char \* namep, Vtop \* modelp) <br> |
|  void | [**\_traceDump**](#function-_tracedump) () <br> |
|  void | [**\_traceDumpClose**](#function-_tracedumpclose) () <br> |
|  void | [**\_traceDumpOpen**](#function-_tracedumpopen) () <br> |
|  const char \* | [**name**](#function-name) () <br> |
|   | [**~Vtop\_\_Syms**](#function-vtop__syms) () <br> |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**VERILATED\_VTOP\_\_SYMS\_H\_**](Vtop____Syms_8h.md#define-verilated_vtop__syms_h_)  <br> |

## Public Attributes Documentation




### variable TOP 

```C++
Vtop___024root TOP;
```






### variable \_\_Vhier 

```C++
VerilatedHierarchy __Vhier;
```






### variable \_\_Vm\_activity 

_Trace class for $dump\*._ 
```C++
bool __Vm_activity;
```



Used by trace routines to determine change occurred 


        



### variable \_\_Vm\_baseCode 

```C++
uint32_t __Vm_baseCode;
```






### variable \_\_Vm\_didInit 

```C++
bool __Vm_didInit;
```






### variable \_\_Vm\_dumperMutex 

```C++
VerilatedMutex __Vm_dumperMutex;
```






### variable \_\_Vm\_dumping 

```C++
bool __Vm_dumping;
```






### variable \_\_Vm\_modelp 

```C++
Vtop* const __Vm_modelp;
```






### variable \_\_Vscope\_TOP 

```C++
VerilatedScope __Vscope_TOP;
```






### variable \_\_Vscope\_dut\_param\_mux 

```C++
VerilatedScope __Vscope_dut_param_mux;
```






### variable \_\_Vscope\_dut\_param\_mux\_\_uut\_pmux 

```C++
VerilatedScope __Vscope_dut_param_mux__uut_pmux;
```



## Public Functions Documentation




### function VL\_ATTR\_ALIGNED 

```C++
Vtop__Syms VerilatedSyms VL_ATTR_ALIGNED (
    VL_CACHE_LINE_BYTES
) 
```






### function VL\_GUARDED\_BY 

```C++
VerilatedVcdC *__Vm_dumperp VL_GUARDED_BY (
    __Vm_dumperMutex
) 
```






### function Vtop\_\_Syms 

```C++
Vtop__Syms (
    VerilatedContext * contextp,
    const char * namep,
    Vtop * modelp
) 
```






### function \_traceDump 

```C++
void _traceDump () 
```






### function \_traceDumpClose 

```C++
void _traceDumpClose () 
```






### function \_traceDumpOpen 

```C++
void _traceDumpOpen () 
```






### function name 

```C++
const char * name () 
```






### function ~Vtop\_\_Syms 

```C++
~Vtop__Syms () 
```



## Macro Definition Documentation





### define VERILATED\_VTOP\_\_SYMS\_H\_ 

```C++
#define VERILATED_VTOP__SYMS_H_ 
```




------------------------------
The documentation for this class was generated from the following file `titan/comms/verilog/tests/sim_build/Vtop__Syms.h`

