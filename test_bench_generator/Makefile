GHDL=ghdl

SRC_DIR = ".."
SIM_DURATION = "1000us"
TEST_BENCH_ENTITY_NAME = "generated_tb"

all:
	@$(GHDL) -a $(SRC_DIR)/rules_array.vhd $(SRC_DIR)/wrapper.vhd 
	@$(GHDL) -a $(SRC_DIR)/interface_AXI.vhd
	@$(GHDL) -a Interface_AXI_tb.vhd
	@$(GHDL) -e $(TEST_BENCH_ENTITY_NAME)
	@$(GHDL) -r $(TEST_BENCH_ENTITY_NAME) --vcd=$(TEST_BENCH_ENTITY_NAME).vcd --stop-time=$(SIM_DURATION) --wave=Interface_AXI.ghw

	gtkwave $(TEST_BENCH_ENTITY_NAME).vcd waveform.gtkw