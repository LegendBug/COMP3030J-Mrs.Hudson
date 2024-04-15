#!/bin/bash

# This shell script is used to delete ALL migration files in the project.
# After running the script, you will lose all migration history.
# By Sichen Li.

# Find all migration directories
files_to_delete=$(find . -path "*/migrations/*.py" -not -name "__init__.py")
pyc_files_to_delete=$(find . -path "*/migrations/*.pyc")

# Print out the files that is going to be deleted
echo "The following .py files will be deleted:"
echo "$files_to_delete"
echo "-----------------------------------------"
echo "The following .pyc files will be deleted:"
echo "$pyc_files_to_delete"

# Ask for confirmation
read -p "Are you **really** sure you want to delete these files? (y/N)" confirm
if [[ $confirm == [yY] || $confirm ==[yY][eE][sS] ]]
then
    echo "-----------------------------------------"
    echo "Deleting files..."
    rm "$files_to_delete"
    rm "$pyc_files_to_delete"
    echo "Done. Wish you have a fresh restart!"
else
    echo "Aborted."
fi