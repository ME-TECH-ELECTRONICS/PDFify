#!/usr/bin/env python

#imports
import os
import re
import sys
from typing import Callable
import pikepdf
import subprocess
from PIL import Image
from tqdm import tqdm
from time import sleep
from blessed import Terminal
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

#Constants
term = Terminal()
OUTPUT_FOLDER = "output/"
INPUT_FOLDER = "input/"
MENUS = ["Convert to PDF", "Merge PDF", "Compress PDF", "Split PDF"]


class BreakLoop(Exception):
    """
    Custom exception to break out of a loop.
    """
    pass


def check_app_install():
    """
   Checks if LibreOffice is installed and accessible via the terminal.

   :return: True if LibreOffice is installed and accessible, False otherwise.
   """
    try:
        subprocess.run(
            ["libreoffice", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except FileNotFoundError:
        return False


def filter_valid_indices(arr1: list[int], arr2: list[int]) -> list[int]:
    """
   Filters valid indices from `arr2` based on the bounds of `arr1`.

   :param arr1: The original array.
   :param arr2: The array of indices to filter.
   :return: A list of valid indices from `arr2` within the bounds of `arr1`.
   """
    return [arr1[index] for index in arr2 if 0 <= index < len(arr1)]


def parse_to_numbers(input_string: str) -> list[int]:
    """
   Parses a string into a list of numbers or ranges.

   :param input_string: The input string to parse.
   :return: A list of integers representing the parsed numbers or ranges.
   """
    numbers = []
    matches = re.findall(r'(\d+)(?:-(\d+))?', input_string)
    for match in matches:
        start = int(match[0]) - 1
        end = int(match[1]) - 1 if match[1] else start
        numbers.extend(range(start, end + 1))
    return numbers


def clear_console() -> None:
    """
    Clears the console for better UI experience.
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def check_folders() -> None:
    """
    Ensures the input and output folders exist, creating them if necessary.
    """
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def rewrite_console_line(position: int) -> None:
    """
    Overwrites the last `position` lines in the console.

    :param position: Number of lines to overwrite
    """
    for b in range(term.get_location()[0] - position):
        sys.stdout.write("\033[F\033[K")


def shorten_filename(filename: str, max_length: int = 12) -> str:
    """
    Shortens filenames to fit within a maximum length, adding ellipses if necessary.

    :param filename: The original filename
    :param max_length: The maximum length of the shortened filename
    :return: The shortened filename
    """
    name, ext = os.path.splitext(filename)
    if len(name) > max_length - len(ext) - 3:
        return name[:max_length - len(ext) - 3] + "..." + ext
    return filename


def user_input_option(prompt: str = "", default: int = 1) -> int:
    """
    Gets a numerical user input with a default value.

    :param prompt: Shows the prompt
    :param default: Default value
    :return: integer option
    """
    try:
        return int(input(prompt).strip() or default)
    except ValueError:
        return default


def print_title(action: str = "") -> None:
    print(term.white_on_blue(f"PDFify v1.0 | {action.upper()}"))


def print_menu(disabled: list[int]) -> None:
    for i, menu in enumerate(MENUS, start=1):
        if i not in disabled:
            print(term.gold(f"{i}. {menu}"))
        else:
            print(term.gray45(f"{i}. {menu}"))
    print(term.red("0. Exit"))


def user_input_range(prompt: str = "", default: list[int] = None) -> list[int]:
    """
    Gets a range of numerical user input.

    :param prompt: Shows the prompt
    :param default: Default value
    :return: list of numbers
    """
    if default is None:
        default = [1]
    user_input = input(prompt).strip()
    if user_input == "b":
        raise BreakLoop
    arr = parse_to_numbers(user_input)
    return filter_valid_indices(arr, default)


def list_files(file_types: list[str]) -> list[str]:
    """
    Lists files in the input folder matching given extensions.

    :param file_types: list of file extensions
    :return: list of files
    """
    return [file for file in os.listdir(INPUT_FOLDER) if file.endswith(tuple(file_types))]


def docx_to_pdf(input_path: str) -> str:
    """
    Converts a DOCX file to PDF using LibreOffice.

    :param input_path: path to the input docx
    :return: path to the converted PDF
    """
    output_pdf = os.path.join(INPUT_FOLDER, os.path.basename(input_path).replace(".docx", ".pdf"))
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", OUTPUT_FOLDER],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return output_pdf


def ppt_to_pdf(input_path: str) -> str:
    """
    Converts a PPTX file to PDF using LibreOffice.
    :param input_path: path to the input pptx
    :return: path to the converted PDF
    """
    output_pdf = os.path.join(OUTPUT_FOLDER, os.path.basename(input_path).replace(".pptx", ".pdf"))
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", OUTPUT_FOLDER],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return output_pdf


def image_to_pdf(input_path: str) -> str:
    """
    Converts an image file to PDF.

    :param input_path: path to the input image
    :return: path to the converted PDF
    """
    img = Image.open(input_path)
    output_pdf = os.path.join(OUTPUT_FOLDER, os.path.basename(input_path).rsplit('.', 1)[0] + ".pdf")
    img.convert('RGB').save(output_pdf)
    return output_pdf


def compress_pdf(input_pdf: str) -> str:
    """
    Compresses a PDF using `pikepdf`.

    :param input_pdf: List of paths to the input PDFs.

    :return: Path to the compressed PDF.
    """
    compressed_pdf = os.path.join(OUTPUT_FOLDER, "compressed_" + os.path.basename(input_pdf))
    with pikepdf.open(input_pdf) as pdf:
        pdf.save(compressed_pdf)
    return compressed_pdf
            
            
def compress_pdfs(input_pdfs: list[str]) -> str:
    """
    Compresses a PDFs using `pikepdf`.

    :param input_pdfs: List of paths to the input PDFs.

    """
    with tqdm(total=len(input_pdfs), desc="Compressing PDFs") as progress_bar:
        for file in input_pdfs:
            compressed_pdf = os.path.join(OUTPUT_FOLDER, "compressed_" + os.path.basename(file))
            with pikepdf.open(INPUT_FOLDER + file) as pdf:
                pdf.save(compressed_pdf)
                progress_bar.update(1)
            


def merge_pdfs(file_paths: list[str]) -> None:
    """
    Merges multiple PDFs into a single file.

    :param file_paths: List of paths to the input PDFs.
    """
    merger = PdfMerger()
    output_path = os.path.join(OUTPUT_FOLDER, "merged_output.pdf")
    with tqdm(total=len(file_paths), desc="Merging PDFs") as progress_bar:
        for path in file_paths:
            merger.append(os.path.join(INPUT_FOLDER, path))
            progress_bar.update(1)
        merger.write(output_path)
        merger.close()
        compress_pdf(output_path)
        os.remove(output_path)


"""def split_pdf(input_path: str, start_page: int, end_page: int, output_path: str) -> None:
    """"""
    Split a PDF into multiple PDFs

    :param input_path: Path to the input PDF
    :param start_page: Start page number
    :param end_page: End page number
    :param output_path: Path to the output PDF
    """"""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for j in range(start_page, end_page + 1):
        writer.add_page(reader.pages[j])
    with open(output_path, "wb") as f:
        writer.write(f)
"""

def split_pdf(selected_files: list[str]) -> None:
    """
    Handles the splitting of PDFs based on user input.
    
    :param selected_files: List of selected PDF files to split.
    """
    for file in selected_files:
        input_path = os.path.join(INPUT_FOLDER, file)
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        print(f"\nSelected file: {file}")
        print(f"Total pages: {total_pages}")
        print("1. Split by range (e.g., 1-3)")
        print("2. Split pages into separate PDFs")
        print("3. Split by a number of pages per file")
        
        split_option = user_input_option("Choose a split option: ", default=1)

        if split_option == 1:  # Split by range
            page_range = user_input_range(
                "Enter page range(s) to split [e.g., 1-3,5]: ",
                [i + 1 for i in range(total_pages)]
            )
            for i, page in enumerate(page_range, start=1):
                output_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(file)[0]}_split_{i}.pdf")
                split_pdf(input_path, page, page, output_path)
                print(f"Split page {page + 1} into {output_path}")

        elif split_option == 2:  # Split pages into separate PDFs
            for page in range(total_pages):
                output_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(file)[0]}_page_{page + 1}.pdf")
                split_pdf(input_path, page, page, output_path)
                print(f"Split page {page + 1} into {output_path}")

        elif split_option == 3:  # Split by a number of pages per file
            pages_per_file = user_input_option("Enter the number of pages per file: ", default=1)
            for i in range(0, total_pages, pages_per_file):
                start_page = i
                end_page = min(i + pages_per_file - 1, total_pages - 1)
                output_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(file)[0]}_split_{i // pages_per_file + 1}.pdf")
                split_pdf(input_path, start_page, end_page, output_path)
                print(f"Split pages {start_page + 1}-{end_page + 1} into {output_path}")

        else:
            print("Invalid split option selected. Skipping file.")
        sleep(1)


def convert_and_compress_files(input_files: list[str]) -> None:
    """
    Convert and compress files

    :param input_files: List of files to convert
    """
    total_files = len(input_files)

    with tqdm(total=total_files, desc="Processing files") as main_bar:
        for filename in input_files:
            file_path = os.path.join(INPUT_FOLDER, filename)
            name, ext = os.path.splitext(filename)
            short_name = shorten_filename(filename)
            if ext.lower() == '.docx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = docx_to_pdf(file_path)
                    sub_bar.update(1)
                    compress_pdf(pdf_path)
                    sub_bar.update(1)
                    os.remove(pdf_path)
            elif ext.lower() == '.pptx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = ppt_to_pdf(file_path)
                    sub_bar.update(1)
                    compress_pdf(pdf_path)
                    sub_bar.update(1)
                    os.remove(pdf_path)
            elif ext.lower() in ['.jpg', '.jpeg', '.png']:
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = image_to_pdf(file_path)
                    sub_bar.update(1)
                    compress_pdf(pdf_path)
                    sub_bar.update(1)
                    os.remove(pdf_path)
            else:
                print(f"Skipping unsupported file format: {filename}")
            main_bar.update(1)


def process_operation(menu_title: str, file_types: list[str], action: Callable, min_files: int = 1,
                      error_message: str = "Enter at least one file to process"):
    """
    General function to process operations for a menu.

    :param menu_title: Menu title to display
    :param file_types: List of file extensions to filter
    :param action: Function to execute on selected files
    :param min_files: Minimum number of files required for the operation
    :param error_message: Error message to display if no files are selected
    """
    clear_console()
    print_title(menu_title.upper())
    raw_files = list_files(file_types)
    if not raw_files:
        print(f"No {', '.join(file_types)} files found")
        sleep(3)
        return
    for i, file in enumerate(raw_files, start=1):
        print(f"{i}. {shorten_filename(file, 50)}")
    if menu_title.lower() == "split pdf":
        while True:
            
    line = term.get_location()[0]
    
    try:
        while True:

            input_range = user_input_range(
                f"Enter file number(s) to process [e.g., 1,3-5]: ",
                [i for i in range(len(raw_files))]
            )
            if input_range:
                selected_files = [raw_files[i] for i in input_range if 0 <= i < len(raw_files)]
                if len(selected_files) >= min_files:
                    action(selected_files)
                else:
                    print(error_message)
                    sleep(3)
                    rewrite_console_line(line)
            else:
                print("No files selected.")
                sleep(3)
                rewrite_console_line(line)
    except BreakLoop:
        pass


if __name__ == "__main__":
    try:
        if not check_app_install():
            print("Libra Office is not installed")
            # sys.exit(0)
        check_folders()
        while True:
            clear_console()
            print_title()
            print_menu([])  # Pass the menu options
            op = user_input_option("Choose an option to start: ")

            if op == 1:
                process_operation(
                    menu_title=MENUS[0],
                    file_types=["png", "jpeg", "jpg", "docx", "doc", "ppt", "pptx"],
                    action=convert_and_compress_files,
                    error_message="Enter at least one file to convert"
                )
            elif op == 2:
                process_operation(
                    menu_title=MENUS[1],
                    file_types=["pdf"],
                    action=merge_pdfs,
                    min_files=2,
                    error_message="Enter at least two PDFs to merge"
                )
            elif op == 3:
                process_operation(
                    menu_title=MENUS[2],
                    file_types=["pdf"],
                    action=compress_pdfs,
                    error_message="Enter at least one PDF to compress"
                )
            elif op == 4:
                process_operation(
                    menu_title=MENUS[3],
                    file_types=["pdf"],
                    action=split_pdf,
                    error_message="Enter at least one page to split"
                )
            elif op == 0:
                clear_console()
                print(term.red("User interrupted. Quitting..."))
                sleep(3)
                exit()
    except KeyboardInterrupt:
        clear_console()
        print(term.red("SIGINT received. Quitting..."))
        sleep(3)
        exit()
