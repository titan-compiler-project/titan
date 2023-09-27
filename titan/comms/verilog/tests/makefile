SIM ?= verilator
TOPLEVEL_LANG ?= verilog
EXTRA_ARGS += --trace --trace-structs --timing --Wno-width --Wno-unsigned --Wno-pinmissing
# --Wno-multitop

RTL_DIR ?= $(shell dirname $(PWD))/rtl
TEST_DIR ?= $(shell dirname $(PWD))/tests


VERILOG_SOURCES += $(RTL_DIR)/titan_comms_package.sv
VERILOG_SOURCES += $(RTL_DIR)/add_2.sv
VERILOG_SOURCES += $(RTL_DIR)/core_interface.sv
VERILOG_SOURCES += $(RTL_DIR)/instruction_handler.sv
VERILOG_SOURCES += $(TEST_DIR)/dut_core_interface.sv
VERILOG_SOURCES += $(TEST_DIR)/dut_instruction_handler.sv

# MODULE refers to python file containing tests
# TOPLEVEL refers to the top level module in the source file

# core interface
test_ci:
	$(MAKE) sim MODULE=test_core_interface TOPLEVEL=dut_core_interface

test_ih:
	$(MAKE) sim MODULE=test_instruction_handler TOPLEVEL=dut_instruction_handler


#   not sure how to tell verilator to use something else for a top-level module, or if its even possible
#   so to support multiple seperate tests we're just going to clean the directory and rebuild every time
clean_test_ci:
	$(MAKE) clean
	$(MAKE) sim MODULE=test_core_interface TOPLEVEL=dut_core_interface

clean_test_ih:
	$(MAKE) clean
	$(MAKE) sim MODULE=test_instruction_handler TOPLEVEL=dut_instruction_handler


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
