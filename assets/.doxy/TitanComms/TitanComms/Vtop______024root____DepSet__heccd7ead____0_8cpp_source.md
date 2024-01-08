

# File Vtop\_\_\_024root\_\_DepSet\_heccd7ead\_\_0.cpp

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_\_024root\_\_DepSet\_heccd7ead\_\_0.cpp**](Vtop______024root____DepSet__heccd7ead____0_8cpp.md)

[Go to the documentation of this file](Vtop______024root____DepSet__heccd7ead____0_8cpp.md)

```C++

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "verilated.h"
#include "verilated_dpi.h"

#include "Vtop___024root.h"

VlCoroutine Vtop___024root___eval_initial__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_initial(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_initial\n"); );
    // Body
    Vtop___024root___eval_initial__TOP__0(vlSelf);
}

VL_INLINE_OPT void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ico_sequent__TOP__0\n"); );
    // Body
    vlSelf->dut_param_mux__DOT__in1 = vlSelf->in1;
    vlSelf->dut_param_mux__DOT__in2 = vlSelf->in2;
    vlSelf->dut_param_mux__DOT__in3 = vlSelf->in3;
    vlSelf->dut_param_mux__DOT__in4 = vlSelf->in4;
    vlSelf->dut_param_mux__DOT__sel_i = vlSelf->sel_i;
    vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs[0U] 
        = vlSelf->in1;
    vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs[1U] 
        = vlSelf->in2;
    vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs[2U] 
        = vlSelf->in3;
    vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs[3U] 
        = vlSelf->in4;
    vlSelf->dut_param_mux__DOT__uut_pmux__DOT__selector 
        = vlSelf->dut_param_mux__DOT__sel_i;
    vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[0U] 
        = vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs
        [0U];
    vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[1U] 
        = vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs
        [1U];
    vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[2U] 
        = vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs
        [2U];
    vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[3U] 
        = vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs
        [3U];
    vlSelf->mux_o = vlSelf->dut_param_mux__DOT____Vcellinp__uut_pmux__inputs
        [vlSelf->sel_i];
    vlSelf->dut_param_mux__DOT__mux_o = vlSelf->mux_o;
    vlSelf->dut_param_mux__DOT__uut_pmux__DOT__out 
        = vlSelf->mux_o;
}

void Vtop___024root___eval_ico(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_ico\n"); );
    // Body
    if (vlSelf->__VicoTriggered.at(0U)) {
        Vtop___024root___ico_sequent__TOP__0(vlSelf);
    }
}

void Vtop___024root___eval_act(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_act\n"); );
}

void Vtop___024root___eval_nba(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_nba\n"); );
}

void Vtop___024root___eval_triggers__ico(Vtop___024root* vlSelf);
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
void Vtop___024root___eval_triggers__act(Vtop___024root* vlSelf);
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
void Vtop___024root___timing_resume(Vtop___024root* vlSelf);
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__nba(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval\n"); );
    // Init
    CData/*0:0*/ __VicoContinue;
    VlTriggerVec<1> __VpreTriggered;
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    vlSelf->__VicoIterCount = 0U;
    __VicoContinue = 1U;
    while (__VicoContinue) {
        __VicoContinue = 0U;
        Vtop___024root___eval_triggers__ico(vlSelf);
        if (vlSelf->__VicoTriggered.any()) {
            __VicoContinue = 1U;
            if (VL_UNLIKELY((0x64U < vlSelf->__VicoIterCount))) {
#ifdef VL_DEBUG
                Vtop___024root___dump_triggers__ico(vlSelf);
#endif
                VL_FATAL_MT("/home/kris/repos/titan/titan/comms/verilog/tests/dut_param_mux.sv", 1, "", "Input combinational region did not converge.");
            }
            vlSelf->__VicoIterCount = ((IData)(1U) 
                                       + vlSelf->__VicoIterCount);
            Vtop___024root___eval_ico(vlSelf);
        }
    }
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        __VnbaContinue = 0U;
        vlSelf->__VnbaTriggered.clear();
        vlSelf->__VactIterCount = 0U;
        vlSelf->__VactContinue = 1U;
        while (vlSelf->__VactContinue) {
            vlSelf->__VactContinue = 0U;
            Vtop___024root___eval_triggers__act(vlSelf);
            if (vlSelf->__VactTriggered.any()) {
                vlSelf->__VactContinue = 1U;
                if (VL_UNLIKELY((0x64U < vlSelf->__VactIterCount))) {
#ifdef VL_DEBUG
                    Vtop___024root___dump_triggers__act(vlSelf);
#endif
                    VL_FATAL_MT("/home/kris/repos/titan/titan/comms/verilog/tests/dut_param_mux.sv", 1, "", "Active region did not converge.");
                }
                vlSelf->__VactIterCount = ((IData)(1U) 
                                           + vlSelf->__VactIterCount);
                __VpreTriggered.andNot(vlSelf->__VactTriggered, vlSelf->__VnbaTriggered);
                vlSelf->__VnbaTriggered.set(vlSelf->__VactTriggered);
                Vtop___024root___timing_resume(vlSelf);
                Vtop___024root___eval_act(vlSelf);
            }
        }
        if (vlSelf->__VnbaTriggered.any()) {
            __VnbaContinue = 1U;
            if (VL_UNLIKELY((0x64U < __VnbaIterCount))) {
#ifdef VL_DEBUG
                Vtop___024root___dump_triggers__nba(vlSelf);
#endif
                VL_FATAL_MT("/home/kris/repos/titan/titan/comms/verilog/tests/dut_param_mux.sv", 1, "", "NBA region did not converge.");
            }
            __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
            Vtop___024root___eval_nba(vlSelf);
        }
    }
}

void Vtop___024root___timing_resume(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___timing_resume\n"); );
    // Body
    if (vlSelf->__VactTriggered.at(0U)) {
        vlSelf->__VdlySched.resume();
    }
}

#ifdef VL_DEBUG
void Vtop___024root___eval_debug_assertions(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_debug_assertions\n"); );
    // Body
    if (VL_UNLIKELY((vlSelf->sel_i & 0xfcU))) {
        Verilated::overWidthError("sel_i");}
}
#endif  // VL_DEBUG

```

