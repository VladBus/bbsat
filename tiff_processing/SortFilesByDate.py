import os
import shutil
from datetime import datetime, timedelta

# Set base folders with data to work with
base_folder = "S:\\GeoTif"
TERRA_folder = "S:\\Products\\TERRA"
NOAA_folder = "S:\\Products\\NOAA"
METOP_folder = "S:\\Products\\METOP"

# Set the current date
now_time = datetime.today()
now_date = now_time.date()
print(f"Today is {now_date}")


# Function for checking if folder exists, anyway the folder is created
def FolderExistChecker(path_folder):
    if os.path.exists(path_folder):
        pass
    else:
        os.makedirs(path_folder)
        print(path_folder, " folder has been created")


# Function for creating folders
def FileMover(source_folder, flist2move, dest_folder):
    for f in flist2move:
        copy_from = source_folder + "\\" + f
        copy_to = dest_folder + "\\" + f
        shutil.move(copy_from, copy_to)


# Function for creation of names for date subfolders
def SetYearMonthDayFolder(initial_date):
    Year = initial_date.__format__("%Y")
    Month = initial_date.__format__("%m")
    Date = initial_date.__format__("%d-%m-%Y")
    return Year, Month, Date


# Main function for
def FilterFiles2Move(sat_folder, ini_date, sat_name, base_dest_folder):
    sat_flist = os.listdir(sat_folder)  # Create a list of files in the source folder
    while (
            len(sat_flist) != 0
    ):  # We will perform the commands until there are no files in the list
        filtered_list = []  # Set the empty list for adding there filtered files
        date_mask = ini_date.__format__("%Y%m%d")  # Set the mask for filtering
        for file in sat_flist:
            if date_mask in file:
                filtered_list.append(
                    file
                )  # We search all files that match with the mask
        if (
                len(filtered_list) != 0
        ):  # If there are some files in the list, matched with the mask, we perform all commands, given below
            Year_now, Month_now, Day_now = SetYearMonthDayFolder(
                ini_date
            )  # Set the name of subfolders for moving there files
            DateFolder4move = (
                    base_dest_folder
                    + "\\"
                    + Year_now
                    + "\\"
                    + Month_now
                    + "\\"
                    + Day_now
                    + "\\"
                    + sat_name
            )  # Create a path for moving there filtered files
            FolderExistChecker(
                DateFolder4move
            )  # Check the existance of folders and subfolders
            FileMover(sat_folder, filtered_list, DateFolder4move)  # Move files
            sat_flist = list(
                set(sat_flist) - set(filtered_list)
            )  # Exclude all files that were moved from the initial list
            ini_date = ini_date - timedelta(days=1)  # Change the date (go down)
            print(
                f"{len(filtered_list)} files were moved to the folder {DateFolder4move}"
            )
        else:
            print(
                f"No files for the date {ini_date}"
            )  # If the filtered list has 0 values...
            ini_date = ini_date - timedelta(days=1)  # we change the date (do down)


FilterFiles2Move(METOP_folder, now_date, "METOP", base_folder)
FilterFiles2Move(NOAA_folder, now_date, "NOAA", base_folder)
FilterFiles2Move(TERRA_folder, now_date, "TERRA", base_folder)
