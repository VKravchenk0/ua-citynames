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

    def write_result_to_file(self, df, item_counts, result_file_name, label):
        longest_string_length = df.display_name.str.len().max()
        number_of_dots = longest_string_length + 10
        FileUtils().create_output_dir(result_file_name)
        with open(FileUtils().get_output_file_path(result_file_name), 'a') as fp:
            fp.write(label + '\n')
            count_label = "Кількість"
            count_label_length = len(count_label)
            fp.write(f'{"Назва":.<{number_of_dots - count_label_length}}{count_label}\n')
            for idx, name in enumerate(item_counts.index.tolist()):
                count = item_counts[idx]
                # for formatting purposes
                number_of_digits_in_count = len(str(count))
                fp.write(f'{name:.<{number_of_dots - number_of_digits_in_count}}{count}\n')

            fp.write('\n\n')

    def process_dataset(self, input_file_location):

        original_dataset = pd.read_json(input_file_location)

        # renaming columns
        original_dataset.rename(columns={
            'Назва об\'єкта українською мовою': 'name',
            'Категорія': 'category',
            'Перший рівень': 'firstLevelCode',
            'Другий рівень': 'secondLevelCode',
        }, inplace=True)

        high_level_entity_names = self.get_high_level_entity_names(original_dataset)

        df = self.prepare_dataset(original_dataset)

        grouped = df.groupby(df.firstLevelCode)

        for group_code, group in grouped:
            self.sort_and_write_dataset_to_file(group,
                                                result_file_name="result_" + high_level_entity_names[group_code],
                                                label=high_level_entity_names[group_code])

        self.sort_and_write_dataset_to_file(df, result_file_name="result", label="ВСЯ УКРАЇНА")

    def prepare_dataset(self, df):
        # deleting unused columns
        df = df[['firstLevelCode', 'name', 'category']]

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
        return df

    def get_high_level_entity_names(self, df):
        df = df[df.secondLevelCode.isin([''])]
        df = df[['firstLevelCode', 'name']]
        code_name_dict = df.to_dict('list')
        result = {}
        for index in range(len(code_name_dict['firstLevelCode'])):
            result[code_name_dict['firstLevelCode'][index]] = code_name_dict['name'][index].split('/')[0]

        return result


    def sort_and_write_dataset_to_file(self, df, result_file_name, label):
        df = df.sort_values('name')
        # [df['display_name'].unique()] - магічне сортування за алфавітом
        item_counts = df["display_name"].value_counts()[df['display_name'].unique()]
        # item_counts = df["display_name"].value_counts() # - сортування за кількістю населених пунктів з назвою
        print(item_counts)
        self.write_result_to_file(df, item_counts, result_file_name, label)