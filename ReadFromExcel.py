import pandas as pd
import os
import shutil

# First version, old code

def process_excel_column(excel_file, column, start_row, end_row, sheet_name="Sheet1", output_txt_file=None):
    """
    Read numeric data from a specific column and row range of an Excel file
    and save it to a text file as a single line of comma-separated values.
    """
    try:
        # Check if the Excel file exists
        if not os.path.exists(excel_file):
            print(f"Error: File '{excel_file}' not found")
            return False

        # Create output filename if not provided
        if output_txt_file is None:
            base_name = os.path.splitext(excel_file)[0]
            output_txt_file = f"{base_name}_{sheet_name}_column_{column}_{start_row}-{end_row}.txt"

            # Make sure output directory exists and is writable
            output_dir = os.path.dirname(output_txt_file)
            if output_dir and not os.access(output_dir, os.W_OK):
                # If output directory not writable, use current directory
                output_txt_file = f"{sheet_name}_column_{column}_{start_row}-{end_row}.txt"
                print(f"Warning: Cannot write to original location, using current directory instead")

        # Read the specified column starting from specified row
        print(f"Reading Excel file: {excel_file}, sheet: {sheet_name}, column {column}, rows {start_row}-{end_row}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=column, skiprows=start_row-1, nrows=end_row-start_row+1)

        # Get the values as a list
        values = df.iloc[:, 0].tolist()

        # Convert to strings and join with ", "
        formatted_line = ", ".join(str(val) for val in values)

        # Write to text file (single line)
        with open(output_txt_file, 'w', encoding='utf-8') as f:
            f.write(formatted_line)

        print(f"Text file created successfully: {output_txt_file}")
        return True

    except PermissionError:
        print(f"Permission error: Cannot access '{excel_file}'")
        print("Tips: \n- Make sure the file is not open in another program\n"
              "- Try copying the file to your project directory\n"
              "- On macOS, grant Full Disk Access to your terminal/IDE")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def process_excel_data(excel_file, output_c_main=None, output_f=None, output_g=None, output_c_header=None):
    """Process all required ranges from the Excel file"""
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

        # Process column C from Sheet2 (rows 13-22545)
        result_c_main = process_excel_column(excel_file, "C", 13, 22545, "Sheet2", output_c_main)

        # Process column D from Sheet2 (rows 13-22545) for order 3 filter
        result_f = process_excel_column(excel_file, "D", 13, 22545, "Sheet2", output_f)

        # Process column E from Sheet2 (rows 13-22545) for order 5 filter
        result_g = process_excel_column(excel_file, "E", 13, 22545, "Sheet2", output_g)

        # Process column B header (keeping this the same for now, but adding sheet parameter)
        result_c_header = process_excel_column(excel_file, "B", 13, 19, "Sheet2", output_c_header)

        return result_c_main and result_f and result_g and result_c_header

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    input_file = input("Enter the path to the Excel file: ")

    # Process all required ranges
    process_excel_data(input_file)