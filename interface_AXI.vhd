library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.Memory_type.all;

entity interface_AXI is
    generic(
        -- Width of the AXI transaction ID
        C_S_AXI_ID_WIDTH       : integer := 3;
        -- Width of the AXI data in bits
        C_S_AXI_DATA_WIDTH     : integer := 16;
        -- Width of the AXI address in bits
        C_S_AXI_ADDR_WIDTH     : integer := 5;
        -- Width of the user signals for AW, AR, W, R, and B channels
        -- optional
        C_S_AXI_AWUSER_WIDTH   : integer := 0;
        C_S_AXI_ARUSER_WIDTH   : integer := 0;
        C_S_AXI_WUSER_WIDTH    : integer := 0;
        C_S_AXI_RUSER_WIDTH    : integer := 0;
        C_S_AXI_BUSER_WIDTH    : integer := 0;

        C_MASTER_ID_WIDTH      : integer := 3
    );
    port(
        -- Memory configuration
        rule_number        : in std_logic_vector(2 downto 0);
        data_rule          : in std_logic_vector(15 downto 0);
        w_rule_enable      : in std_logic; -- Signal to indicate that a rule is being written into memory

        -- Master IDs
        MID_R              : in std_logic_vector(C_MASTER_ID_WIDTH-1 downto 0); -- Signal for the ID of the master requesting the read
        MID_W              : in std_logic_vector(C_MASTER_ID_WIDTH-1 downto 0); -- Signal for the ID of the master requesting the write

        x_enable           : in std_logic;

        -- Signals for the responses
        wrapper_write_response  : out std_logic;
        wrapper_read_response   : out std_logic;

        ------------------------------------------- AXI signals -------------------------------------------
        -- Clock
        S_AXI_ACLK        : in std_logic;
        -- Reset signal
        S_AXI_ARESETN     : in std_logic;

        -- Write address and control channels
        S_AXI_AWID        : in std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0);   -- Write transaction ID
        S_AXI_AWADDR      : in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0); -- Address where the master wants to write
        S_AXI_AWLEN       : in std_logic_vector(7 downto 0); -- Transaction length (number of data transfers)
        S_AXI_AWSIZE      : in std_logic_vector(2 downto 0); -- Size of each data transfer
        S_AXI_AWBURST     : in std_logic_vector(1 downto 0); -- Burst type (INCR, WRAP, etc.)
        S_AXI_AWLOCK      : in std_logic; -- Locking of the transaction
        S_AXI_AWCACHE     : in std_logic_vector(3 downto 0); -- Cache attributes
        S_AXI_AWPROT      : in std_logic_vector(2 downto 0); -- Protection attributes
        S_AXI_AWQOS       : in std_logic_vector(3 downto 0); -- Quality of Service
        S_AXI_AWREGION    : in std_logic_vector(3 downto 0); -- Address region
        S_AXI_AWUSER      : in std_logic_vector(C_S_AXI_AWUSER_WIDTH-1 downto 0); -- Additional user signals 
        S_AXI_AWVALID     : in std_logic; -- Indicates that the write address and control signals are valid

        -- Write data and control channels
        S_AXI_WDATA       : in std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0); -- Write data
        S_AXI_WSTRB       : in std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0); -- Data strobes (indicates valid bytes)
        S_AXI_WLAST       : in std_logic; -- Indicates the last data transfer in a burst
        S_AXI_WUSER       : in std_logic_vector(C_S_AXI_WUSER_WIDTH-1 downto 0); -- Additional user signals 
        S_AXI_WVALID      : in std_logic; -- Indicates that the write data is valid

        -- Write response from the master
        S_AXI_BREADY      : in std_logic; -- Indicates that the master is ready to accept a write response

        -- Read address and control channels
        S_AXI_ARID        : in std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0);   -- Read transaction ID
        S_AXI_ARADDR      : in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0); -- Address where the master wants to read
        S_AXI_ARLEN       : in std_logic_vector(7 downto 0); -- Read transaction length (number of data transfers)
        S_AXI_ARSIZE      : in std_logic_vector(2 downto 0); -- Size of each data transfer
        S_AXI_ARBURST     : in std_logic_vector(1 downto 0); -- Burst type (INCR, WRAP)
        S_AXI_ARLOCK      : in std_logic; -- Locking of the read transaction
        S_AXI_ARCACHE     : in std_logic_vector(3 downto 0); -- Cache attributes for reading
        S_AXI_ARPROT      : in std_logic_vector(2 downto 0); -- Protection attributes for reading
        S_AXI_ARQOS       : in std_logic_vector(3 downto 0); -- Quality of Service for reading
        S_AXI_ARREGION    : in std_logic_vector(3 downto 0); -- Address region for reading
        S_AXI_ARUSER      : in std_logic_vector(C_S_AXI_ARUSER_WIDTH-1 downto 0); -- Additional user signals for reading 
        S_AXI_ARVALID     : in std_logic; -- Indicates that the read address and control signals are valid

        -- Read response from the master
        S_AXI_RREADY      : in std_logic; -- Indicates that the master is ready to accept read data

        -- Slave to master output signals

        -- Receipt of write transactions
        S_AXI_AWREADY     : out std_logic; -- Indicates that the slave is ready to accept a write address and control
        S_AXI_WREADY      : out std_logic; -- Indicates that the slave is ready to accept write data

        -- Write response from the slave
        S_AXI_BID         : out std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0); -- Write transaction ID
        S_AXI_BRESP       : out std_logic_vector(1 downto 0); -- Write response code (OKAY, EXOKAY, SLVERR, DECERR)
        S_AXI_BUSER       : out std_logic_vector(C_S_AXI_BUSER_WIDTH-1 downto 0); -- Additional user signals 
        S_AXI_BVALID      : out std_logic; -- Indicates that the write response is valid

        -- Receipt of read transactions
        S_AXI_ARREADY     : out std_logic; -- Indicates that the slave is ready to accept a read address and control

        -- Read response from the slave
        S_AXI_RID         : out std_logic_vector(C_S_AXI_ID_WIDTH-1 downto 0); -- Read transaction ID
        S_AXI_RDATA       : out std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0); -- Read data
        S_AXI_RRESP       : out std_logic_vector(1 downto 0); -- Read response code (OKAY, EXOKAY, SLVERR, DECERR)
        S_AXI_RLAST       : out std_logic; -- Indicates the last data transfer in a read burst
        S_AXI_RUSER       : out std_logic_vector(C_S_AXI_RUSER_WIDTH-1 downto 0); -- Additional user signals 
        S_AXI_RVALID      : out std_logic  -- Indicates that the read data is valid
    );
end interface_AXI;

architecture interface_AXI_arch of interface_AXI is

begin

    wrapper_inst: entity work.wrapper
     port map(
        clk => S_AXI_ACLK,
        reset => S_AXI_ARESETN,
        w_rule_enable => w_rule_enable,
        data_rule => data_rule,
        rule_number => rule_number,
        MID_W => MID_W,
        MID_R => MID_R,
        x_enable => x_enable,
        addr_w => S_AXI_AWADDR,
        addr_r => S_AXI_ARADDR,
        wrapper_write_response => wrapper_write_response,
        wrapper_read_response => wrapper_read_response
    );

end architecture;
