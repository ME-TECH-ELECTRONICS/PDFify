import os
import re
import sys
import pikepdf
import subprocess
import platform
import blessed
from time import sleep
from PIL import Image
from tqdm import tqdm
from colorama import Fore, Back, Style, init
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

init(autoreset=True)
output_folder = "output/"
input_folder = "input/"

error = False

def clear_console(name_print = True):
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    if name_print:
        print(Back.BLUE + "PDFify v1.0")
def check_folders():
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def rewrite_console_line(position=1):
    for i in range(term.get_location()[0] - position):
        sys.stdout.write("\033[F\033[K")

def shorten_filename(filename, max_length=12):
    name, ext = os.path.splitext(filename)
    if len(name) > max_length - len(ext) - 3:
        return name[:max_length - len(ext) - 3] + "..." + ext
    return filename

def docx_to_pdf(input_path, input_dir):
    output_pdf = os.path.join(input_dir, os.path.basename(input_path).replace(".docx", ".pdf"))
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", input_dir],stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return output_pdf

def ppt_to_pdf(input_path, output_dir):
    output_pdf = os.path.join(output_dir, os.path.basename(input_path).replace(".pptx", ".pdf"))
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", output_dir],stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return output_pdf

def image_to_pdf(input_path, output_dir):
    img = Image.open(input_path)
    output_pdf = os.path.join(output_dir, os.path.basename(input_path).rsplit('.', 1)[0] + ".pdf")
    img.convert('RGB').save(output_pdf)
    return output_pdf

def compress_pdf(input_pdf, output_dir):
    compressed_pdf = os.path.join(output_dir, "compressed_" + os.path.basename(input_pdf))
    with pikepdf.open(input_pdf) as pdf:
        pdf.save(compressed_pdf)
    return compressed_pdf

def compress_pdfs(input_dir, output_dir):
    if os.path.isdir(input_dir):
        pdfs = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        with tqdm(total=len(pdf_files), desc="Compressing PDFs") as progress_bar:
            for file in pdfs:
                compressed_pdf = os.path.join(output_dir, "compressed_" + os.path.basename(file))
                with pikepdf.open(file) as pdf:
                    pdf.save(compressed_pdf)
                    progress_bar.update(1)

def merge_pdfs(file_paths, output_path):
    merger = PdfMerger()
    with tqdm(total=len(file_paths), desc="Merging PDFs") as progress_bar:
        for path in file_paths:
            merger.append(os.path.join(input_folder,path))
            progress_bar.update(1)
        merger.write(output_path)
        merger.close()
        compress_pdf(output_path,output_folder)
        os.remove(output_path)

def split_pdf(input_path, start_page, end_page, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for j in range(start_page, end_page + 1):
        writer.add_page(reader.pages[j])
    with open(output_path, "wb") as f:
        writer.write(f)

def convert_and_compress_folder(folder_path, output_dir):
    files = os.listdir(folder_path)
    total_files = len(files)

    with tqdm(total=total_files, desc="Processing files") as main_bar:
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            name, ext = os.path.splitext(filename)
            short_name = shorten_filename(filename)
            if ext.lower() == '.docx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = docx_to_pdf(file_path, output_dir)
                    sub_bar.update(1)
                    compress_pdf(pdf_path, output_dir)
                    sub_bar.update(1)
                    os.remove(pdf_path)

            elif ext.lower() == '.pptx':
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = ppt_to_pdf(file_path, output_dir)
                    sub_bar.update(1)
                    compress_pdf(pdf_path, output_dir)
                    sub_bar.update(1)
                    os.remove(pdf_path)

            elif ext.lower() in ['.jpg', '.jpeg', '.png']:
                with tqdm(total=2, desc=f"Converting {short_name}", leave=False) as sub_bar:
                    pdf_path = image_to_pdf(file_path, output_dir)
                    sub_bar.update(1)
                    compress_pdf(pdf_path, output_dir)
                    sub_bar.update(1)
                    os.remove(pdf_path)

            else:
                print(f"Skipping unsupported file format: {filename}")

            main_bar.update(1)

##################
## Main Program ##
##################
if __name__ == "__main__":
    term = blessed.Terminal()
    try:
        check_folders()
        while True:
            clear_console()
            print(Fore.YELLOW + "1 - Convert all to pdf\n2 - Merge pdf\n3 - Compress pdf\n4 - Split pdf\nq - Quit")
            option = input("Choose an option to start: ")
            clear_console()
            if option == "1":
                convert_and_compress_folder(input_folder, output_folder)
            elif option == "2":
                while True:
                    clear_console()
                    pdf_files = [file for file in os.listdir(input_folder) if file.endswith(".pdf")]
                    i=1
                    for file in pdf_files:
                        print(f"{i}. {shorten_filename(file, 50)}")
                        i += 1
                    merge_all = input("Merge all pdf [y/N]: ").lower() or "n"
                    y1 = term.get_location()[0]
                    while True:
                        pattern = input("Order of pdf to merge comma seperated: ").strip()
                        if re.fullmatch(r"^\d+(,\d+)*$", pattern):
                            pattern = list(map(int, pattern.split(",")))
                            for i in range(len(pattern)):
                                if 0 <= pattern[i]-1 < len(pdf_files): error = False
                                else:
                                    print("Please enter the valid file number!")
                                    sleep(3)
                                    rewrite_console_line(y1)
                                    error = True
                                    break
                                
                            if not error:
                                break
                        else:
                            print("Invalid character. please input only number seperated by comma")
                            sleep(3)
                            rewrite_console_line(y1)
                    if not merge_all == "n":
                        sorted_merge_list = [pdf_files[i-1] for i in pattern]
                        remaining_indexes = [i for i in range(len(pdf_files)) if i not in pattern]
                        sorted_merge_list.extend([pdf_files[i-1] for i in remaining_indexes])
                        merge_pdfs(sorted_merge_list, os.path.join(output_folder, "merged_output.pdf"))
                        break
                    else:
                        sorted_merge_list = [pdf_files[i-1] for i in pattern]
                        merge_pdfs(sorted_merge_list, os.path.join(output_folder, "merged_output.pdf"))
                 
                    user_input = input("Do you want to merge any other files [y/N]: ").lower() or "n"
                    if user_input == "n":
                        break
                        
            elif option == "3":
                clear_console()
                pdf_files = [file for file in os.listdir(input_folder) if file.endswith(".pdf")]
                i=1
                for file in pdf_files:
                    print(f"{i}. {shorten_filename(file, 50)}")
                    i += 1
                compress_all = input("Compress all pdf [y/N]: ").lower() or "n"
                y1 = term.get_location()[0]
                if compress_all == "n":
                    while True:
                        compress_list = input("List of pdf to compress comma seperated: ").strip()
                        if re.fullmatch(r"^\d+(,\d+)*$", compress_list):
                           compress_list = list(map(int, compress_list.split(",")))
                           for i in range(len(compress_list)):
                               if 0 <= compress_list[i]-1 < len(pdf_files): error = False
                               else:
                                   print("Please enter the valid file number!")
                                   sleep(3)
                                   rewrite_console_line(y1)
                                   error = True
                                   break
                           if not error:
                               compress_pdf_list = [pdf_files[i-1] for i in compress_list]
                        else:
                           print("Invalid character. please input only number seperated by comma")
                           sleep(3)
                           rewrite_console_line(y1)
                else:
                    compress_pdfs(input_folder, output_folder)
                    break
            elif option == "4":
                split_pdf(input_folder + "NAUKRI_MELVIN_RIJOHN_T_(2).pdf", 0, 0, os.path.join(output_folder, "split_output.pdf"))
            elif option == "q":
                print(Fore.RED + "Quitting...")
                sleep(3)
                clear_console(False)
                exit()
            else:
                print("Invalid option. Try again.")

            sleep(2)
    except KeyboardInterrupt:
        clear_console()
        print(Fore.RED + Style.BRIGHT + "SIGINT detected. Quitting...")
        sleep(1)
        clear_console(False)