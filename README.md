# VHDL Testbench Generator for Reti Logiche Project

## Disclaimer

> **No Warranty of Accuracy**
>
> This project is provided *"as is"* without any guarantees or warranties of any kind, either express or implied. While every effort has been made to ensure the correctness and reliability of the content and functionality, i cannot guarantee that it is free from bugs or errors. Use at your own risk.


## Overview
This repository contains Python scripts that automate the generation of VHDL testbenches for the Reti Logiche course project at Politecnico di Milano. The scripts read filter configuration and test data from Excel files and generate complete VHDL testbench files ready for simulation.

## Features
- Automatically extracts configuration parameters and test vectors from Excel spreadsheets
- Generates complete VHDL testbench files with proper formatting
- Supports both 3rd order and 5th order filter implementations
- Handles file path issues automatically with temporary file copying
- Provides detailed console output during execution

## Scripts
The repository contains two main scripts:

1. **ReadFromExcelAndProduceTB3.py** - Generates testbenches for 3rd order filter implementation (S=0)
2. **ReadFromExcelAndProduceTB5.py** - Generates testbenches for 5th order filter implementation (S=1)

The only difference between these scripts is the S parameter (filter selection) and the output data column reference.

## Requirements
- Python 3.x
- pandas library
- Excel file with test data organized according to the expected format

## Installation
1. Clone this repository or download the script files
2. Install required dependencies:
```bash
pip install pandas
```

## Usage
1. Place your Excel data file in an accessible location
2. Run the script with Python:
```bash
python ReadFromExcelAndProduceTB3.py  # For 3rd order filter testbench
# OR
python ReadFromExcelAndProduceTB5.py  # For 5th order filter testbench
```

3. By default, the scripts look for a file named `progetto2425_python_used_copy.xlsx` in the current directory
4. To use a different input file or specify an output file name, modify the script as needed:
```python
if __name__ == "__main__":
    input_file = "your_excel_filename.xlsx"
    output_file = "your_desired_output.vhd"  # Optional
    process_excel_to_testbench(input_file, output_file)
```

## Excel File Format
Your Excel file should be structured as follows:
- **Sheet2**: Contains all test data
  - **Column B, Rows 13-26**: Config header data (C1-C14 configuration parameters)
  - **Column C, Rows 13-22545**: Input scenario (test input values)
  - **Column D, Rows 13-22545**: Output scenario for 3rd order filter
  - **Column E, Rows 13-22545**: Output scenario for 5th order filter

## Generated Testbench
The generated VHDL testbench file includes:
- All required library definitions and entity declarations
- Memory initialization with configuration parameters and test vectors
- Clock generation logic
- Signal handling between testbench and DUT (Device Under Test)
- Test routine with appropriate assertions
- Proper validation of output against expected results

## How It Works
1. The script reads configuration data and test vectors from the specified Excel file
2. It formats the data as comma-separated values suitable for VHDL array initialization
3. The formatted data is inserted into a template VHDL testbench file
4. The complete testbench is written to an output file, with a timestamp in the filename if no output name is specified

## Project Context
This tool is designed specifically for the Reti Logiche (Logic Networks) course project at Politecnico di Milano. The project involves implementing digital filters in VHDL, and these testbenches help verify the correctness of the implementation against provided test vectors.

## Customization
To adapt the scripts for different projects or test data:
- Modify the row and column references in the `process_excel_to_testbench` function
- Update the testbench template string in the `generate_vhdl_testbench` function
- Adjust the `SCENARIO_LENGTH` constant in the template if your test data size differs

## Troubleshooting
- If you encounter file access errors, the script attempts to copy the file to a temporary location
- Check console output for detailed information about script execution and potential errors
- Verify that your Excel file contains data in the expected format and locations

## Notes
- The testbench assumes a component named `project_reti_logiche` with the interface specified in the VHDL template
- The memory organization follows the project specifications with configuration parameters and test vectors at specific addresses
- The scenario address (1234) can be modified if needed, but it must match what your implementation expects
