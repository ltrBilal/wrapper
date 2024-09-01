library ieee;
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
            wait for 5.0 us;
            S_AXI_ACLK <= '1';
            wait for 5.0 us;
        end process;

        -- S_AXI_ARESETN simulation
        reset_process : process
        begin
            S_AXI_ARESETN <= '1';
            wait for 5.0 us;
            S_AXI_ARESETN <= '0';
            wait;
        end process;
    	-- simulation of memory configuration 
        memory_process : process
        begin
            w_rule_enable <= '0';
            data_rule <= (others => '-');
            rule_number <= "---";
            wait for 5.0 us;
    		rule_number <= "000";
            w_rule_enable <= '1';
            data_rule <= "0000100000011111";
            wait for 10 us;
    		rule_number <= "001";
            w_rule_enable <= '1';
            data_rule <= "1001000001111100";
            wait for 10 us;
    		rule_number <= "010";
            w_rule_enable <= '1';
            data_rule <= "0011010001111110";
            wait for 10 us;
    		w_rule_enable <= '0';
            data_rule <= (others => '-');
            rule_number <= "---";
            wait;
        end process;

    	-- request simulation
    wrapper_process : process
        variable log_line : line; -- Variable for writing lines to the file
        variable test_resp : boolean;
    begin
        file_open(log_file, "test_bench.log", write_mode);
        wait for 30 us;
		-----------------------------------TEST 1------------------------------
        MID_W <= "000";
        x_enable <= '1'; 
        S_AXI_AWADDR <= "01100";
        wait for 10 us;
        test_resp := check_write_test('1', 1);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_W = 0"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 3"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_AWADDR = 0C"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 1 but the test return 0"));
            writeline(log_file, log_line);
        end if;
		-----------------------------------TEST 2------------------------------
        MID_W <= "101";
        x_enable <= '0'; 
        S_AXI_AWADDR <= "01100";
        wait for 10 us;
        test_resp := check_write_test('1', 2);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_W = 5"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 2"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_AWADDR = 0C"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 1 but the test return 0"));
            writeline(log_file, log_line);
        end if;
		-----------------------------------TEST 3------------------------------
        MID_W <= "000";
        x_enable <= '0'; 
        S_AXI_AWADDR <= "01100";
        wait for 10 us;
        test_resp := check_write_test('1', 3);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_W = 0"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 2"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_AWADDR = 0C"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 1 but the test return 0"));
            writeline(log_file, log_line);
        end if;
		-----------------------------------TEST 4------------------------------
        MID_W <= "000";
        x_enable <= '0'; 
        S_AXI_AWADDR <= "11111";
        wait for 10 us;
        test_resp := check_write_test('0', 4);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_W = 0"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 2"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_AWADDR = 1F"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 0 but the test return 1"));
            writeline(log_file, log_line);
        end if;
		-----------------------------------TEST 5------------------------------
        MID_R <= "100";
        x_enable <= '1'; 
        S_AXI_ARADDR <= "01100";
        wait for 10 us;
        test_resp := check_read_test('1', 5);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_R = 4"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 5"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_ARADDR = 0C"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 1 but the test return 0"));
            writeline(log_file, log_line);
        end if;
		-----------------------------------TEST 6------------------------------
        MID_R <= "100";
        x_enable <= '0'; 
        S_AXI_ARADDR <= "01100";
        wait for 10 us;
        test_resp := check_read_test('1', 6);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_R = 4"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 4"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_ARADDR = 0C"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 1 but the test return 0"));
            writeline(log_file, log_line);
        end if;
		-----------------------------------TEST 7------------------------------
        MID_R <= "001";
        x_enable <= '1'; 
        S_AXI_ARADDR <= "01100";
        wait for 10 us;
        test_resp := check_read_test('0', 7);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_R = 1"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 5"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_ARADDR = 0C"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 0 but the test return 1"));
            writeline(log_file, log_line);
        end if;
		-----------------------------------TEST 8------------------------------
        MID_R <= "001";
        x_enable <= '1'; 
        S_AXI_ARADDR <= "11111";
        wait for 10 us;
        test_resp := check_read_test('0', 8);
        if test_resp then
            error_signal <= '0';
        else
            error_signal <= '1';
            write(log_line, string'("MID_R = 1"));
            writeline(log_file, log_line);
            write(log_line, string'("rwx = 5"));
            writeline(log_file, log_line);
            write(log_line, string'("S_AXI_ARADDR = 1F"));
            writeline(log_file, log_line);
            write(log_line, string'("Expected 0 but the test return 1"));
            writeline(log_file, log_line);
        end if;
		-- close file
        file_close(log_file);
        
        MID_W <= (others => '-');
        MID_R <= (others => '-');
        wait;
    end process;
end architecture;
