

# Class VL\_NOT\_FINAL



[**ClassList**](annotated.md) **>** [**VL\_NOT\_FINAL**](classVL__NOT__FINAL.md)








Inherits the following classes: VerilatedModel


















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
|   | [**Vtop**](#function-vtop-12) (VerilatedContext \* contextp, const char \* name="TOP") <br> |
|   | [**Vtop**](#function-vtop-22) (const char \* name="TOP") <br> |
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




























## Public Attributes Documentation




### variable in1 

```C++
VL_IN& VL_NOT_FINAL::in1;
```






### variable in2 

```C++
VL_IN& VL_NOT_FINAL::in2;
```






### variable in3 

```C++
VL_IN& VL_NOT_FINAL::in3;
```






### variable in4 

```C++
VL_IN& VL_NOT_FINAL::in4;
```






### variable mux\_o 

```C++
VL_OUT& VL_NOT_FINAL::mux_o;
```






### variable rootp 

```C++
Vtop___024root* const VL_NOT_FINAL::rootp;
```






### variable sel\_i 

```C++
VL_IN8& VL_NOT_FINAL::sel_i;
```



## Public Functions Documentation




### function Vtop [1/2]


```C++
explicit VL_NOT_FINAL::Vtop (
    VerilatedContext * contextp,
    const char * name="TOP"
) 
```



Construct the model; called by application code If contextp is null, then the model will use the default global context If name is "", then makes a wrapper with a single model invisible with respect to DPI scope names. 


        



### function Vtop [2/2]

```C++
explicit VL_NOT_FINAL::Vtop (
    const char * name="TOP"
) 
```






### function eval 

```C++
inline void VL_NOT_FINAL::eval () 
```






### function eval\_end\_step 


```C++
void VL_NOT_FINAL::eval_end_step () 
```



Evaluate at end of a timestep for tracing, when using [**eval\_step()**](classVL__NOT__FINAL.md#function-eval_step). Application must call after all [**eval()**](classVL__NOT__FINAL.md#function-eval) and before time changes. 


        



### function eval\_step 

```C++
void VL_NOT_FINAL::eval_step () 
```






### function eventsPending 

```C++
bool VL_NOT_FINAL::eventsPending () 
```






### function final 

```C++
void VL_NOT_FINAL::final () 
```






### function hierName 

```C++
const char * VL_NOT_FINAL::hierName () override const
```






### function modelName 

```C++
const char * VL_NOT_FINAL::modelName () override const
```






### function name 

```C++
const char * VL_NOT_FINAL::name () const
```






### function nextTimeSlot 

```C++
uint64_t VL_NOT_FINAL::nextTimeSlot () 
```






### function threads 

```C++
unsigned VL_NOT_FINAL::threads () override const
```






### function trace 

```C++
void VL_NOT_FINAL::trace (
    VerilatedVcdC * tfp,
    int levels,
    int options=0
) 
```






### function traceConfig 

```C++
std::unique_ptr< VerilatedTraceConfig > VL_NOT_FINAL::traceConfig () override const
```






### function ~Vtop 

```C++
virtual VL_NOT_FINAL::~Vtop () 
```




------------------------------
The documentation for this class was generated from the following file `titan/comms/verilog/tests/sim_build/Vtop.h`

