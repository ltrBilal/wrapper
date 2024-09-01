library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.Memory_type.all;

entity wrapper is

    port (
        clk     : in std_logic;
        reset   : in std_logic;
        -- for rules array
        w_rule_enable   : in std_logic;
        data_rule       : in std_logic_vector(15 downto 0);
        rule_number     : in std_logic_vector(2 downto 0);
        -- for wrapper
        MID_W   : in std_logic_vector(2 DOWNTO 0);
        MID_R   : in std_logic_vector(2 DOWNTO 0);
        x_enable : in std_logic;
        addr_w  : in std_logic_vector(4 DOWNTO 0);
        addr_r  : in std_logic_vector(4 DOWNTO 0);
        -- output
        wrapper_write_response  : out std_logic := '0';
        wrapper_read_response   : out std_logic := '0'
    );
end wrapper;


architecture wrapper_rtl of wrapper is
        signal rules_array : MemoryArrayType;
begin

    -- instance of memory for rules
    rules_array_inst: entity work.rules_array
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
        
        variable field_id : std_logic_vector(2 DOWNTO 0);
        variable field_rwx : std_logic_vector(2 DOWNTO 0);
        variable field_addr_min : std_logic_vector( 4 DOWNTO 0);
        variable field_addr_max : std_logic_vector( 4 DOWNTO 0);
        
    begin
        if rising_edge(clk) then
            if w_rule_enable /= '1' then
                res_w := '0';
                res_r := '0';    
                myloop:for i in 0 to 7 loop
                    field_id := rules_array(i)(15 DOWNTO 13);
                    field_rwx := rules_array(i)(12 DOWNTO 10);
                    field_addr_min := rules_array(i)(9 DOWNTO 5);
                    field_addr_max := rules_array(i)(4 DOWNTO 0);
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
