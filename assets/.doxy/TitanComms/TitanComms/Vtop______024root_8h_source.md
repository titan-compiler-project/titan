

# File Vtop\_\_\_024root.h

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_\_024root.h**](Vtop______024root_8h.md)

[Go to the documentation of this file](Vtop______024root_8h.md)

```C++

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP___024ROOT_H_
#define VERILATED_VTOP___024ROOT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"

class Vtop__Syms;

class Vtop___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    VL_IN8(sel_i,1,0);
    CData/*1:0*/ dut_param_mux__DOT__sel_i;
    CData/*1:0*/ dut_param_mux__DOT__uut_pmux__DOT__selector;
    CData/*0:0*/ __VactContinue;
    VL_IN(in1,31,0);
    VL_IN(in2,31,0);
    VL_IN(in3,31,0);
    VL_IN(in4,31,0);
    VL_OUT(mux_o,31,0);
    IData/*31:0*/ dut_param_mux__DOT__in1;
    IData/*31:0*/ dut_param_mux__DOT__in2;
    IData/*31:0*/ dut_param_mux__DOT__in3;
    IData/*31:0*/ dut_param_mux__DOT__in4;
    IData/*31:0*/ dut_param_mux__DOT__mux_o;
    IData/*31:0*/ dut_param_mux__DOT__uut_pmux__DOT__out;
    IData/*31:0*/ __VstlIterCount;
    IData/*31:0*/ __VicoIterCount;
    IData/*31:0*/ __VactIterCount;
    VlUnpacked<IData/*31:0*/, 4> dut_param_mux__DOT____Vcellinp__uut_pmux__inputs;
    VlUnpacked<IData/*31:0*/, 4> dut_param_mux__DOT__uut_pmux__DOT__inputs;
    VlDelayScheduler __VdlySched;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<1> __VactTriggered;
    VlTriggerVec<1> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr IData/*31:0*/ dut_param_mux__DOT__uut_pmux__DOT__INPUT_WIDTH = 0x00000020U;
    static constexpr IData/*31:0*/ dut_param_mux__DOT__uut_pmux__DOT__SELECTOR_WIDTH = 2U;
    static constexpr IData/*31:0*/ dut_param_mux__DOT__uut_pmux__DOT__SIGNAL_COUNT = 4U;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
} VL_ATTR_ALIGNED(VL_CACHE_LINE_BYTES);


#endif  // guard

```

