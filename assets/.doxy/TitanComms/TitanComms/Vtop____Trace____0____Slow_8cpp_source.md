

# File Vtop\_\_Trace\_\_0\_\_Slow.cpp

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_Trace\_\_0\_\_Slow.cpp**](Vtop____Trace____0____Slow_8cpp.md)

[Go to the documentation of this file](Vtop____Trace____0____Slow_8cpp.md)

```C++

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vtop__Syms.h"


VL_ATTR_COLD void Vtop___024root__trace_init_sub__TOP__0(Vtop___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_init_sub__TOP__0\n"); );
    // Init
    const int c = vlSymsp->__Vm_baseCode;
    // Body
    tracep->declBus(c+1,"in1", false,-1, 31,0);
    tracep->declBus(c+2,"in2", false,-1, 31,0);
    tracep->declBus(c+3,"in3", false,-1, 31,0);
    tracep->declBus(c+4,"in4", false,-1, 31,0);
    tracep->declBus(c+5,"sel_i", false,-1, 1,0);
    tracep->declBus(c+6,"mux_o", false,-1, 31,0);
    tracep->pushNamePrefix("dut_param_mux ");
    tracep->declBus(c+7,"in1", false,-1, 31,0);
    tracep->declBus(c+8,"in2", false,-1, 31,0);
    tracep->declBus(c+9,"in3", false,-1, 31,0);
    tracep->declBus(c+10,"in4", false,-1, 31,0);
    tracep->declBus(c+11,"sel_i", false,-1, 1,0);
    tracep->declBus(c+12,"mux_o", false,-1, 31,0);
    tracep->pushNamePrefix("uut_pmux ");
    tracep->declBus(c+19,"INPUT_WIDTH", false,-1, 31,0);
    tracep->declBus(c+20,"SELECTOR_WIDTH", false,-1, 31,0);
    tracep->declBus(c+21,"SIGNAL_COUNT", false,-1, 31,0);
    tracep->declBus(c+13,"selector", false,-1, 1,0);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+14+i*1,"inputs", true,(i+0), 31,0);
    }
    tracep->declBus(c+18,"out", false,-1, 31,0);
    tracep->popNamePrefix(2);
}

VL_ATTR_COLD void Vtop___024root__trace_init_top(Vtop___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_init_top\n"); );
    // Body
    Vtop___024root__trace_init_sub__TOP__0(vlSelf, tracep);
}

VL_ATTR_COLD void Vtop___024root__trace_full_top_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vtop___024root__trace_chg_top_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vtop___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/);

VL_ATTR_COLD void Vtop___024root__trace_register(Vtop___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_register\n"); );
    // Body
    tracep->addFullCb(&Vtop___024root__trace_full_top_0, vlSelf);
    tracep->addChgCb(&Vtop___024root__trace_chg_top_0, vlSelf);
    tracep->addCleanupCb(&Vtop___024root__trace_cleanup, vlSelf);
}

VL_ATTR_COLD void Vtop___024root__trace_full_sub_0(Vtop___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vtop___024root__trace_full_top_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_full_top_0\n"); );
    // Init
    Vtop___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtop___024root*>(voidSelf);
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    Vtop___024root__trace_full_sub_0((&vlSymsp->TOP), bufp);
}

VL_ATTR_COLD void Vtop___024root__trace_full_sub_0(Vtop___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_full_sub_0\n"); );
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    // Body
    bufp->fullIData(oldp+1,(vlSelf->in1),32);
    bufp->fullIData(oldp+2,(vlSelf->in2),32);
    bufp->fullIData(oldp+3,(vlSelf->in3),32);
    bufp->fullIData(oldp+4,(vlSelf->in4),32);
    bufp->fullCData(oldp+5,(vlSelf->sel_i),2);
    bufp->fullIData(oldp+6,(vlSelf->mux_o),32);
    bufp->fullIData(oldp+7,(vlSelf->dut_param_mux__DOT__in1),32);
    bufp->fullIData(oldp+8,(vlSelf->dut_param_mux__DOT__in2),32);
    bufp->fullIData(oldp+9,(vlSelf->dut_param_mux__DOT__in3),32);
    bufp->fullIData(oldp+10,(vlSelf->dut_param_mux__DOT__in4),32);
    bufp->fullCData(oldp+11,(vlSelf->dut_param_mux__DOT__sel_i),2);
    bufp->fullIData(oldp+12,(vlSelf->dut_param_mux__DOT__mux_o),32);
    bufp->fullCData(oldp+13,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__selector),2);
    bufp->fullIData(oldp+14,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[0]),32);
    bufp->fullIData(oldp+15,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[1]),32);
    bufp->fullIData(oldp+16,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[2]),32);
    bufp->fullIData(oldp+17,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__inputs[3]),32);
    bufp->fullIData(oldp+18,(vlSelf->dut_param_mux__DOT__uut_pmux__DOT__out),32);
    bufp->fullIData(oldp+19,(0x20U),32);
    bufp->fullIData(oldp+20,(2U),32);
    bufp->fullIData(oldp+21,(4U),32);
}

```

