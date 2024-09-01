# scripts name
SCRIPT1 = wrapper.py
SCRIPT2 = test_bench_generator.py

# params
MEM_DEPTH ?= 8
MEM_WIDTH ?= 16

all: run_wrapper run_test_bench

# execute the wrapper script
run_wrapper:
	@echo "Executing $(SCRIPT1) with parameters $(MEM_DEPTH) and $(MEM_WIDTH)"
	python3 $(SCRIPT1) -d $(MEM_DEPTH) -w $(MEM_WIDTH)

# execute the test bench script
run_test_bench:
	@echo "Changing directory to test_bench_generator and executing $(SCRIPT2)"
	@cd test_bench_generator && python3 $(SCRIPT2) -d $(MEM_DEPTH) -w $(MEM_WIDTH)
