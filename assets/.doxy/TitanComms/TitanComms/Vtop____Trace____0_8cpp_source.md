

# File Vtop\_\_Trace\_\_0.cpp

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_Trace\_\_0.cpp**](Vtop____Trace____0_8cpp.md)

[Go to the documentation of this file](Vtop____Trace____0_8cpp.md)

```C++

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vtop__Syms.h"


void Vtop___024root__trace_chg_sub_0(Vtop___024root* vlSelf, VerilatedVcd::Buffer* bufp);

void Vtop___024root__trace_chg_top_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_chg_top_0\n"); );
    // Init
    Vtop___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtop___024root*>(voidSelf);
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (VL_UNLIKELY(!vlSymsp->__Vm_activity)) return;
    // Body
    Vtop___024root__trace_chg_sub_0((&vlSymsp->TOP), bufp);
}

void Vtop___024root__trace_chg_sub_0(Vtop___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_chg_sub_0\n"); );
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + 1);
    // Body
    bufp->chgIData(oldp+0,(vlSelf->in1),32);
    bufp->chgIData(oldp+1,(vlSelf->in2),32);
    bufp->chgIData(oldp+2,(vlSelf->in3),32);
    bufp->chgIData(oldp+3,(vlSelf->in4),32);
    bufp->chgCData(oldp+4,(vlSelf->sel_i),2);
    bufp->chgIData(oldp+5,(vlSelf->mux_o),32);
    bufp->chgIData(oldp+6,(vlSelf->dut_param_mux__DOT__in1),32);
    bufp->chgIData(oldp+7,(vlSelf->dut_param_mux__DOT__in2),32);
    bufp->chgIData(oldp+8,(vlSelf->dut_param_mux__DOT__in3),32);
    bufp->chgIData(oldp+9,(vlSelf->dut_param_mux__DOT__in4),32);
    bufp->chgCData(oldp+10,(vlSelf->dut_param_mux__DOT__sel_i),2);
    bufp->chgIData(oldp+11,(vlSelf->dut_param_mux__DOT__mux_o),32);
    bufp->chgCData(oldp+12,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__selector),2);
    bufp->chgIData(oldp+13,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[0]),32);
    bufp->chgIData(oldp+14,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[1]),32);
    bufp->chgIData(oldp+15,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[2]),32);
    bufp->chgIData(oldp+16,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[3]),32);
    bufp->chgIData(oldp+17,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__out),32);
}

void Vtop___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_cleanup\n"); );
    // Init
    Vtop___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtop___024root*>(voidSelf);
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VlUnpacked<CData/*0:0*/, 1> __Vm_traceActivity;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        __Vm_traceActivity[__Vi0] = 0;
    }
    // Body
    vlSymsp->__Vm_activity = false;
    __Vm_traceActivity[0U] = 0U;
}

```

