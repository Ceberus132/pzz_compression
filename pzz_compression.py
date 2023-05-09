__version__ = "0.1"
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
    while True:
        # Get the input and output paths from the user
        input_path = input(f"Please enter your full file path: ")
        output_path = input(f"Please enter your full output path: ")

        # Strip the quotes away from the user input, if there are any
        if (input_path.startswith("\"") or input_path.endswith("\"")) or \
           (output_path.startswith("\"") or output_path.endswith("\"")):
            input_path = input_path.replace("\"", "")
            output_path = output_path.replace("\"", "")

        # Check if the input path is a file and if the output path has a parent directory and a file suffix
        if (not Path(input_path).is_file()) or not (Path(output_path).parent.is_dir() and Path(output_path).suffix):
            print(f"--------------------\nInput path: {input_path} or \nOutput path: {output_path} are not a valid file path!\nPlease enter a valid file path!\n--------------------")
            continue

        # Start the decompression
        print(f"--------------------\nDecompression started!")
        Path(output_path).write_bytes(decompress(Path(input_path).read_bytes()))
        print(f"Decompression finished!\n--------------------")

        break
