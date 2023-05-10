__version__ = "0.2"
__author__ = "Ceberus132"
__description__ = "Decompressor for files with pzz compression (Monster Hunter, GioGio, etc.)"
__license__ = "MIT"

from pathlib import Path

print(f"{__description__} | Version {__version__} by {__author__}")


# Function to decompress the files data
def decompress(file_data):
    file_out = bytearray()
    file_size = len(file_data) & ~1  # Get the file size as a multiple of 2

    cb = 0  # Control bytes
    cb_bit = -1  # Cycle through control bit from 15 to 0
    i = 0
    while i < file_size:
        if cb_bit < 0:
            cb = file_data[i] | (file_data[i + 1] << 8)
            cb_bit = 15
            i += 2

        compress_flag = cb & (1 << cb_bit)
        cb_bit -= 1

        if compress_flag:
            c = file_data[i] | (file_data[i + 1] << 8)
            offset = (c & 0x7FF) << 1
            # Check, if we reached the end of compressed data
            if offset == 0:
                break
            count = (c >> 11) << 1
            if count == 0:
                i += 2
                c = file_data[i] | (file_data[i + 1] << 8)
                count = c << 1

            index = len(file_out) - offset
            for j in range(count):
                file_out.append(file_out[index + j])
        else:
            file_out.extend(file_data[i: i + 2])
        i += 2

    return file_out


if __name__ == '__main__':
    batch_yes = {"y", "yes", "Y", "Yes", "YES"}
    batch_no = {"n", "no", "N", "No", "NO"}
    while True:
        # Ask the user if he wants to batch process
        batch_convert = input("Do you want to batch process multiple files at once? y/n: ")
        path_type = "file"
        if batch_convert in batch_yes:
            path_type = "folder"
            batch_convert = True
        elif batch_convert in batch_no:
            path_type = "file"
            batch_convert = False
        else:
            print("--------------------\nPlease enter a valid option!\n--------------------")
            continue

        # Get the input and output paths from the user
        input_path = input(f"Please enter your full file path: ")
        output_path = input(f"Please enter your full output path: ")

        # Strip the quotes away from the user input, if there are any
        if (input_path.startswith("\"") or input_path.endswith("\"")) or \
           (output_path.startswith("\"") or output_path.endswith("\"")):
            input_path = input_path.replace("\"", "")
            output_path = output_path.replace("\"", "")

        # Check if the input path is a folder if batch_conversion is enabled or if it is a file
        if (batch_convert and not Path(input_path).is_dir()) or (not batch_convert and not Path(input_path).is_file()):
            print(
                f"--------------------\nInput path: {input_path} is not a valid {path_type} path!\nPlease enter a valid {path_type} path!\n--------------------")
            continue
        # Check if the output path is a folder if batch_conversion is enabled or has a parent directory and a file suffix
        elif (batch_convert and not Path(output_path).is_dir()) or (not batch_convert and not (Path(output_path).parent.is_dir() and Path(output_path).suffix)):
            print(
                f"--------------------\nOutput path: {output_path} is not a valid {path_type} path!\nPlease enter a valid {path_type} path!\n--------------------")
            continue

        # Start the decompression
        if batch_convert:
            print(f"--------------------\nBatch decompression starting")
            for file in Path(input_path).glob("*"):
                (Path(output_path) / file.name).with_suffix(file.suffix).write_bytes(decompress(Path(file).read_bytes()))
            print(f"Decompression finished!\n--------------------")

        else:
            print(f"--------------------\nDecompression starting")
            Path(output_path).write_bytes(decompress(Path(input_path).read_bytes()))
            print(f"Decompression finished!\n--------------------")

        break
