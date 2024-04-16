import os
import shutil
from glob import glob

def find_files(base, pattern):
    """Return list of files matching pattern in base directory and its subdirectories."""
    return [y for x in os.walk(base) for y in glob(os.path.join(x[0], pattern)) if '__init__.py' not in y]

def delete_files(files):
    """Delete files from the filesystem."""
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted {file}")
        except OSError as e:
            print(f"Error deleting {file}: {e}")


if __name__ == '__main__':
    # Find all .py migration files except __init__.py
    files_to_delete = find_files('.', '*/migrations/*.py')

    # Find all .pyc migration files
    pyc_files_to_delete = find_files('.', '*/migrations/*.pyc')
    pyc_files_to_delete_2 = find_files('.', '*/__pycache__/*.pyc')

    # Display files to be deleted
    print("The following .py files will be deleted:")
    print('\n'.join(files_to_delete))
    print("-----------------------------------------")
    print("The following .pyc files will be deleted:")
    print('\n'.join(pyc_files_to_delete))
    print('\n'.join(pyc_files_to_delete_2))

    # Ask for user confirmation
    confirm = input("Are you **really** sure you want to delete these files? (y/N) ")
    if confirm.lower() == 'y':
        print("-----------------------------------------")
        print("Deleting files...")
        delete_files(files_to_delete)
        delete_files(pyc_files_to_delete)
        delete_files(pyc_files_to_delete_2)
        print("Done. Wish you have a fresh restart!")
    else:
        print("Aborted.")
