'''
import re

pattern = r"^(\d+(-\d+)?)(,\s*\d+(-\d+)?)*$"
while True:
    v = input("input seq: ")

    if re.fullmatch(pattern, v):
        print("Match!")
    else:
        print("No match")
'''        
import re
import blessed
import os
import time

term = blessed.Terminal()
os.system("clear")
time.sleep(5)
with term.location(0, term.height):
    print("hello world!", term.height)


for i in range(7):
    with term.location(0,i):
        print("This is a test")
        
def parse_to_numbers(input_string):
    pattern = r'(\d+)(?:-(\d+))?'
    numbers = []
    matches = re.findall(pattern, input_string)
    for match in matches:
        start = int(match[0])
        end = int(match[1]) if match[1] else start
        numbers.extend(range(start, end + 1))
    return numbers

# Example usage
#input_string = input("input seq: ")
#result = parse_to_numbers(input_string)
#print(result)  # Output: [1, 2, 3, 7, 8, 9, 10]