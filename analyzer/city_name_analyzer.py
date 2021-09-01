import pandas as pd
import re

from utils.utils import FileUtils


class CityNameAnalyzer:

    settlement_types_dict = {
        'С': 'с. ',
        'Щ': 'с-ще ',
        'Т': 'смт. ',
        'М': 'м. '
    }
    
    def print_df(self, step_name, df):
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

    def remove_latin(self, string):
        return string.replace('A', 'А').replace('C', 'С').replace('I', 'І')

    def process_case(self, name):
        name_lowercase = name.lower()
        punc_filter = re.compile('([- ]\s*)')
        split_with_punctuation = punc_filter.split(name_lowercase)

        final = ''.join([i.capitalize() for i in split_with_punctuation])
        return final

    def add_settlement_type_prefix(self, row):
        return self.settlement_types_dict[row['category']] + row['display_name']

    def write_result_to_file(self, df, item_counts):
        longest_string_length = df.display_name.str.len().max()
        number_of_dots = longest_string_length + 10
        with open(FileUtils().get_output_file_name(), 'w') as fp:
            count_label = "Кількість"
            count_label_length = len(count_label)
            fp.write(f'{"Назва":.<{number_of_dots - count_label_length}}{count_label}\n')
            for idx, name in enumerate(item_counts.index.tolist()):
                count = item_counts[idx]
                # for formatting purposes
                number_of_digits_in_count = len(str(count))
                fp.write(f'{name:.<{number_of_dots - number_of_digits_in_count}}{count}\n')
    
    def process_dataset(self, input_file_location):

        df = pd.read_json(input_file_location)

        # renaming columns
        df.rename(columns={'Назва об\'єкта українською мовою': 'name', 'Категорія': 'category'}, inplace=True)
        # deleting unused columns
        df = df[['name', 'category']]

        self.print_df("START", df)

        # deleting categories. Р - districts of large cities
        df = df[~df.category.isin(['', 'Р'])]

        self.print_df("CATEGORIES DELETED", df)

        # remove latin letters
        df['category'] = df.apply(lambda row: self.remove_latin(row['category']), axis=1)
        df['name'] = df.apply(lambda row: self.remove_latin(row['name']), axis=1)

        self.print_df("WITHOUT LATIN LETTERS", df)

        # process case
        df['display_name'] = df.apply(lambda row: self.process_case(row['name']), axis=1)

        self.print_df("WITH DISPLAY NAME", df)

        # add settlement type
        df['display_name'] = df.apply(lambda row: self.add_settlement_type_prefix(row), axis=1)

        self.print_df("WITH SETTLEMENT TYPE", df)

        df = df.sort_values('name')
        # [df['display_name'].unique()] - магічне сортування за алфавітом
        item_counts = df["display_name"].value_counts()[df['display_name'].unique()]
        # item_counts = df["display_name"].value_counts() # - сортування за кількістю населених пунктів з назвою
        print(item_counts)

        self.write_result_to_file(df, item_counts)