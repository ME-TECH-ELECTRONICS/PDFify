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
        