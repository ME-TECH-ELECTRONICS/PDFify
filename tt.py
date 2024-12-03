import os
import re
import sys
from typing import Callable

import pikepdf
import platform
import subprocess
from PIL import Image
from tqdm import tqdm
from time import sleep
from blessed import Terminal
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

term = Terminal()
OUTPUT_FOLDER = "output/"
INPUT_FOLDER = "input/"
MENUS = ["Convert to PDF", "Merge PDF", "Compress PDF", "Split PDF"]

class BreakLoop(Exception):
    pass

def check_app_install():
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
    valid_indices = [index for index in arr2 if 0 <= index < len(arr1)]
    return [arr1[index] for index in valid_indices]
    
    
def parse_to_numbers(input_string: str) -> list[int]:
    numbers = []
    matches = re.findall(r'(\d+)(?:-(\d+))?', input_string)
    for match in matches:
        start = int(match[0]) - 1
        end = int(match[1]) - 1 if match[1] else start
        numbers.extend(range(start, end + 1))
    return numbers


def clear_console() -> None:
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def check_folders() -> None:
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)


def rewrite_console_line(position: int) -> None:
    """
    Moves the cursor up by `position` lines and clears those lines.

    :param position: The number of lines to move up from the current position.
    """
    if os.name == "nt":  # Windows
        for _ in range(position):
            sys.stdout.write("\033[F")  # Move up
            sys.stdout.write("\033[K")  # Clear line
    else:  # Linux/Unix
        for _ in range(position):
            sys.stdout.write("\033[F")  # Move up
            sys.stdout.write("\033[K")  # Clear line
    sys.stdout.flush()


def shorten_filename(filename: str, max_length: int = 12) -> str:
    name, ext = os.path.splitext(filename)
    if len(name) > max_length - len(ext) - 3:
        return name[:max_length - len(ext) - 3] + "..." + ext
    return filename


def user_input_yn(prompt: str = "", default: str = "n") -> str:
    return input(prompt).strip().lower() or default


def user_input_option(prompt: str = "", default: int = 1) -> int:
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
    if default is None:
        default = [1]
    user_input = input(prompt).strip()
    if user_input == "b":
        raise BreakLoop
    arr = parse_to_numbers(user_input)
    return filter_valid_indices(arr, default)


def list_files(file_type: list[str]) -> list[str]:
    return [file for file in os.listdir(INPUT_FOLDER) if file.endswith(tuple(file_type))]


def docx_to_pdf(input_path: str, input_dir: str) -> str:
    output_pdf = os.path.join(input_dir, os.path.basename(input_path).replace(".docx", ".pdf"))
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", input_dir],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return output_pdf


def ppt_to_pdf(input_path: str, output_dir: str) -> str:
    output_pdf = os.path.join(output_dir, os.path.basename(input_path).replace(".pptx", ".pdf"))
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", output_dir],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return output_pdf


def image_to_pdf(input_path: str) -> str:
    img = Image.open(input_path)
    output_pdf = os.path.join(OUTPUT_FOLDER, os.path.basename(input_path).rsplit('.', 1)[0] + ".pdf")
    img.convert('RGB').save(output_pdf)
    return output_pdf


def compress_pdf(input_pdf: str) -> str:
    compressed_pdf = os.path.join(OUTPUT_FOLDER, "compressed_" + os.path.basename(input_pdf))
    with pikepdf.open(input_pdf) as pdf:
        pdf.save(compressed_pdf)
    return compressed_pdf


def compress_pdfs(input_pdf: list[str]) -> None:
    with tqdm(total=len(input_pdf), desc="Compressing PDFs") as progress_bar:
        for file in input_pdf:
            compressed_pdf = os.path.join(OUTPUT_FOLDER, "compressed_" + os.path.basename(file))
            with pikepdf.open(INPUT_FOLDER + file) as pdf:
                pdf.save(compressed_pdf)
                progress_bar.update(1)


def merge_pdfs(file_paths: list[str]) -> None:
    """
    Merge multiple PDFs into a single PDF

    Args:
    :param file_paths:
    :return:

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


def split_pdf(input_path: str, start_page: int, end_page: int, output_path: str) -> None:
    """
    Split a PDF into multiple PDFs

    Args:
    :param input_path: input path
    :param start_page:
    :param end_page:
    :param output_path:
    :return:
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for j in range(start_page, end_page + 1):
        writer.add_page(reader.pages[j])
    with open(output_path, "wb") as f:
        writer.write(f)


def convert_and_compress_files(input_files: list[str]) -> None:
    """
    Convert and compress files

    Args:
        input_files (list[str]): List of file names

    """
    total_files = len(input_files)

    with tqdm(total=total_files, desc="Processing files") as main_bar:
        for filename in input_files:
            file_path = os.path.join(INPUT_FOLDER, filename)
            name, ext = os.path.splitext(filename)
            short_name = shorten_filename(filename)
            if ext.lower() == '.docx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = docx_to_pdf(file_path, OUTPUT_FOLDER)
                    sub_bar.update(1)
                    compress_pdf(pdf_path)
                    sub_bar.update(1)
                    os.remove(pdf_path)
            elif ext.lower() == '.pptx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = ppt_to_pdf(file_path, OUTPUT_FOLDER)
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


def process_operation(menu_title: str, file_types: list[str], action: Callable, min_files: int = 1, error_message: str = "Enter at least one file to process"):
    """
    General function to process operations for a menu.

    :param menu_title: Title to display for the current operation.
    :param file_types: List of file extensions to filter.
    :param action: Function to execute on selected files.
    :param min_files: Minimum number of files required for the operation.
    :param error_message: Message to display when user input is invalid.
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
    except BreakLoop:
        pass

if __name__ == "__main__":
    try:
        while True:
            clear_console()
            print_title()
            print_menu([])  # Pass the menu options
            op = user_input_option("Choose an option to start: ")

            if op == 1:
                process_operation(
                    menu_title=MENUS[0],
                    file_types=["png", "jpeg", "jpg", "docx", "ppt"],
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
                print(term.RED + "Quitting...")
                sleep(3)
                clear_console()
                exit()
    except KeyboardInterrupt:
        print(term.RED + "Quitting...")
        sleep(3)
        clear_console()
        exit()