

# File Vtop\_\_\_024root\_\_DepSet\_h84412442\_\_0.cpp

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_\_024root\_\_DepSet\_h84412442\_\_0.cpp**](Vtop______024root____DepSet__h84412442____0_8cpp.md)

[Go to the documentation of this file](Vtop______024root____DepSet__h84412442____0_8cpp.md)

```C++

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "verilated.h"
#include "verilated_dpi.h"

#include "Vtop__Syms.h"
#include "Vtop___024root.h"

VL_INLINE_OPT VlCoroutine Vtop___024root___eval_initial__TOP__0(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_initial__TOP__0\n"); );
    // Init
    VlWide<6>/*191:0*/ __Vtemp_h513746c2__0;
    // Body
    __Vtemp_h513746c2__0[0U] = 0x2e766364U;
    __Vtemp_h513746c2__0[1U] = 0x5f6d7578U;
    __Vtemp_h513746c2__0[2U] = 0x6172616dU;
    __Vtemp_h513746c2__0[3U] = 0x75745f70U;
    __Vtemp_h513746c2__0[4U] = 0x65735f64U;
    __Vtemp_h513746c2__0[5U] = 0x776176U;
    vlSymsp->_vm_contextp__->dumpfile(VL_CVT_PACK_STR_NW(6, __Vtemp_h513746c2__0));
    vlSymsp->_traceDumpOpen();
    co_await vlSelf->__VdlySched.delay(0x3e8U, "/home/kris/repos/titan/titan/comms/verilog/tests/dut_param_mux.sv", 
                                       12);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval_triggers__ico(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_triggers__ico\n"); );
    // Body
    vlSelf->__VicoTriggered.at(0U) = (0U == vlSelf->__VicoIterCount);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtop___024root___dump_triggers__ico(vlSelf);
    }
#endif
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval_triggers__act(Vtop___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_triggers__act\n"); );
    // Body
    vlSelf->__VactTriggered.at(0U) = vlSelf->__VdlySched.awaitingCurrentTime();
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtop___024root___dump_triggers__act(vlSelf);
    }
#endif
}

```

