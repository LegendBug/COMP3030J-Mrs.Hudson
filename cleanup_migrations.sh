# This shell script is used to delete ALL migration files in the project.
# After running the script, you will lose all your migration history.
# By Sichen Li.

# Find all migration directories
files_to_delete=$(find . -path "*/migrations/*.py" -not -name "__init__.py")
pyc_files_to_delete=$(find . -path "*/migrations/*.pyc")
pyc_files_to_delete_2=$(find . -path "*/__pycache__/*.pyc")

# Print out the files that are going to be deleted
echo "The following .py files will be deleted:"
echo "$files_to_delete"
echo "-----------------------------------------"
echo "The following .pyc files will be deleted:"
echo "$pyc_files_to_delete"
echo "$pyc_files_to_delete_2"

# Ask for confirmation
read -p "Are you **really** sure you want to delete these files? (y/N) " confirm
if [[ "$confirm" == [yY] ]]
then
    echo "-----------------------------------------"
    echo "Deleting files..."
    echo "$files_to_delete" | xargs rm
    echo "$pyc_files_to_delete" | xargs rm
    echo "$pyc_files_to_delete_2" | xargs rm
    echo "Done. Wish you have a fresh restart!"
else
    echo "Aborted."
fi