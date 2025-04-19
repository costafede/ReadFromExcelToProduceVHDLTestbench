import pandas as pd
import os
from string import Template

# This script needs to be fixed

def read_excel_scenarios(excel_file):
    """Read scenarios from Excel file."""
    try:
        df = pd.read_excel(excel_file)
        scenarios = []

        # Process each row as a scenario
        for index, row in df.iterrows():
            scenario = {
                'id': index + 1,
                'config': [],
                'input': [],
                'output': [],
                'length': 0
            }

            # Parse configuration, input and output data from row
            # Adjust column names based on your actual Excel structure
            if 'config' in row:
                scenario['config'] = [int(x) for x in str(row['config']).split(',') if x.strip()]

            if 'input' in row:
                scenario['input'] = [int(x) for x in str(row['input']).split(',') if x.strip()]

            if 'output' in row:
                scenario['output'] = [int(x) for x in str(row['output']).split(',') if x.strip()]

            scenario['length'] = max(len(scenario['input']), len(scenario['output']))
            scenarios.append(scenario)

        return scenarios

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def generate_testbench(scenario, template_file="testbench_template.vhd", output_dir="testbenches"):
    """Generate a VHDL testbench file for a scenario."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Read the template file
        with open(template_file, 'r') as f:
            template_content = f.read()

        # Create template object
        template = Template(template_content)

        # Format configuration arrays as VHDL arrays
        config_array = ", ".join([str(x) for x in scenario['config']])
        input_array = ", ".join([str(x) for x in scenario['input']])
        output_array = ", ".join([str(x) for x in scenario['output']])

        # Substitute values in template
        testbench_content = template.substitute(
            SCENARIO_ID=scenario['id'],
            SCENARIO_LENGTH=scenario['length'],
            SCENARIO_CONFIG=config_array,
            SCENARIO_INPUT=input_array,
            SCENARIO_OUTPUT=output_array
        )

        # Write to output file
        output_file = os.path.join(output_dir, f"tb_scenario_{scenario['id']}.vhd")
        with open(output_file, 'w') as f:
            f.write(testbench_content)

        print(f"Generated testbench for scenario {scenario['id']}: {output_file}")

    except Exception as e:
        print(f"Error generating testbench for scenario {scenario['id']}: {e}")

def create_testbench_template():
    """Create a template file based on the provided testbench structure."""
    template_content = """library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_unsigned.all;

entity project_tb is
end project_tb;

architecture projecttb of project_tb is
    constant CLOCK_PERIOD : time := 100 ns;
    signal tb_clk : std_logic := '0';
    signal tb_rst : std_logic := '0';
    signal tb_start : std_logic := '0';
    signal tb_add : std_logic_vector(15 downto 0) := (others => '0');
    signal tb_done : std_logic;
    
    signal tb_o_mem_addr : std_logic_vector(15 downto 0);
    signal tb_o_mem_data : std_logic_vector(7 downto 0);
    signal tb_i_mem_data : std_logic_vector(7 downto 0);
    signal tb_o_mem_we   : std_logic;
    signal tb_o_mem_en   : std_logic;
    
    signal exc_o_mem_addr : std_logic_vector(15 downto 0);
    signal exc_o_mem_data : std_logic_vector(7 downto 0);
    signal exc_o_mem_we   : std_logic;
    signal exc_o_mem_en   : std_logic;
    
    signal init_o_mem_addr : std_logic_vector(15 downto 0);
    signal init_o_mem_data : std_logic_vector(7 downto 0);
    signal init_o_mem_we   : std_logic;
    signal init_o_mem_en   : std_logic;

    type ram_type is array (65535 downto 0) of std_logic_vector(7 downto 0);
    signal RAM: ram_type := (others => (others => '0'));
    
    constant SCENARIO_LENGTH : integer := $SCENARIO_LENGTH;
    
    -- Define scenario_config, scenario_input, and scenario_output arrays
    type scenario_config_type is array (0 to 16) of integer;
    constant scenario_config : scenario_config_type := ($SCENARIO_CONFIG);
    
    type scenario_input_type is array (0 to SCENARIO_LENGTH-1) of integer;
    constant scenario_input : scenario_input_type := ($SCENARIO_INPUT);
    
    type scenario_output_type is array (0 to SCENARIO_LENGTH-1) of integer;
    constant scenario_output : scenario_output_type := ($SCENARIO_OUTPUT);
    
    signal memory_control : std_logic := '0';
    constant SCENARIO_ADDRESS : integer := 1234;

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

        assert false report "Simulation Ended! TEST PASSATO (SCENARIO $SCENARIO_ID)" severity failure;
    end process;

end architecture;
"""
    with open("testbench_template.vhd", "w") as f:
        f.write(template_content)
    print("Created testbench template file: testbench_template.vhd")

def main():
    """Main function to execute the script."""
    # Create template file if it doesn't exist
    if not os.path.exists("testbench_template.vhd"):
        create_testbench_template()

    # Ask for Excel file path
    excel_file = input("Enter path to Excel file with scenarios: ")

    # Read scenarios from Excel
    scenarios = read_excel_scenarios(excel_file)

    if not scenarios:
        print("No scenarios found or error reading Excel file.")
        return

    # Generate only testbenches 3 and 5 as per filename
    for scenario in scenarios:
        if scenario['id'] in [3, 5]:
            generate_testbench(scenario)

    print("Testbench generation completed.")

if __name__ == "__main__":
    main()