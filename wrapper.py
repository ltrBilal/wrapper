import math
import argparse


MEM_DEPTH : int = 8
MEM_WIDTH : int = 16

def generate_vhdl(MEM_DEPTH : int, MEM_WIDTH : int):

    ID_width : int = math.ceil(math.log2(MEM_DEPTH))
    rwx_width : int = 3
    adress_width : int = math.ceil((MEM_WIDTH-ID_width-rwx_width)/2)

    ################################################## Files names ##################################################

    wrapper_file_name : str = "wrapper"
    rules_array_file_name : str = "rules_array"
    interface_AXI_file_name   : str = "interface_AXI"

    ################################################## rules_array ##################################################

    rules_array : str = f"""library ieee;
use ieee.std_logic_1164.all;

package Memory_type is
    type MemoryArrayType is array (0 to {MEM_DEPTH-1}) of std_logic_vector({MEM_WIDTH-1} DOWNTO 0);
end package Memory_type;

----------------------------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.Memory_type.all;

entity {rules_array_file_name} is
    port(
        clk         : in std_logic;
        reset       : in std_logic;
        rule_number : in std_logic_vector({ID_width-1} DOWNTO 0);
        w_enable    : in std_logic;
        data_in     : in std_logic_vector({MEM_WIDTH - 1} DOWNTO 0);

        data_out    : out MemoryArrayType
    );
end {rules_array_file_name};

architecture {rules_array_file_name}_rtl of {rules_array_file_name} is
    signal memory_array : MemoryArrayType := (others => (others => '0') );
begin

    process(CLK)
    begin
        if rising_edge(CLK) then
            if RESET = '1' then
                memory_array <= (others => (others => '0'));
            else
                if w_enable = '1' then
                    memory_array(to_integer(unsigned(rule_number))) <= data_in;
                end if;
            end if;
        end if;
    end process;

    data_out <= memory_array;

end architecture;
"""
    ################################################## wrapper ######################################################

    wrapper : str = f"""library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.Memory_type.all;

entity {wrapper_file_name} is

    port (
        clk     : in std_logic;
        reset   : in std_logic;
        -- for rules array
        w_rule_enable   : in std_logic;
        data_rule       : in std_logic_vector({MEM_WIDTH-1} downto 0);
        rule_number     : in std_logic_vector({rwx_width-1} downto 0);
        -- for wrapper
        MID_W   : in std_logic_vector({rwx_width-1} DOWNTO 0);
        MID_R   : in std_logic_vector({rwx_width-1} DOWNTO 0);
        x_enable : in std_logic;
        addr_w  : in std_logic_vector({adress_width-1} DOWNTO 0);
        addr_r  : in std_logic_vector({adress_width-1} DOWNTO 0);
        -- output
        wrapper_write_response  : out std_logic := '0';
        wrapper_read_response   : out std_logic := '0'
    );
end {wrapper_file_name};


architecture {wrapper_file_name}_rtl of {wrapper_file_name} is
        signal rules_array : MemoryArrayType;
begin

    -- instance of memory for rules
    {rules_array_file_name}_inst: entity work.{rules_array_file_name}
     port map(
        CLK => clk,
        RESET => reset,
        rule_number => rule_number,
        w_enable => w_rule_enable,
        data_in => data_rule,
        data_out => rules_array
    );

    -- process to check whether the master who requested the has the right to write or to read
    process (clk)
        variable res_w : std_logic := '0';
        variable res_r : std_logic := '0';
        
        variable field_id : std_logic_vector({ID_width-1} DOWNTO 0);
        variable field_rwx : std_logic_vector({rwx_width-1} DOWNTO 0);
        variable field_addr_min : std_logic_vector( {adress_width - 1} DOWNTO 0);
        variable field_addr_max : std_logic_vector( {adress_width - 1} DOWNTO 0);
        
    begin
        if rising_edge(clk) then
            if w_rule_enable /= '1' then
                res_w := '0';
                res_r := '0';    
                myloop:for i in 0 to {MEM_DEPTH-1} loop
                    field_id := rules_array(i)({MEM_WIDTH-1} DOWNTO {MEM_WIDTH-ID_width});
                    field_rwx := rules_array(i)({MEM_WIDTH-ID_width-1} DOWNTO {MEM_WIDTH-ID_width-rwx_width});
                    field_addr_min := rules_array(i)({MEM_WIDTH-ID_width-rwx_width-1} DOWNTO {MEM_WIDTH-ID_width-rwx_width-adress_width});
                    field_addr_max := rules_array(i)({MEM_WIDTH-ID_width-rwx_width-adress_width-1} DOWNTO 0);
                    if field_id = MID_W AND field_rwx = ("01" & x_enable) AND addr_w >= field_addr_min AND addr_w < field_addr_max then
                        res_w := '1';
                    end if;
                    if field_id = MID_R AND field_rwx = ("10" & x_enable) AND addr_r >= field_addr_min AND addr_r < field_addr_max then
                        res_r := '1';
                    end if;
                end loop;
                wrapper_write_response <= res_w;
                wrapper_read_response <= res_r;
            else
                wrapper_write_response <= '0';
                wrapper_read_response <= '0';
            end if;
        end if;
    end process;

end architecture;
"""
    ################################################## interface_AXI ##################################################

    interface_AXI : str = f"""library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.Memory_type.all;

entity {interface_AXI_file_name} is
    generic(
        -- Width of the AXI transaction ID
        C_S_AXI_ID_WIDTH       : integer := 3;
        -- Width of the AXI data in bits
        C_S_AXI_DATA_WIDTH     : integer := {MEM_WIDTH};
        -- Width of the AXI address in bits
        C_S_AXI_ADDR_WIDTH     : integer := {adress_width};
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
        rule_number        : in std_logic_vector({ID_width-1} downto 0);
        data_rule          : in std_logic_vector({MEM_WIDTH-1} downto 0);
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
end {interface_AXI_file_name};

architecture {interface_AXI_file_name}_arch of {interface_AXI_file_name} is

begin

    {wrapper_file_name}_inst: entity work.{wrapper_file_name}
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
"""
    ######################################################################################Génération###########################

    with open(f"{rules_array_file_name}.vhd", 'w') as f:
        f.write(rules_array)

    with open(f"{wrapper_file_name}.vhd", 'w') as f:
        f.write(wrapper)

    with open(f"{interface_AXI_file_name}.vhd", 'w') as f:
        f.write(interface_AXI)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate VHDL files for a wrapper with specified MEM_DEPTH and MEM_WIDTH.')
    parser.add_argument('--mem_depth','-d', type=int, default= MEM_DEPTH, required=False, help='Memory depth (number of memory cells)')
    parser.add_argument('--mem_width','-w', type=int, default= MEM_WIDTH, required=False, help='Memory width (width of each memory cell)')

    args = parser.parse_args()

    generate_vhdl( args.mem_depth, args.mem_width)

    if MEM_DEPTH == args.mem_depth and MEM_WIDTH == args.mem_width:
        print(f"VHDL files generated with MEM_DEPTH = {MEM_DEPTH} and MEM_WIDTH = {MEM_WIDTH} to change this values use the -d and -w options")
    else:
        MEM_DEPTH = args.mem_depth
        MEM_WIDTH = args.mem_width
        print(f"VHDL files generated with MEM_DEPTH = {args.mem_depth} and MEM_WIDTH = {args.mem_width}")

    