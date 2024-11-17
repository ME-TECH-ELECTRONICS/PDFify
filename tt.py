# Array of names
names = ["Alice", "Bob", "Charlie", "David", "Eve"]

# User input for indexes, e.g., "3,0,4"
user_input = "1,3,4,2"#input("Enter the array indexes to sort by (comma-separated): ")

try:
    # Convert user input to a list of integers
    indexes = [int(index.strip()) for index in user_input.split(",")]

    # Validate that all indexes are within range
    if any(i < 0 or i >= len(names) for i in indexes):
        print("Invalid index. Please provide valid indexes within the array range.")
    else:
        # Sort names based on the given indexes
        sorted_names = [names[i] for i in indexes]

        # Handle remaining elements not specified by the user
        remaining_indexes = [i for i in range(len(names)) if i not in indexes]
        sorted_names.extend([names[i] for i in remaining_indexes])

        print("Sorted names:", sorted_names)
except ValueError:
    print("Invalid input. Please enter only integers separated by commas.")