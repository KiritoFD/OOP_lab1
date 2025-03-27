import os

def check_file_exists(filepath):
    exists = os.path.exists(filepath)
    print(f"Checking {filepath}: {'EXISTS' if exists else 'MISSING'}")
    return exists

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    paths_to_check = [
        "src/application/command_parser.py",
        "src/core/html_model.py",
        "src/commands/base.py",
        "src/commands/io_commands.py",
        "src/commands/edit/add_element_command.py",
        "src/commands/edit/delete_element_command.py",
        "src/commands/edit/edit_text_command.py",
        "src/core/exceptions.py"
    ]
    
    missing = 0
    for path in paths_to_check:
        full_path = os.path.join(base_dir, path)
        if not check_file_exists(full_path):
            missing += 1
    
    if missing:
        print(f"\n{missing} files are missing. Please check your project structure.")
        print("Make sure you have the correct directory structure or adjust your imports accordingly.")
    else:
        print("\nAll required files exist!")

if __name__ == "__main__":
    main()
