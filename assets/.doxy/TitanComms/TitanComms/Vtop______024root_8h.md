

# File Vtop\_\_\_024root.h



[**FileList**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_\_024root.h**](Vtop______024root_8h.md)

[Go to the source code of this file](Vtop______024root_8h_source.md)



* `#include "verilated.h"`
* `#include "verilated_timing.h"`















## Classes

| Type | Name |
| ---: | :--- |
| class | [**Vtop\_\_\_024root**](classVtop______024root.md) <br> |






## Public Attributes

| Type | Name |
| ---: | :--- |
|  CData | [**\_\_VactContinue**](#variable-__vactcontinue)  <br> |
|  IData | [**\_\_VactIterCount**](#variable-__vactitercount)  <br> |
|  VlTriggerVec&lt; 1 &gt; | [**\_\_VactTriggered**](#variable-__vacttriggered)  <br> |
|  VlDelayScheduler | [**\_\_VdlySched**](#variable-__vdlysched)  <br> |
|  IData | [**\_\_VicoIterCount**](#variable-__vicoitercount)  <br> |
|  VlTriggerVec&lt; 1 &gt; | [**\_\_VicoTriggered**](#variable-__vicotriggered)  <br> |
|  VlTriggerVec&lt; 1 &gt; | [**\_\_VnbaTriggered**](#variable-__vnbatriggered)  <br> |
|  IData | [**\_\_VstlIterCount**](#variable-__vstlitercount)  <br> |
|  VlTriggerVec&lt; 1 &gt; | [**\_\_VstlTriggered**](#variable-__vstltriggered)  <br> |
|  VlUnpacked&lt; IData, 4 &gt; | [**dut\_param\_mux\_\_DOT\_\_\_\_Vcellinp\_\_uut\_pmux\_\_inputs**](#variable-dut_param_mux__dot____vcellinp__uut_pmux__inputs)  <br> |
|  IData | [**dut\_param\_mux\_\_DOT\_\_in1**](#variable-dut_param_mux__dot__in1)  <br> |
|  IData | [**dut\_param\_mux\_\_DOT\_\_in2**](#variable-dut_param_mux__dot__in2)  <br> |
|  IData | [**dut\_param\_mux\_\_DOT\_\_in3**](#variable-dut_param_mux__dot__in3)  <br> |
|  IData | [**dut\_param\_mux\_\_DOT\_\_in4**](#variable-dut_param_mux__dot__in4)  <br> |
|  IData | [**dut\_param\_mux\_\_DOT\_\_mux\_o**](#variable-dut_param_mux__dot__mux_o)  <br> |
|  CData | [**dut\_param\_mux\_\_DOT\_\_sel\_i**](#variable-dut_param_mux__dot__sel_i)  <br> |
|  VlUnpacked&lt; IData, 4 &gt; | [**dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_inputs**](#variable-dut_param_mux__dot__uut_pmux__dot__inputs)  <br> |
|  IData | [**dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_out**](#variable-dut_param_mux__dot__uut_pmux__dot__out)  <br> |
|  CData | [**dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_selector**](#variable-dut_param_mux__dot__uut_pmux__dot__selector)  <br> |
|  [**Vtop\_\_Syms**](classVtop____Syms.md) \*const | [**vlSymsp**](#variable-vlsymsp)  <br> |


## Public Static Attributes

| Type | Name |
| ---: | :--- |
|  constexpr IData | [**dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_INPUT\_WIDTH**](#variable-dut_param_mux__dot__uut_pmux__dot__input_width)   = = 0x00000020U<br> |
|  constexpr IData | [**dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_SELECTOR\_WIDTH**](#variable-dut_param_mux__dot__uut_pmux__dot__selector_width)   = = 2U<br> |
|  constexpr IData | [**dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_SIGNAL\_COUNT**](#variable-dut_param_mux__dot__uut_pmux__dot__signal_count)   = = 4U<br> |














## Public Functions

| Type | Name |
| ---: | :--- |
|  [**Vtop\_\_\_024root**](classVtop______024root.md) VerilatedModule | [**VL\_ATTR\_ALIGNED**](#function-vl_attr_aligned) (VL\_CACHE\_LINE\_BYTES) <br> |
|   | [**VL\_IN**](#function-vl_in) (in1, 31, 0) <br> |
|   | [**VL\_IN**](#function-vl_in) (in2, 31, 0) <br> |
|   | [**VL\_IN**](#function-vl_in) (in3, 31, 0) <br> |
|   | [**VL\_IN**](#function-vl_in) (in4, 31, 0) <br> |
|   | [**VL\_IN8**](#function-vl_in8) (sel\_i, 1, 0) <br> |
|   | [**VL\_OUT**](#function-vl_out) (mux\_o, 31, 0) <br> |
|   | [**VL\_UNCOPYABLE**](#function-vl_uncopyable) ([**Vtop\_\_\_024root**](classVtop______024root.md)) <br> |
|   | [**Vtop\_\_\_024root**](#function-vtop___024root) ([**Vtop\_\_Syms**](classVtop____Syms.md) \* symsp, const char \* v\_\_name) <br> |
|  void | [**\_\_Vconfigure**](#function-__vconfigure) (bool first) <br> |
|   | [**~Vtop\_\_\_024root**](#function-vtop___024root) () <br> |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**VERILATED\_VTOP\_\_\_024ROOT\_H\_**](Vtop______024root_8h.md#define-verilated_vtop___024root_h_)  <br> |

## Public Attributes Documentation




### variable \_\_VactContinue 

```C++
CData __VactContinue;
```






### variable \_\_VactIterCount 

```C++
IData __VactIterCount;
```






### variable \_\_VactTriggered 

```C++
VlTriggerVec<1> __VactTriggered;
```






### variable \_\_VdlySched 

```C++
VlDelayScheduler __VdlySched;
```






### variable \_\_VicoIterCount 

```C++
IData __VicoIterCount;
```






### variable \_\_VicoTriggered 

```C++
VlTriggerVec<1> __VicoTriggered;
```






### variable \_\_VnbaTriggered 

```C++
VlTriggerVec<1> __VnbaTriggered;
```






### variable \_\_VstlIterCount 

```C++
IData __VstlIterCount;
```






### variable \_\_VstlTriggered 

```C++
VlTriggerVec<1> __VstlTriggered;
```






### variable dut\_param\_mux\_\_DOT\_\_\_\_Vcellinp\_\_uut\_pmux\_\_inputs 

```C++
VlUnpacked<IData, 4> dut_param_mux__DOT____Vcellinp__uut_pmux__inputs;
```






### variable dut\_param\_mux\_\_DOT\_\_in1 

```C++
IData dut_param_mux__DOT__in1;
```






### variable dut\_param\_mux\_\_DOT\_\_in2 

```C++
IData dut_param_mux__DOT__in2;
```






### variable dut\_param\_mux\_\_DOT\_\_in3 

```C++
IData dut_param_mux__DOT__in3;
```






### variable dut\_param\_mux\_\_DOT\_\_in4 

```C++
IData dut_param_mux__DOT__in4;
```






### variable dut\_param\_mux\_\_DOT\_\_mux\_o 

```C++
IData dut_param_mux__DOT__mux_o;
```






### variable dut\_param\_mux\_\_DOT\_\_sel\_i 

```C++
CData dut_param_mux__DOT__sel_i;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_inputs 

```C++
VlUnpacked<IData, 4> dut_param_mux__DOT__uut_pmux__DOT__inputs;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_out 

```C++
IData dut_param_mux__DOT__uut_pmux__DOT__out;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_selector 

```C++
CData dut_param_mux__DOT__uut_pmux__DOT__selector;
```






### variable vlSymsp 

```C++
Vtop__Syms* const vlSymsp;
```



## Public Static Attributes Documentation




### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_INPUT\_WIDTH 

```C++
constexpr IData dut_param_mux__DOT__uut_pmux__DOT__INPUT_WIDTH;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_SELECTOR\_WIDTH 

```C++
constexpr IData dut_param_mux__DOT__uut_pmux__DOT__SELECTOR_WIDTH;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_SIGNAL\_COUNT 

```C++
constexpr IData dut_param_mux__DOT__uut_pmux__DOT__SIGNAL_COUNT;
```



## Public Functions Documentation




### function VL\_ATTR\_ALIGNED 

```C++
Vtop___024root VerilatedModule VL_ATTR_ALIGNED (
    VL_CACHE_LINE_BYTES
) 
```






### function VL\_IN 

```C++
VL_IN (
    in1,
    31,
    0
) 
```






### function VL\_IN 

```C++
VL_IN (
    in2,
    31,
    0
) 
```






### function VL\_IN 

```C++
VL_IN (
    in3,
    31,
    0
) 
```






### function VL\_IN 

```C++
VL_IN (
    in4,
    31,
    0
) 
```






### function VL\_IN8 

```C++
VL_IN8 (
    sel_i,
    1,
    0
) 
```






### function VL\_OUT 

```C++
VL_OUT (
    mux_o,
    31,
    0
) 
```






### function VL\_UNCOPYABLE 

```C++
VL_UNCOPYABLE (
    Vtop___024root
) 
```






### function Vtop\_\_\_024root 

```C++
Vtop___024root (
    Vtop__Syms * symsp,
    const char * v__name
) 
```






### function \_\_Vconfigure 

```C++
void __Vconfigure (
    bool first
) 
```






### function ~Vtop\_\_\_024root 

```C++
~Vtop___024root () 
```



## Macro Definition Documentation





### define VERILATED\_VTOP\_\_\_024ROOT\_H\_ 

```C++
#define VERILATED_VTOP___024ROOT_H_ 
```




------------------------------
The documentation for this class was generated from the following file `titan/comms/verilog/tests/sim_build/Vtop___024root.h`

