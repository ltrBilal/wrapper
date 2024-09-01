import math
import argparse

MEM_DEPTH : int = 8
MEM_WIDTH : int = 16

period : int = 10
unite  : str = "us"

def decimal_to_binary(decimal, number_of_bits):
    binary = bin(decimal)[2:]
    size = len(binary)
    if(size < number_of_bits):
        binary = binary.zfill(number_of_bits)
    elif size > number_of_bits:
        binary = binary[-number_of_bits:]
    return binary

def hexa_to_binary(hexa, number_of_bits):
    # hexa to int
    decimal = int(hexa, 16)
    return decimal_to_binary(decimal, number_of_bits)

def generate_test_bench_file(MEM_DEPTH : int, MEM_WIDTH : int):

    ID_width : int = math.ceil(math.log2(MEM_DEPTH))
    rwx_width : int = 3
    adress_width : int = math.ceil((MEM_WIDTH-ID_width-rwx_width)/2)

    test_bench : str = f"""library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;


entity generated_tb is
end generated_tb;

architecture arch_interface of generated_tb is

    -- AXI Transaction ID width
    signal C_S_AXI_ID_WIDTH       : integer := 3; -- Width of the AXI transaction ID

    -- AXI Data width in bits
    signal C_S_AXI_DATA_WIDTH     : integer := 16; -- Width of AXI data in bits

    -- AXI Address width in bits
    signal C_S_AXI_ADDR_WIDTH     : integer := 5;  -- Width of AXI address in bits

    -- Optional user signal widths for AW, AR, W, R, and B channels
    signal C_S_AXI_AWUSER_WIDTH   : integer := 0;  -- Width of user signals for write address channel (AW)
    signal C_S_AXI_ARUSER_WIDTH   : integer := 0;  -- Width of user signals for read address channel (AR)
    signal C_S_AXI_WUSER_WIDTH    : integer := 0;  -- Width of user signals for write data channel (W)
    signal C_S_AXI_RUSER_WIDTH    : integer := 0;  -- Width of user signals for read data channel (R)
    signal C_S_AXI_BUSER_WIDTH    : integer := 0;  -- Width of user signals for write response channel (B)

    -- Master ID width
    signal C_MASTER_ID_WIDTH      : integer := 3;  -- Width of the master ID

    -- Master ID signals
    signal MID_R                  : std_logic_vector(C_MASTER_ID_WIDTH-1 downto 0); -- ID of the master requesting a read operation
    signal MID_W                  : std_logic_vector(C_MASTER_ID_WIDTH-1 downto 0); -- ID of the master requesting a write operation

    -- Rule-related signals
    signal rule_number            : std_logic_vector(2 downto 0); -- Number representing the rule
    signal data_rule              : std_logic_vector(15 downto 0); -- Data associated with the rule
    signal w_rule_enable          : std_logic; -- Signal to indicate that a rule is being written to memory

    -- Enable signal
    signal x_enable               : std_logic; -- General enable signal

    -- Response signals
    signal wrapper_write_response : std_logic; -- Signal indicating the response to a write operation
    signal wrapper_read_response  : std_logic; -- Signal indicating the response to a read operation

    signal error_signal           : std_logic := '0';

    -- Declaration of a global log file
    file log_file : text; -- Global log file for recording operations

    -- Declaration of a function for write request verification 
    function check_write_test( wrapper_response : std_logic; test_number : integer) return boolean is
        variable log_line : line;
    begin
        if wrapper_write_response = wrapper_response then
            report "Test PASSED" severity note;
            return true;
        else
            report "Test FAILED" severity error;
            write(log_line, string'("ERROR : test number "));
            write(log_line, integer'image(test_number));
            write(log_line, string'(" FAILED "));
            writeline(log_file, log_line);
            return false;
        end if;
    end function;

    -- Declaration of a function for read request verification
    function check_read_test( wrapper_response : std_logic; test_number : integer) return boolean is
        variable log_line : line;
    begin
        if wrapper_read_response = wrapper_response then
            report "Test PASSED" severity note;
            return true;
        else
            report "Test FAILED" severity error;
            write(log_line, string'("ERROR : test number "));
            write(log_line, integer'image(test_number));
            write(log_line, string'(" FAILED "));
            writeline(log_file, log_line);
            return false;
        end if;
    end function;



    ------------------------------------------- AXI signals -------------------------------------------
    -- Clock signal
    signal S_AXI_ACLK        : std_logic;

    -- Signal for reset
    signal S_AXI_ARESETN     : std_logic;

    -- Write address and control channels
    signal S_AXI_AWID        : std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0);   -- Write transaction identifier
    signal S_AXI_AWADDR      : std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0); -- Address where the master wants to write
    signal S_AXI_AWLEN       : std_logic_vector(7 downto 0); -- Burst length (number of data transfers)
    signal S_AXI_AWSIZE      : std_logic_vector(2 downto 0); -- Size of each data transfer
    signal S_AXI_AWBURST     : std_logic_vector(1 downto 0); -- Burst type (INCR, WRAP, etc.)
    signal S_AXI_AWLOCK      : std_logic; -- Lock signal for the transaction
    signal S_AXI_AWCACHE     : std_logic_vector(3 downto 0); -- Cache attributes
    signal S_AXI_AWPROT      : std_logic_vector(2 downto 0); -- Protection attributes
    signal S_AXI_AWQOS       : std_logic_vector(3 downto 0); -- Quality of Service
    signal S_AXI_AWREGION    : std_logic_vector(3 downto 0); -- Address region
    signal S_AXI_AWUSER      : std_logic_vector(C_S_AXI_AWUSER_WIDTH-1 downto 0); -- Additional user signals
    signal S_AXI_AWVALID     : std_logic; -- Indicates that the write address and control signals are valid

    -- Write data and control channels
    signal S_AXI_WDATA       : std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0); -- Write data
    signal S_AXI_WSTRB       : std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0); -- Data strobes (indicates valid bytes)
    signal S_AXI_WLAST       : std_logic; -- Indicates the last data transfer in a burst
    signal S_AXI_WUSER       : std_logic_vector(C_S_AXI_WUSER_WIDTH-1 downto 0); -- Additional user signals
    signal S_AXI_WVALID      : std_logic; -- Indicates that the write data is valid

    -- Write response from the master
    signal S_AXI_BREADY      : std_logic; -- Indicates that the master is ready to accept a write response

    -- Read address and control channels
    signal S_AXI_ARID        : std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0);   -- Read transaction identifier
    signal S_AXI_ARADDR      : std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0); -- Address where the master wants to read
    signal S_AXI_ARLEN       : std_logic_vector(7 downto 0); -- Burst length for read transaction (number of data transfers)
    signal S_AXI_ARSIZE      : std_logic_vector(2 downto 0); -- Size of each data transfer
    signal S_AXI_ARBURST     : std_logic_vector(1 downto 0); -- Burst type for read transaction (INCR, WRAP)
    signal S_AXI_ARLOCK      : std_logic; -- Lock signal for the read transaction
    signal S_AXI_ARCACHE     : std_logic_vector(3 downto 0); -- Cache attributes for read
    signal S_AXI_ARPROT      : std_logic_vector(2 downto 0); -- Protection attributes for read
    signal S_AXI_ARQOS       : std_logic_vector(3 downto 0); -- Quality of Service for read
    signal S_AXI_ARREGION    : std_logic_vector(3 downto 0); -- Address region for read
    signal S_AXI_ARUSER      : std_logic_vector(C_S_AXI_ARUSER_WIDTH-1 downto 0); -- Additional user signals for read
    signal S_AXI_ARVALID     : std_logic; -- Indicates that the read address and control signals are valid

    -- Read response from the master
    signal S_AXI_RREADY      : std_logic; -- Indicates that the master is ready to accept read data

    -- Signals from slave to master

    -- Accepting write transactions
    signal S_AXI_AWREADY     : std_logic; -- Indicates that the slave is ready to accept a write address and control signals
    signal S_AXI_WREADY      : std_logic; -- Indicates that the slave is ready to accept write data

    -- Write response from the slave
    signal S_AXI_BID         : std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0); -- Write transaction identifier
    signal S_AXI_BRESP       : std_logic_vector(1 downto 0); -- Write response code (OKAY, EXOKAY, SLVERR, DECERR)
    signal S_AXI_BUSER       : std_logic_vector(C_S_AXI_BUSER_WIDTH-1 downto 0); -- Additional user signals
    signal S_AXI_BVALID      : std_logic; -- Indicates that the write response is valid

    -- Accepting read transactions
    signal S_AXI_ARREADY     : std_logic; -- Indicates that the slave is ready to accept a read address and control signals

    -- Read response from the slave
    signal S_AXI_RID         : std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0); -- Read transaction identifier
    signal S_AXI_RDATA       : std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0); -- Read data
    signal S_AXI_RRESP       : std_logic_vector(1 downto 0); -- Read response code (OKAY, EXOKAY, SLVERR, DECERR)
    signal S_AXI_RLAST       : std_logic; -- Indicates the last data transfer in a read burst
    signal S_AXI_RUSER       : std_logic_vector(C_S_AXI_RUSER_WIDTH-1 downto 0); -- Additional user signals
    signal S_AXI_RVALID      : std_logic; -- Indicates that the read data is valid

begin

    interface_AXI_inst: entity work.interface_AXI
    generic map(
        C_S_AXI_ID_WIDTH => C_S_AXI_ID_WIDTH,
        C_S_AXI_DATA_WIDTH => C_S_AXI_DATA_WIDTH,
        C_S_AXI_ADDR_WIDTH => C_S_AXI_ADDR_WIDTH,
        C_S_AXI_AWUSER_WIDTH => C_S_AXI_AWUSER_WIDTH,
        C_S_AXI_ARUSER_WIDTH => C_S_AXI_ARUSER_WIDTH,
        C_S_AXI_WUSER_WIDTH => C_S_AXI_WUSER_WIDTH,
        C_S_AXI_RUSER_WIDTH => C_S_AXI_RUSER_WIDTH,
        C_S_AXI_BUSER_WIDTH => C_S_AXI_BUSER_WIDTH,
        C_MASTER_ID_WIDTH => C_MASTER_ID_WIDTH
    )
    port map(
        rule_number => rule_number,
        data_rule => data_rule,
        w_rule_enable => w_rule_enable,
        MID_R => MID_R,
        MID_W => MID_W,
        x_enable => x_enable,
        wrapper_write_response => wrapper_write_response,
        wrapper_read_response => wrapper_read_response,
        S_AXI_ACLK => S_AXI_ACLK,
        S_AXI_ARESETN => S_AXI_ARESETN,
        S_AXI_AWID => S_AXI_AWID,
        S_AXI_AWADDR => S_AXI_AWADDR,
        S_AXI_AWLEN => S_AXI_AWLEN,
        S_AXI_AWSIZE => S_AXI_AWSIZE,
        S_AXI_AWBURST => S_AXI_AWBURST,
        S_AXI_AWLOCK => S_AXI_AWLOCK,
        S_AXI_AWCACHE => S_AXI_AWCACHE,
        S_AXI_AWPROT => S_AXI_AWPROT,
        S_AXI_AWQOS => S_AXI_AWQOS,
        S_AXI_AWREGION => S_AXI_AWREGION,
        S_AXI_AWUSER => S_AXI_AWUSER,
        S_AXI_AWVALID => S_AXI_AWVALID,
        S_AXI_WDATA => S_AXI_WDATA,
        S_AXI_WSTRB => S_AXI_WSTRB,
        S_AXI_WLAST => S_AXI_WLAST,
        S_AXI_WUSER => S_AXI_WUSER,
        S_AXI_WVALID => S_AXI_WVALID,
        S_AXI_BREADY => S_AXI_BREADY,
        S_AXI_ARID => S_AXI_ARID,
        S_AXI_ARADDR => S_AXI_ARADDR,
        S_AXI_ARLEN => S_AXI_ARLEN,
        S_AXI_ARSIZE => S_AXI_ARSIZE,
        S_AXI_ARBURST => S_AXI_ARBURST,
        S_AXI_ARLOCK => S_AXI_ARLOCK,
        S_AXI_ARCACHE => S_AXI_ARCACHE,
        S_AXI_ARPROT => S_AXI_ARPROT,
        S_AXI_ARQOS => S_AXI_ARQOS,
        S_AXI_ARREGION => S_AXI_ARREGION,
        S_AXI_ARUSER => S_AXI_ARUSER,
        S_AXI_ARVALID => S_AXI_ARVALID,
        S_AXI_RREADY => S_AXI_RREADY,
        S_AXI_AWREADY => S_AXI_AWREADY,
        S_AXI_WREADY => S_AXI_WREADY,
        S_AXI_BID => S_AXI_BID,
        S_AXI_BRESP => S_AXI_BRESP,
        S_AXI_BUSER => S_AXI_BUSER,
        S_AXI_BVALID => S_AXI_BVALID,
        S_AXI_ARREADY => S_AXI_ARREADY,
        S_AXI_RID => S_AXI_RID,
        S_AXI_RDATA => S_AXI_RDATA,
        S_AXI_RRESP => S_AXI_RRESP,
        S_AXI_RLAST => S_AXI_RLAST,
        S_AXI_RUSER => S_AXI_RUSER,
        S_AXI_RVALID => S_AXI_RVALID
    );

        -- Clock simulation
        horloge_process : process
        begin
            S_AXI_ACLK <= '0';
            wait for {period/2} {unite};
            S_AXI_ACLK <= '1';
            wait for {period/2} {unite};
        end process;

        -- S_AXI_ARESETN simulation
        reset_process : process
        begin
            S_AXI_ARESETN <= '1';
            wait for {period/2} {unite};
            S_AXI_ARESETN <= '0';
            wait;
        end process;
    """

    mem_config = open("memory_configuration.txt", 'r')
    lines = mem_config.readlines()

    # start of process
    memory_process : str = f"""\t-- simulation of memory configuration 
        memory_process : process
        begin
            w_rule_enable <= '0';
            data_rule <= (others => '-');
            rule_number <= "---";
            wait for {period/2} {unite};
    """

    i : int = 0 # for rules number
    for line in lines:
        # to ignore comments line
        line = line.split('#')[0].strip()
        if not line:
            continue
        memory_process += f"""\t\trule_number <= "{decimal_to_binary(i, ID_width)}";
            w_rule_enable <= '1';
            data_rule <= "{hexa_to_binary(line, MEM_WIDTH)}";
            wait for {period} {unite};
    """
        i += 1
    # end of process
    memory_process += """\t\tw_rule_enable <= '0';
            data_rule <= (others => '-');
            rule_number <= "---";
            wait;
        end process;

    """
    # start of wrapper process simulation
    wrapper_process = """\t-- request simulation
    wrapper_process : process
        variable log_line : line; -- Variable for writing lines to the file
        variable test_resp : boolean;
    begin
        file_open(log_file, "test_bench.log", write_mode);
        wait for 30 us;
"""

    f = open("request.txt", 'r')
    lines = f.readlines()
    i : int = 1
    for line in lines:
        # ignore comment lines and empty lines
        line = line.split('#')[0].strip()
        if not line:
            continue
        MID : str = None
        ADD : str = None
        check_function : str = None
        tab = line.split() # put the line in a table, each field in a column
        # find in witch mode we are (read or write)
        rwx = hexa_to_binary(tab[1], rwx_width)
        if rwx[0] == '1':
            MID = "MID_R"
            ADD = "S_AXI_ARADDR"
            check_function = "check_read_test"
        else:
            MID = "MID_W"
            ADD = "S_AXI_AWADDR"
            check_function = "check_write_test"
        info : str = f"""



"""
        wrapper_process += f"""\t\t-----------------------------------TEST {i}------------------------------
        {MID} <= "{hexa_to_binary(tab[0], ID_width)}";
        x_enable <= '{rwx[2]}'; 
        {ADD} <= "{hexa_to_binary(tab[2], adress_width)}";
        wait for 10 us;
        test_resp := {check_function}('{tab[3]}', {i});
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("{MID} = {tab[0]}"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = {tab[1]}"));
            writeline(log_file, log_line);
            write(log_line, string'("{ADD} = {tab[2]}"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected {tab[3]} but the test return { 1 - int(tab[3])}"));
            writeline(log_file, log_line);
        end if;
"""
        i += 1

    # end of wrapper process simulation
    wrapper_process += """\t\t-- close file
        file_close(log_file);
        
        MID_W <= (others => '-');
        MID_R <= (others => '-');
        wait;
    end process;
end architecture;
"""

    test_bench += memory_process
    test_bench += wrapper_process

    test = open("Interface_AXI_tb.vhd", 'w')
    test.write(test_bench)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate VHDL test bench files for a wrapper with specified MEM_DEPTH and MEM_WIDTH.')
    parser.add_argument('--mem_depth','-d', type=int, default= MEM_DEPTH, required=False, help='Memory depth (number of memory cells)')
    parser.add_argument('--mem_width','-w', type=int, default= MEM_WIDTH, required=False, help='Memory width (width of each memory cell)')

    args = parser.parse_args()

    generate_test_bench_file( args.mem_depth, args.mem_width)

    if MEM_DEPTH == args.mem_depth and MEM_WIDTH == args.mem_width:
        print(f"VHDL test bench files generated with MEM_DEPTH = {MEM_DEPTH} and MEM_WIDTH = {MEM_WIDTH} to change this values use the -d and -w options")
    else:
        MEM_DEPTH = args.mem_depth
        MEM_WIDTH = args.mem_width
        print(f"VHDL test bench files generated with MEM_DEPTH = {args.mem_depth} and MEM_WIDTH = {args.mem_width}")
