library ieee;
use ieee.std_logic_1164.all;

package Memory_type is
    type MemoryArrayType is array (0 to 7) of std_logic_vector(15 DOWNTO 0);
end package Memory_type;

----------------------------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.Memory_type.all;

entity rules_array is
    port(
        clk         : in std_logic;
        reset       : in std_logic;
        rule_number : in std_logic_vector(2 DOWNTO 0);
        w_enable    : in std_logic;
        data_in     : in std_logic_vector(15 DOWNTO 0);

        data_out    : out MemoryArrayType
    );
end rules_array;

architecture rules_array_rtl of rules_array is
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
