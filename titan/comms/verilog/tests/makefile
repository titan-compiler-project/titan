SIM ?= verilator
# SIM ?= icarus
TOPLEVEL_LANG ?= verilog
# WAVES = 0
# EXTRA_ARGS ?= -v
EXTRA_ARGS += --trace --trace-structs --timing --Wno-width --Wno-unsigned --Wno-pinmissing

RTL_DIR ?= $(shell dirname $(PWD))/rtl
TEST_DIR ?= $(shell dirname $(PWD))/tests


VERILOG_SOURCES += $(RTL_DIR)/titan_comms_package.sv
VERILOG_SOURCES += $(RTL_DIR)/add_2.sv
VERILOG_SOURCES += $(RTL_DIR)/core_interface.sv
VERILOG_SOURCES += $(TEST_DIR)/dut_core_interface.sv

# MODULE refers to python file containing tests
# TOPLEVEL refers to the top level module in the source file

# core interface
test_ci:
	$(MAKE) sim MODULE=test_core_interface TOPLEVEL=dut_test_core_interface


#clean:
#	rm *.vcd
#	rm -r sim_build

cleaner:
	$(MAKE) clean
	rm *.vcd
	rm results.xml

ls_rtl_dir:
	@echo $(RTL_DIR)
	@ls $(RTL_DIR)

ls_test_dir:
	@echo $(TEST_DIR)
	@ls $(TEST_DIR)

say_hello:
	@echo "hello :)"

include $(shell cocotb-config --makefiles)/Makefile.sim
