import os
import re
import sys
import pikepdf
import subprocess
import platform
from time import sleep
from PIL import Image
from tqdm import tqdm
from colorama import Fore, Back, Style, init
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

init(autoreset=True)
output_folder = "output/"
input_folder = "input/"
pdfs_folder = "pdfs/"
os.makedirs(output_folder, exist_ok=True)

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        clear_console()

def check_folders():
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    if not os.path.exists(pdfs_folder):
        os.makedirs(pdfs_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def rewrite_console_line(position=1):
    for i in range(position):
        sys.stdout.write("\033[F\033[K")

def shorten_filename(filename, max_length=12):
    name, ext = os.path.splitext(filename)
    if len(name) > max_length - len(ext) - 3:
        return name[:max_length - len(ext) - 3] + "..." + ext
    return filename

def docx_to_pdf(input_path, output_folder):
    output_pdf = os.path.join(output_folder, os.path.basename(input_path).replace(".docx", ".pdf"))
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", output_folder],stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return output_pdf

def ppt_to_pdf(input_path, output_folder):
    output_pdf = os.path.join(output_folder, os.path.basename(input_path).replace(".pptx", ".pdf"))
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", output_folder],stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return output_pdf

def image_to_pdf(input_path, output_folder):
    img = Image.open(input_path)
    output_pdf = os.path.join(output_folder, os.path.basename(input_path).rsplit('.', 1)[0] + ".pdf")
    img.convert('RGB').save(output_pdf)
    return output_pdf

def compress_pdf(input_pdf, output_folder):
    compressed_pdf = os.path.join(output_folder, "compressed_" + os.path.basename(input_pdf))
    with pikepdf.open(input_pdf) as pdf:
        pdf.save(compressed_pdf)
    return compressed_pdf

def compress_pdfs(input_folder, output_folder):
    if os.path.isdir(file_paths):
        pdf_files = [os.path.join(file_paths, f) for f in os.listdir(file_paths) if f.lower().endswith('.pdf')]
    else:
        pdf_files = file_paths
    with tqdm(total=len(pdf_files), desc="Merging PDFs") as progress_bar:
        for path in pdf_files:
            compressed_pdf = os.path.join(output_folder, "compressed_" + os.path.basename(path))
            with pikepdf.open(input_pdf) as pdf:
                pdf.save(compressed_pdf)
                progress_bar.update(1)

'''def merge_pdfs(file_paths, output_path):
    merger = PdfMerger()
    for path in file_paths:
        merger.append(path)
    merger.write(output_path)
    merger.close()
'''
def merge_pdfs(file_paths, output_path):
    merger = PdfMerger()

    if os.path.isdir(file_paths):
        pdf_files = [os.path.join(file_paths, f) for f in os.listdir(file_paths) if f.lower().endswith('.pdf')]
        pdf_files.sort()
    else:
        pdf_files = file_paths
    with tqdm(total=len(pdf_files), desc="Merging PDFs") as progress_bar:
        for path in pdf_files:
            merger.append(path)
            progress_bar.update(1)

    merger.write(output_path)
    merger.close()

def split_pdf(input_path, start_page, end_page, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for i in range(start_page, end_page + 1):
        writer.add_page(reader.pages[i])
    with open(output_path, "wb") as f:
        writer.write(f)

def convert_and_compress_folder(folder_path, output_folder):
    files = os.listdir(folder_path)
    total_files = len(files)

    with tqdm(total=total_files, desc="Processing files") as main_bar:
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            name, ext = os.path.splitext(filename)
            short_name = shorten_filename(filename)
            if ext.lower() == '.docx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = docx_to_pdf(file_path, output_folder)
                    sub_bar.update(1)
                    compressed_pdf_path = compress_pdf(pdf_path, output_folder)
                    sub_bar.update(1)
                    os.remove(pdf_path)

            elif ext.lower() == '.pptx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = ppt_to_pdf(file_path, output_folder)
                    sub_bar.update(1)
                    compressed_pdf_path = compress_pdf(pdf_path, output_folder)
                    sub_bar.update(1)
                    os.remove(pdf_path)

            elif ext.lower() in ['.jpg', '.jpeg', '.png']:
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = image_to_pdf(file_path, output_folder)
                    sub_bar.update(1)
                    compressed_pdf_path = compress_pdf(pdf_path, output_folder)
                    sub_bar.update(1)
                    os.remove(pdf_path)

            else:
                print(f"Skipping unsupported file format: {filename}")

            main_bar.update(1)

##################
## Main Program ##
##################
if __name__ == "__main__":
    try:
        check_folders()
        while True:
            clear_console()
            print(Back.BLUE + "PDFify v1.0")
            print(Fore.YELLOW + "1 - Convert all to pdf\n2 - Merge pdf\n3 - Compress pdf\nq - Quit")
            option = input("Choose an option to start: ")
            clear_console()
            if option == "1":
                convert_and_compress_folder(input_folder, output_folder)
            elif option == "2":
                while True:
                    pdf_files = [file for file in os.listdir(pdfs_folder) if file.endswith(".pdf")]
                    i=1
                    print(Back.BLUE + "PDFify v1.0")
                    for file in pdf_files:
                        print(f"{i}. {shorten_filename(file, 50)}")
                        i += 1
                    merge_all = input("Merge all pdf [y/N]: ").lower()
                    if merge_all == "": merge_all = "n"
                    while True:

                        pattern = input("Order of pdf to merge comma seperated: ").strip()
                        if re.fullmatch(r"^\d+(,\d+)*$", pattern):
                            break
                        else:
                            print("Invalid character. please input only number seperated by comma")
                            sleep(3)
                            rewrite_console_line(2)
                    if not merge_all == "n":
                        break
                #merge_pdfs(pdfs_folder, os.path.join(output_folder, "merged_output.pdf"))
            elif option == "3":
                compress_pdfs(pdfs_folder, output_folder)
            elif option == "q":
                print(Fore.RED + "Quitting...")
                sleep(3)
                clear_console()
                exit()
            else:
                print("Invalid option. Try again.")

            sleep(2)
    except KeyboardInterrupt:
        clear_console()
        print(Fore.RED + Style.BRIGHT + "SIGINT detected. Quitting...")
        sleep(1)
        clear_console()


'''
pdfs_to_merge = ["/path/to/file1.pdf", "/path/to/file2.pdf"]


split_pdf("/path/to/file.pdf", 0, 2, os.path.join(output_folder, "split_output.pdf"))
'''