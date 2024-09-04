import os
import shutil

working_folder = r"R:\2023"
trash_folder = r"D:\temp"  # моя какая-нибудь

os.chdir(working_folder)


def list_files(filepath):
    paths = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            paths.append(os.path.join(root, file))
    return paths


file_list = list_files(working_folder)


def clean_small_files(f_list):
    files2clean = []
    for file in f_list:
        file_size = os.path.getsize(file) / 1024
        fn = file.split("\\")[-1]
        if file_size < 5120:
            print(trash_folder + "\\" + fn)
            shutil.move(file, trash_folder + "\\" + fn)
        else:
            continue


clean_small_files(file_list)
