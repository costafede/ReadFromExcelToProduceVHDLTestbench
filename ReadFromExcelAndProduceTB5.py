import pandas as pd
import os
import shutil

def process_excel_column(excel_file, column, start_row, end_row, sheet_name="Sheet1"):
    """
    Read numeric data from a specific column and row range of an Excel file
    and return as a comma-separated string with proper formatting.
    """
    try:
        print(f"Reading Excel file: {excel_file}, sheet: {sheet_name}, column {column}, rows {start_row}-{end_row}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=column, skiprows=start_row-1, nrows=end_row-start_row+1)
        values = df.iloc[:, 0].tolist()

        # Format values - convert to integers if they are whole numbers to avoid ".0" suffix
        formatted_values = []
        for val in values:
            if isinstance(val, (int, float)) and float(val).is_integer():
                formatted_values.append(str(int(val)))
            else:
                formatted_values.append(str(val))

        formatted_line = ", ".join(formatted_values)
        return formatted_line
    except Exception as e:
        print(f"An error occurred while reading column {column}: {str(e)}")
        return None

def generate_vhdl_testbench(config_header_data, input_data, output_data, output_file):
    """Generate complete VHDL testbench with the provided data"""

    tb_template = """-- TB EXAMPLE PFRL 2024-2025

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity tb2425 is
end tb2425;

architecture project_tb_arch of tb2425 is

    constant CLOCK_PERIOD : time := 20 ns;

    -- Signals to be connected to the component
    signal tb_clk : std_logic := '0';
    signal tb_rst, tb_start, tb_done : std_logic;
    signal tb_add : std_logic_vector(15 downto 0);

    -- Signals for the memory
    signal tb_o_mem_addr, exc_o_mem_addr, init_o_mem_addr : std_logic_vector(15 downto 0);
    signal tb_o_mem_data, exc_o_mem_data, init_o_mem_data : std_logic_vector(7 downto 0);
    signal tb_i_mem_data : std_logic_vector(7 downto 0);
    signal tb_o_mem_we, tb_o_mem_en, exc_o_mem_we, exc_o_mem_en, init_o_mem_we, init_o_mem_en : std_logic;

    -- Memory
    type ram_type is array (65535 downto 0) of std_logic_vector(7 downto 0);
    signal RAM : ram_type := (OTHERS => "00000000");

    -- Scenario
    type scenario_config_type is array (0 to 16) of integer;
    constant SCENARIO_LENGTH : integer := 22533;
    constant SCENARIO_LENGTH_STL : std_logic_vector(15 downto 0) := std_logic_vector(to_unsigned(SCENARIO_LENGTH, 16));
    type scenario_type is array (0 to SCENARIO_LENGTH-1) of integer;

    signal scenario_config : scenario_config_type := (to_integer(unsigned(SCENARIO_LENGTH_STL(15 downto 8))),   -- K1
                                                      to_integer(unsigned(SCENARIO_LENGTH_STL(7 downto 0))),    -- K2
                                                      1,                                                        -- S
            {config_header_data}     -- C1-C14
                                                      );
    signal scenario_input : scenario_type := ( {input_data} );
    signal scenario_output : scenario_type :=( {output_data} );

    signal memory_control : std_logic := '0';      -- A signal to decide when the memory is accessed
                                                   -- by the testbench or by the project

    constant SCENARIO_ADDRESS : integer := 1234;    -- This value may arbitrarily change

    component project_reti_logiche is
        port (
                i_clk : in std_logic;
                i_rst : in std_logic;
                i_start : in std_logic;
                i_add : in std_logic_vector(15 downto 0);

                o_done : out std_logic;

                o_mem_addr : out std_logic_vector(15 downto 0);
                i_mem_data : in  std_logic_vector(7 downto 0);
                o_mem_data : out std_logic_vector(7 downto 0);
                o_mem_we   : out std_logic;
                o_mem_en   : out std_logic
        );
    end component project_reti_logiche;

begin
    UUT : project_reti_logiche
    port map(
                i_clk   => tb_clk,
                i_rst   => tb_rst,
                i_start => tb_start,
                i_add   => tb_add,

                o_done => tb_done,

                o_mem_addr => exc_o_mem_addr,
                i_mem_data => tb_i_mem_data,
                o_mem_data => exc_o_mem_data,
                o_mem_we   => exc_o_mem_we,
                o_mem_en   => exc_o_mem_en
    );

    -- Clock generation
    tb_clk <= not tb_clk after CLOCK_PERIOD/2;

    -- Process related to the memory
    MEM : process (tb_clk)
    begin
        if tb_clk'event and tb_clk = '1' then
            if tb_o_mem_en = '1' then
                if tb_o_mem_we = '1' then
                    RAM(to_integer(unsigned(tb_o_mem_addr))) <= tb_o_mem_data after 1 ns;
                    tb_i_mem_data <= tb_o_mem_data after 1 ns;
                else
                    tb_i_mem_data <= RAM(to_integer(unsigned(tb_o_mem_addr))) after 1 ns;
                end if;
            end if;
        end if;
    end process;

    memory_signal_swapper : process(memory_control, init_o_mem_addr, init_o_mem_data,
                                    init_o_mem_en,  init_o_mem_we,   exc_o_mem_addr,
                                    exc_o_mem_data, exc_o_mem_en, exc_o_mem_we)
    begin
        -- This is necessary for the testbench to work: we swap the memory
        -- signals from the component to the testbench when needed.

        tb_o_mem_addr <= init_o_mem_addr;
        tb_o_mem_data <= init_o_mem_data;
        tb_o_mem_en   <= init_o_mem_en;
        tb_o_mem_we   <= init_o_mem_we;

        if memory_control = '1' then
            tb_o_mem_addr <= exc_o_mem_addr;
            tb_o_mem_data <= exc_o_mem_data;
            tb_o_mem_en   <= exc_o_mem_en;
            tb_o_mem_we   <= exc_o_mem_we;
        end if;
    end process;

    -- This process provides the correct scenario on the signal controlled by the TB
    create_scenario : process
    begin
        wait for 50 ns;

        -- Signal initialization and reset of the component
        tb_start <= '0';
        tb_add <= (others=>'0');
        tb_rst <= '1';

        -- Wait some time for the component to reset...
        wait for 50 ns;

        tb_rst <= '0';
        memory_control <= '0';  -- Memory controlled by the testbench

        wait until falling_edge(tb_clk); -- Skew the testbench transitions with respect to the clock


        for i in 0 to 16 loop
            init_o_mem_addr<= std_logic_vector(to_unsigned(SCENARIO_ADDRESS+i, 16));
            init_o_mem_data<= std_logic_vector(to_unsigned(scenario_config(i),8));
            init_o_mem_en  <= '1';
            init_o_mem_we  <= '1';
            wait until rising_edge(tb_clk);
        end loop;

        for i in 0 to SCENARIO_LENGTH-1 loop
            init_o_mem_addr<= std_logic_vector(to_unsigned(SCENARIO_ADDRESS+17+i, 16));
            init_o_mem_data<= std_logic_vector(to_unsigned(scenario_input(i),8));
            init_o_mem_en  <= '1';
            init_o_mem_we  <= '1';
            wait until rising_edge(tb_clk);
        end loop;

        wait until falling_edge(tb_clk);

        memory_control <= '1';  -- Memory controlled by the component

        tb_add <= std_logic_vector(to_unsigned(SCENARIO_ADDRESS, 16));

        tb_start <= '1';

        while tb_done /= '1' loop
            wait until rising_edge(tb_clk);
        end loop;

        wait for 5 ns;

        tb_start <= '0';

        wait;

    end process;

    -- Process without sensitivity list designed to test the actual component.
    test_routine : process
    begin

        wait until tb_rst = '1';
        wait for 25 ns;
        assert tb_done = '0' report "TEST FALLITO o_done !=0 during reset" severity failure;
        wait until tb_rst = '0';

        wait until falling_edge(tb_clk);
        assert tb_done = '0' report "TEST FALLITO o_done !=0 after reset before start" severity failure;

        wait until rising_edge(tb_start);

        while tb_done /= '1' loop
            wait until rising_edge(tb_clk);
        end loop;

        assert tb_o_mem_en = '0' or tb_o_mem_we = '0' report "TEST FALLITO o_mem_en !=0 memory should not be written after done." severity failure;

        for i in 0 to SCENARIO_LENGTH-1 loop
            assert RAM(SCENARIO_ADDRESS+17+SCENARIO_LENGTH+i) = std_logic_vector(to_unsigned(scenario_output(i),8)) report "TEST FALLITO @ OFFSET=" & integer'image(17+SCENARIO_LENGTH+i) & " expected= " & integer'image(scenario_output(i)) & " actual=" & integer'image(to_integer(unsigned(RAM(SCENARIO_ADDRESS+17+SCENARIO_LENGTH+i)))) severity failure;
        end loop;

        wait until falling_edge(tb_start);
        assert tb_done = '1' report "TEST FALLITO o_done == 0 before start goes to zero" severity failure;
        wait until falling_edge(tb_done);

        assert false report "Simulation Ended! TEST PASSATO (EXAMPLE)" severity failure;
    end process;

end architecture;
"""
    # Format the template with the data
    vhdl_content = tb_template.format(
        config_header_data=config_header_data,
        input_data=input_data,
        output_data=output_data
    )

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(vhdl_content)

    print(f"VHDL testbench file created successfully: {output_file}")
    return True

def process_excel_to_testbench(excel_file, output_file=None):
    """Process required Excel data and generate a complete VHDL testbench file"""
    try:
        # First, try copying the file to a temporary location if it's in a restricted area
        if excel_file.startswith('/Users') and ('Downloads' in excel_file or 'Desktop' in excel_file):
            temp_file = os.path.join(os.getcwd(), os.path.basename(excel_file))
            print(f"Copying file to temporary location: {temp_file}")
            try:
                shutil.copy2(excel_file, temp_file)
                excel_file = temp_file
                print("File copied successfully")
            except Exception as e:
                print(f"Could not copy file: {e}")
                # Continue with original file

        # Default output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(excel_file)[0]
            output_file = f"{base_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}_testbench.vhd"

        # Process column B from Sheet2 (rows 14-27) for config header
        config_header_data = process_excel_column(excel_file, "B", 13, 26, "Sheet2")

        # Process column C from Sheet2 (rows 13-22545) for input scenario
        input_data = process_excel_column(excel_file, "C", 13, 22545, "Sheet2")

        # Process column D from Sheet2 (rows 13-22545) for output scenario
        output_data = process_excel_column(excel_file, "E", 13, 22545, "Sheet2")

        if config_header_data is None or input_data is None or output_data is None:
            print("Failed to read column data.")
            return False

        # Generate the complete VHDL testbench
        return generate_vhdl_testbench(config_header_data, input_data, output_data, output_file)

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    input_file = "progetto2425_python_used_copy.xlsx"

    # Process Excel data and create VHDL testbench
    process_excel_to_testbench(input_file)