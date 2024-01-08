

# Class Vtop\_\_\_024root



[**ClassList**](annotated.md) **>** [**Vtop\_\_\_024root**](classVtop______024root.md)








Inherits the following classes: VerilatedModule


















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
|   | [**VL\_IN**](#function-vl_in-14) (in1, 31, 0) <br> |
|   | [**VL\_IN**](#function-vl_in-24) (in2, 31, 0) <br> |
|   | [**VL\_IN**](#function-vl_in-34) (in3, 31, 0) <br> |
|   | [**VL\_IN**](#function-vl_in-44) (in4, 31, 0) <br> |
|   | [**VL\_IN8**](#function-vl_in8) (sel\_i, 1, 0) <br> |
|   | [**VL\_OUT**](#function-vl_out) (mux\_o, 31, 0) <br> |
|   | [**VL\_UNCOPYABLE**](#function-vl_uncopyable) ([**Vtop\_\_\_024root**](classVtop______024root.md)) <br> |
|   | [**Vtop\_\_\_024root**](#function-vtop___024root) ([**Vtop\_\_Syms**](classVtop____Syms.md) \* symsp, const char \* v\_\_name) <br> |
|  void | [**\_\_Vconfigure**](#function-__vconfigure) (bool first) <br> |
|   | [**~Vtop\_\_\_024root**](#function-vtop___024root) () <br> |




























## Public Attributes Documentation




### variable \_\_VactContinue 

```C++
CData Vtop___024root::__VactContinue;
```






### variable \_\_VactIterCount 

```C++
IData Vtop___024root::__VactIterCount;
```






### variable \_\_VactTriggered 

```C++
VlTriggerVec<1> Vtop___024root::__VactTriggered;
```






### variable \_\_VdlySched 

```C++
VlDelayScheduler Vtop___024root::__VdlySched;
```






### variable \_\_VicoIterCount 

```C++
IData Vtop___024root::__VicoIterCount;
```






### variable \_\_VicoTriggered 

```C++
VlTriggerVec<1> Vtop___024root::__VicoTriggered;
```






### variable \_\_VnbaTriggered 

```C++
VlTriggerVec<1> Vtop___024root::__VnbaTriggered;
```






### variable \_\_VstlIterCount 

```C++
IData Vtop___024root::__VstlIterCount;
```






### variable \_\_VstlTriggered 

```C++
VlTriggerVec<1> Vtop___024root::__VstlTriggered;
```






### variable dut\_param\_mux\_\_DOT\_\_\_\_Vcellinp\_\_uut\_pmux\_\_inputs 

```C++
VlUnpacked<IData, 4> Vtop___024root::dut_param_mux__DOT____Vcellinp__uut_pmux__inputs;
```






### variable dut\_param\_mux\_\_DOT\_\_in1 

```C++
IData Vtop___024root::dut_param_mux__DOT__in1;
```






### variable dut\_param\_mux\_\_DOT\_\_in2 

```C++
IData Vtop___024root::dut_param_mux__DOT__in2;
```






### variable dut\_param\_mux\_\_DOT\_\_in3 

```C++
IData Vtop___024root::dut_param_mux__DOT__in3;
```






### variable dut\_param\_mux\_\_DOT\_\_in4 

```C++
IData Vtop___024root::dut_param_mux__DOT__in4;
```






### variable dut\_param\_mux\_\_DOT\_\_mux\_o 

```C++
IData Vtop___024root::dut_param_mux__DOT__mux_o;
```






### variable dut\_param\_mux\_\_DOT\_\_sel\_i 

```C++
CData Vtop___024root::dut_param_mux__DOT__sel_i;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_inputs 

```C++
VlUnpacked<IData, 4> Vtop___024root::dut_param_mux__DOT__uut_pmux__DOT__inputs;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_out 

```C++
IData Vtop___024root::dut_param_mux__DOT__uut_pmux__DOT__out;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_selector 

```C++
CData Vtop___024root::dut_param_mux__DOT__uut_pmux__DOT__selector;
```






### variable vlSymsp 

```C++
Vtop__Syms* const Vtop___024root::vlSymsp;
```



## Public Static Attributes Documentation




### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_INPUT\_WIDTH 

```C++
constexpr IData Vtop___024root::dut_param_mux__DOT__uut_pmux__DOT__INPUT_WIDTH;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_SELECTOR\_WIDTH 

```C++
constexpr IData Vtop___024root::dut_param_mux__DOT__uut_pmux__DOT__SELECTOR_WIDTH;
```






### variable dut\_param\_mux\_\_DOT\_\_uut\_pmux\_\_DOT\_\_SIGNAL\_COUNT 

```C++
constexpr IData Vtop___024root::dut_param_mux__DOT__uut_pmux__DOT__SIGNAL_COUNT;
```



## Public Functions Documentation




### function VL\_IN [1/4]

```C++
Vtop___024root::VL_IN (
    in1,
    31,
    0
) 
```






### function VL\_IN [2/4]

```C++
Vtop___024root::VL_IN (
    in2,
    31,
    0
) 
```






### function VL\_IN [3/4]

```C++
Vtop___024root::VL_IN (
    in3,
    31,
    0
) 
```






### function VL\_IN [4/4]

```C++
Vtop___024root::VL_IN (
    in4,
    31,
    0
) 
```






### function VL\_IN8 

```C++
Vtop___024root::VL_IN8 (
    sel_i,
    1,
    0
) 
```






### function VL\_OUT 

```C++
Vtop___024root::VL_OUT (
    mux_o,
    31,
    0
) 
```






### function VL\_UNCOPYABLE 

```C++
Vtop___024root::VL_UNCOPYABLE (
    Vtop___024root
) 
```






### function Vtop\_\_\_024root 

```C++
Vtop___024root::Vtop___024root (
    Vtop__Syms * symsp,
    const char * v__name
) 
```






### function \_\_Vconfigure 

```C++
void Vtop___024root::__Vconfigure (
    bool first
) 
```






### function ~Vtop\_\_\_024root 

```C++
Vtop___024root::~Vtop___024root () 
```




------------------------------
The documentation for this class was generated from the following file `titan/comms/verilog/tests/sim_build/Vtop___024root.h`

