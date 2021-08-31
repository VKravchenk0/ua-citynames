import pandas as pd
import re
import os
import shutil
from pathlib import Path

dev = True
# dev = False

base_output_dir = './output'

settlement_types_dict = {
    'С': 'с. ',
    'Щ': 'с-ще ',
    'Т': 'смт. ',
    'М': 'м. '
}


def get_output_file_name():
    filename = 'result_dev.txt' if dev else 'result.txt'
    return f"{base_output_dir}/{filename}"


def reset_output_directory():
    delete_output_dir_if_exists()
    create_output_dir()


def delete_output_dir_if_exists():
    dirpath = Path(base_output_dir)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)


def create_output_dir():
    filename = get_output_file_name()
    os.makedirs(os.path.dirname(filename), exist_ok=True)


def print_df(step_name):
    print("\n")
    print("-------------------------------------------")
    print(f"-------------- {step_name} -----------")
    print("-------------------------------------------")
    print(df)
    print("--- category ---")
    print(df['category'].unique())
    print("--- name ---")
    print(df['name'].unique())
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


def remove_latin(string):
    return string.replace('A', 'А').replace('C', 'С').replace('I', 'І')


def process_case(name):
    name_lowercase = name.lower()
    punc_filter = re.compile('([- ]\s*)')
    split_with_punctuation = punc_filter.split(name_lowercase)

    final = ''.join([i.capitalize() for i in split_with_punctuation])
    return final


def add_settlement_type_prefix(row):
    return settlement_types_dict[row['category']] + row['display_name']

def write_result_to_file():
    longest_string_length = df.display_name.str.len().max()
    number_of_dots = longest_string_length + 10
    with open(get_output_file_name(), 'w') as fp:
        count_label = "Кількість"
        count_label_length = len(count_label)
        fp.write(f'{"Назва":.<{number_of_dots - count_label_length}}{count_label}\n')
        for idx, name in enumerate(item_counts.index.tolist()):
            count = item_counts[idx]
            # for formatting purposes
            number_of_digits_in_count = len(str(count))
            fp.write(f'{name:.<{number_of_dots - number_of_digits_in_count}}{count}\n')


reset_output_directory()

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

if dev:
    input_file = './input_files/dev_koatuu.json'
else:
    input_file = './input_files/koatuu.json'
df = pd.read_json(input_file)

# renaming columns
df.rename(columns={'Назва об\'єкта українською мовою': 'name', 'Категорія': 'category'}, inplace=True)
# deleting unused columns
df = df[['name', 'category']]

print_df("START")

# deleting categories. Р - districts of large cities
df = df[~df.category.isin(['', 'Р'])]

print_df("CATEGORIES DELETED")

# remove latin letters
df['category'] = df.apply(lambda row: remove_latin(row['category']), axis=1)
df['name'] = df.apply(lambda row: remove_latin(row['name']), axis=1)

print_df("WITHOUT LATIN LETTERS")

# process case
df['category'] = df.apply(lambda row: remove_latin(row['category']), axis=1)
df['display_name'] = df.apply(lambda row: process_case(row['name']), axis=1)

print_df("WITH DISPLAY NAME")

# add settlement type
df['category'] = df.apply(lambda row: remove_latin(row['category']), axis=1)
df['display_name'] = df.apply(lambda row: add_settlement_type_prefix(row), axis=1)

print_df("WITH SETTLEMENT TYPE")

df = df.sort_values('name')
# [df['display_name'].unique()] - магічне сортування за алфавітом
item_counts = df["display_name"].value_counts()[df['display_name'].unique()]
# item_counts = df["display_name"].value_counts() # - сортування за кількістю населених пунктів з назвою
print(item_counts)

write_result_to_file()
