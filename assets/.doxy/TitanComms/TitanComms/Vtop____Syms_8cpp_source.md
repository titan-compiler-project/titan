

# File Vtop\_\_Syms.cpp

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop\_\_Syms.cpp**](Vtop____Syms_8cpp.md)

[Go to the documentation of this file](Vtop____Syms_8cpp.md)

```C++

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtop__Syms.h"
#include "Vtop.h"
#include "Vtop___024root.h"
#include "Vtop___024unit.h"

// FUNCTIONS
Vtop__Syms::~Vtop__Syms()
{

    // Tear down scope hierarchy
    __Vhier.remove(0, &__Vscope_dut_param_mux);
    __Vhier.remove(&__Vscope_dut_param_mux, &__Vscope_dut_param_mux__uut_pmux);

#ifdef VM_TRACE
    if (__Vm_dumping) _traceDumpClose();
#endif  // VM_TRACE
}

void Vtop__Syms::_traceDump() {
    const VerilatedLockGuard lock(__Vm_dumperMutex);
    __Vm_dumperp->dump(VL_TIME_Q());
}

void Vtop__Syms::_traceDumpOpen() {
    const VerilatedLockGuard lock(__Vm_dumperMutex);
    if (VL_UNLIKELY(!__Vm_dumperp)) {
        __Vm_dumperp = new VerilatedVcdC();
        __Vm_modelp->trace(__Vm_dumperp, 0, 0);
        std::string dumpfile = _vm_contextp__->dumpfileCheck();
        __Vm_dumperp->open(dumpfile.c_str());
        __Vm_dumping = true;
    }
}

void Vtop__Syms::_traceDumpClose() {
    const VerilatedLockGuard lock(__Vm_dumperMutex);
    __Vm_dumping = false;
    VL_DO_CLEAR(delete __Vm_dumperp, __Vm_dumperp = nullptr);
}

Vtop__Syms::Vtop__Syms(VerilatedContext* contextp, const char* namep, Vtop* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
{
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    // Setup scopes
    __Vscope_TOP.configure(this, name(), "TOP", "TOP", 0, VerilatedScope::SCOPE_OTHER);
    __Vscope_dut_param_mux.configure(this, name(), "dut_param_mux", "dut_param_mux", -9, VerilatedScope::SCOPE_MODULE);
    __Vscope_dut_param_mux__uut_pmux.configure(this, name(), "dut_param_mux.uut_pmux", "uut_pmux", -9, VerilatedScope::SCOPE_MODULE);

    // Set up scope hierarchy
    __Vhier.add(0, &__Vscope_dut_param_mux);
    __Vhier.add(&__Vscope_dut_param_mux, &__Vscope_dut_param_mux__uut_pmux);

    // Setup export functions
    for (int __Vfinal = 0; __Vfinal < 2; ++__Vfinal) {
        __Vscope_TOP.varInsert(__Vfinal,"in1", &(TOP.in1), false, VLVT_UINT32,VLVD_IN|VLVF_PUB_RW,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"in2", &(TOP.in2), false, VLVT_UINT32,VLVD_IN|VLVF_PUB_RW,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"in3", &(TOP.in3), false, VLVT_UINT32,VLVD_IN|VLVF_PUB_RW,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"in4", &(TOP.in4), false, VLVT_UINT32,VLVD_IN|VLVF_PUB_RW,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"mux_o", &(TOP.mux_o), false, VLVT_UINT32,VLVD_OUT|VLVF_PUB_RW,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"sel_i", &(TOP.sel_i), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,1 ,1,0);
        __Vscope_dut_param_mux.varInsert(__Vfinal,"in1", &(TOP.dut_param_mux__DOT__in1), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux.varInsert(__Vfinal,"in2", &(TOP.dut_param_mux__DOT__in2), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux.varInsert(__Vfinal,"in3", &(TOP.dut_param_mux__DOT__in3), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux.varInsert(__Vfinal,"in4", &(TOP.dut_param_mux__DOT__in4), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux.varInsert(__Vfinal,"mux_o", &(TOP.dut_param_mux__DOT__mux_o), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux.varInsert(__Vfinal,"sel_i", &(TOP.dut_param_mux__DOT__sel_i), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,1 ,1,0);
        __Vscope_dut_param_mux__uut_pmux.varInsert(__Vfinal,"INPUT_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.dut_param_mux__DOT__uut_pmux__DOT__INPUT_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux__uut_pmux.varInsert(__Vfinal,"SELECTOR_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.dut_param_mux__DOT__uut_pmux__DOT__SELECTOR_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux__uut_pmux.varInsert(__Vfinal,"SIGNAL_COUNT", const_cast<void*>(static_cast<const void*>(&(TOP.dut_param_mux__DOT__uut_pmux__DOT__SIGNAL_COUNT))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux__uut_pmux.varInsert(__Vfinal,"inputs", &(TOP.dut_param_mux__DOT__uut_pmux__DOT__inputs), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,2 ,31,0 ,0,3);
        __Vscope_dut_param_mux__uut_pmux.varInsert(__Vfinal,"out", &(TOP.dut_param_mux__DOT__uut_pmux__DOT__out), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,1 ,31,0);
        __Vscope_dut_param_mux__uut_pmux.varInsert(__Vfinal,"selector", &(TOP.dut_param_mux__DOT__uut_pmux__DOT__selector), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,1 ,1,0);
    }
}

```

