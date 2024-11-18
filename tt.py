def user_interactor(action, msg, )
while True:
    clear_console()
    pdf_files = [file for file in os.listdir(input_folder) if file.endswith(".pdf")]
    i = 1
    for file in pdf_files:
        print(f"{i}. {shorten_filename(file, 50)}")
        i += 1
    merge_all = input("Merge all pdf [y/N]: ").lower() or "n"
    y1 = term.get_location()[0]
    while True:
        if msg == "M":
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