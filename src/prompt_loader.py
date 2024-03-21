import os

def load_prompt(filename):
    """
    Loads the content of a given prompt file.

    :param filename: The name of the file to load.
    :return: The content of the file as a string.
    """
    # Define the base directory where prompt files are stored
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
    
    # Construct the full path to the file
    file_path = os.path.join(base_dir, filename)
    
    # Load and return the content of the file
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None