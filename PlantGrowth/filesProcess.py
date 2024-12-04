import os
import re


def date_processing(year, month, day, a = 0):
    num_year = int(year)
    num_month = int(month)
    num_day = int(day)
    if (num_month in [1, 3, 5, 7, 8, 10, 12] and num_day + a > 31)\
            or (num_month in [4, 6, 9, 11] and num_day + a > 30)\
            or ((num_year % 4 == 0 or num_day % 400 == 0) and num_month == 2 and num_day + a > 29)\
            or ((num_year % 4 != 0 and num_day % 400 != 0) and num_month == 2 and num_day + a > 28):
        num_month += 1
        if num_month == 13:
            num_month = 1
            num_day = 1
    else:
         num_day += a

    return f"{num_year:04d}_{num_month:02d}_{num_day:02d}"


def rename_files_by_pattern(folder_path, pattern):
    new_name_prefix = ""
    files = os.listdir(folder_path)
    for file_name in files:
        match = re.match(pattern, file_name)
        a = 0
        if match:
            new_file_name = new_name_prefix + date_processing(match.group(1), match.group(2), match.group(3)) + os.path.splitext(file_name)[1]
            old_file_path = os.path.join(folder_path, file_name)
            while True:
                try :
                    new_file_path = os.path.join(folder_path, new_file_name)
                    os.rename(old_file_path, new_file_path)
                    print(f"{old_file_path} 重命名为 {new_file_path}")
                    break
                except FileExistsError:
                    a += 1
                    new_file_name = new_name_prefix + date_processing(match.group(1), match.group(2), match.group(3) ,a) + os.path.splitext(file_name)[1]

# 示例用法
folder_path = "my_images"
pattern = r"IMG_(.{4})(.{2})(.{2})_.*"  # 例如：匹配以“pattern”开头的文件名，并提取其后的部分
rename_files_by_pattern(folder_path, pattern)

