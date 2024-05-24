import csv
import os

def split_csv(file_path, output_folder, num_parts=6):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Read the CSV file
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = list(csv.reader(file))
        header = reader[0]
        rows = reader[1:]

    # Calculate the number of lines per part
    total_lines = len(rows)
    lines_per_part = total_lines // num_parts
    remainder = total_lines % num_parts

    start = 0

    # Create each part
    for i in range(num_parts):
        end = start + lines_per_part + (1 if i < remainder else 0)
        part_rows = rows[start:end]
        output_file_path = os.path.join(output_folder, f'part_{i+1}.csv')
        
        # Write the part to a new CSV file
        with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header)  # Write the header
            writer.writerows(part_rows)  # Write the rows for this part
        
        start = end

# Example usage
file_path = 'path/to/your/input.csv'
output_folder = 'path/to/output/folder'
num_parts = 6
split_csv(file_path, output_folder, num_parts)
