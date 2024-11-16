import sys
from time import sleep
# Function to clear the current line and overwrite it
def clear_and_print_line(text):
    # Move cursor up one line, clear the line, and print new text
    sys.stdout.write("\033[F\033[K" + text + "\n")
    sys.stdout.flush()

# Simulate the process
print("Order of pdf to merge comma separated: 1,2,3, ")
sleep(2)
# Replace the first line with an error message
clear_and_print_line("Invalid character. Please input only numbers separated by commas.")
