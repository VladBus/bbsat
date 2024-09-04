# _*_ coding: utf-8 _*_

import os

# import gdal
# import glob
# import shutil
# from contextlib import suppress

Products_bbsat = r"S:\GeoTif"
trash_folder = r"S:\trash"
os.chdir(Products_bbsat)

# file_list = glob.glob('*.geotiff.tif')

command = "gdal_translate -of Gtiff -co COMPRESS=LZW {input} {output}"


def list_files(filepath):
    paths = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if file.endswith(".geotiff.tif"):
                paths.append(os.path.join(root, file))
    return paths


def compressor(file_ini):
    output_file = file_ini.split(".")[0] + ".tif"
    os.system(command.format(input=file_ini, output=output_file))
    return output_file


def tif_size(tif_file):
    file_size = os.path.getsize(tif_file) / 1024
    return file_size


def file_filter(ini_file, compressed_file):
    big_tif = tif_size(ini_file)
    small_tif = tif_size(compressed_file)
    if small_tif <= big_tif * 0.2:
        print(
            "File size %s is too small, so it  can be deleted: \n Size: %d"
            % (compressed_file, small_tif)
        )
        # shutil.move(compressed_file, trash_folder + '\\' + compressed_file.split('\\')[-1])
        os.remove(compressed_file)
    else:
        print("File size for %s: \n %d" % (compressed_file, small_tif))


f_list = list_files(Products_bbsat)

if __name__ == "__main__":
    for file in f_list:
        try:
            light_file = compressor(file)
            file_filter(file, light_file)
            # shutil.move(file, trash_folder + '\\' + file.split('\\')[-1])
        except FileNotFoundError:
            pass
        finally:
            os.remove(file)
            print("File %s is moved to trash" % file)

# --Это для проверки работы Gdal--
# file1 = r'D:\GeoTif\2024\07\18-07-2024\METOP\Bar-Nord_METOP-C_20240718_130859_29558_CH_1_2_4.geotiff.tif'
#
# file2 = r"D:\GeoTif\2024\07\18-07-2024\METOP\Bar-Nord_METOP-C_20240718_130859_29558_CH_1_2_4.tif"
#
# os.system(f"gdal_translate.exe -of Gtiff -co COMPRESS=LZW {file1} {file2}")
