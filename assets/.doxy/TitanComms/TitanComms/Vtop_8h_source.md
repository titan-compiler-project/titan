

# File Vtop.h

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**verilog**](dir_549b42112f6dc36cf8af5f13bada3f17.md) **>** [**tests**](dir_359bc3875cb3adaee3d3f269dbe0d6e4.md) **>** [**sim\_build**](dir_816ed350c72cf5de8127e0b7e8b74e54.md) **>** [**Vtop.h**](Vtop_8h.md)

[Go to the documentation of this file](Vtop_8h.md)

```C++

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Primary model header
//
// This header should be included by all source files instantiating the design.
// The class here is then constructed to instantiate the design.
// See the Verilator manual for examples.

#ifndef VERILATED_VTOP_H_
#define VERILATED_VTOP_H_  // guard

#include "verilated.h"
#include "svdpi.h"

class Vtop__Syms;
class Vtop___024root;
class VerilatedVcdC;

// This class is the main interface to the Verilated model
class Vtop VL_NOT_FINAL : public VerilatedModel {
  private:
    // Symbol table holding complete model state (owned by this class)
    Vtop__Syms* const vlSymsp;

  public:

    // PORTS
    // The application code writes and reads these signals to
    // propagate new values into/out from the Verilated model.
    VL_IN8(&sel_i,1,0);
    VL_IN(&in1,31,0);
    VL_IN(&in2,31,0);
    VL_IN(&in3,31,0);
    VL_IN(&in4,31,0);
    VL_OUT(&mux_o,31,0);

    // CELLS
    // Public to allow access to /* verilator public */ items.
    // Otherwise the application code can consider these internals.

    // Root instance pointer to allow access to model internals,
    // including inlined /* verilator public_flat_* */ items.
    Vtop___024root* const rootp;

    // CONSTRUCTORS
    explicit Vtop(VerilatedContext* contextp, const char* name = "TOP");
    explicit Vtop(const char* name = "TOP");
    virtual ~Vtop();
  private:
    VL_UNCOPYABLE(Vtop);  

  public:
    // API METHODS
    void eval() { eval_step(); eval_end_step(); }
    void eval_step();
    void eval_end_step();
    void final();
    bool eventsPending();
    uint64_t nextTimeSlot();
    void trace(VerilatedVcdC* tfp, int levels, int options = 0);
    const char* name() const;

    // Abstract methods from VerilatedModel
    const char* hierName() const override final;
    const char* modelName() const override final;
    unsigned threads() const override final;
    std::unique_ptr<VerilatedTraceConfig> traceConfig() const override final;
} VL_ATTR_ALIGNED(VL_CACHE_LINE_BYTES);

#endif  // guard

```

