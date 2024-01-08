

# File Vtop.h



[**FileList**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop.h**](Vtop_8h.md)

[Go to the source code of this file](Vtop_8h_source.md)



* `#include "verilated.h"`
* `#include "svdpi.h"`















## Classes

| Type | Name |
| ---: | :--- |
| class | [**VL\_NOT\_FINAL**](classVL__NOT__FINAL.md) <br> |






## Public Attributes

| Type | Name |
| ---: | :--- |
|  VL\_IN & | [**in1**](#variable-in1)  <br> |
|  VL\_IN & | [**in2**](#variable-in2)  <br> |
|  VL\_IN & | [**in3**](#variable-in3)  <br> |
|  VL\_IN & | [**in4**](#variable-in4)  <br> |
|  VL\_OUT & | [**mux\_o**](#variable-mux_o)  <br> |
|  [**Vtop\_\_\_024root**](classVtop______024root.md) \*const | [**rootp**](#variable-rootp)  <br> |
|  VL\_IN8 & | [**sel\_i**](#variable-sel_i)  <br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  [**VL\_NOT\_FINAL**](classVL__NOT__FINAL.md) VerilatedModel | [**VL\_ATTR\_ALIGNED**](#function-vl_attr_aligned) (VL\_CACHE\_LINE\_BYTES) <br> |
|   | [**Vtop**](#function-vtop) (VerilatedContext \* contextp, const char \* name="TOP") <br> |
|   | [**Vtop**](#function-vtop) (const char \* name="TOP") <br> |
|  void | [**eval**](#function-eval) () <br>_Evaluate the model. Application must call when inputs change._  |
|  void | [**eval\_end\_step**](#function-eval_end_step) () <br> |
|  void | [**eval\_step**](#function-eval_step) () <br>_Evaluate when calling multiple units/models per time step._  |
|  bool | [**eventsPending**](#function-eventspending) () <br>_Are there scheduled events to handle?_  |
|  void | [**final**](#function-final) () <br>_Simulation complete, run final blocks. Application must call on completion._  |
|  const char \* | [**hierName**](#function-hiername) () override const<br> |
|  const char \* | [**modelName**](#function-modelname) () override const<br> |
|  const char \* | [**name**](#function-name) () const<br>_Retrieve name of this model instance (as passed to constructor)._  |
|  uint64\_t | [**nextTimeSlot**](#function-nexttimeslot) () <br>_Returns time at next time slot. Aborts if !eventsPending()_  |
|  unsigned | [**threads**](#function-threads) () override const<br> |
|  void | [**trace**](#function-trace) (VerilatedVcdC \* tfp, int levels, int options=0) <br>_Trace signals in the model; called by application code._  |
|  std::unique\_ptr&lt; VerilatedTraceConfig &gt; | [**traceConfig**](#function-traceconfig) () override const<br> |
| virtual  | [**~Vtop**](#function-vtop) () <br>_Destroy the model; called (often implicitly) by application code._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**VERILATED\_VTOP\_H\_**](Vtop_8h.md#define-verilated_vtop_h_)  <br> |

## Public Attributes Documentation




### variable in1 

```C++
VL_IN& in1;
```






### variable in2 

```C++
VL_IN& in2;
```






### variable in3 

```C++
VL_IN& in3;
```






### variable in4 

```C++
VL_IN& in4;
```






### variable mux\_o 

```C++
VL_OUT& mux_o;
```






### variable rootp 

```C++
Vtop___024root* const rootp;
```






### variable sel\_i 

```C++
VL_IN8& sel_i;
```



## Public Functions Documentation




### function VL\_ATTR\_ALIGNED 

```C++
VL_NOT_FINAL VerilatedModel VL_ATTR_ALIGNED (
    VL_CACHE_LINE_BYTES
) 
```






### function Vtop 


```C++
explicit Vtop (
    VerilatedContext * contextp,
    const char * name="TOP"
) 
```



Construct the model; called by application code If contextp is null, then the model will use the default global context If name is "", then makes a wrapper with a single model invisible with respect to DPI scope names. 


        



### function Vtop 

```C++
explicit Vtop (
    const char * name="TOP"
) 
```






### function eval 

```C++
void eval () 
```






### function eval\_end\_step 


```C++
void eval_end_step () 
```



Evaluate at end of a timestep for tracing, when using eval\_step(). Application must call after all eval() and before time changes. 


        



### function eval\_step 

```C++
void eval_step () 
```






### function eventsPending 

```C++
bool eventsPending () 
```






### function final 

```C++
void final () 
```






### function hierName 

```C++
const char * hierName () override const
```






### function modelName 

```C++
const char * modelName () override const
```






### function name 

```C++
const char * name () const
```






### function nextTimeSlot 

```C++
uint64_t nextTimeSlot () 
```






### function threads 

```C++
unsigned threads () override const
```






### function trace 

```C++
void trace (
    VerilatedVcdC * tfp,
    int levels,
    int options=0
) 
```






### function traceConfig 

```C++
std::unique_ptr< VerilatedTraceConfig > traceConfig () override const
```






### function ~Vtop 

```C++
virtual ~Vtop () 
```



## Macro Definition Documentation





### define VERILATED\_VTOP\_H\_ 

```C++
#define VERILATED_VTOP_H_ 
```




------------------------------
The documentation for this class was generated from the following file `titan/comms/verilog/tests/sim_build/Vtop.h`

