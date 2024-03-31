## code to read in and refine data

import pandas as pd
import re

# require user ot input filepath
filepath = input('Data filepath: ')

# define class to load and refine data
class DataLoader:
    def __init__(self, filepath) -> None:
        try:
            self.df = pd.read_csv(filepath)
        except Exception as e:
            print('File could not be read')
            print(f'Error: {e}')
        
    # print error rows and drop from df
    def _error_handler(self, col, errors):
        print(f'The following records contain invalid data types in column \'{col}\': ')
        print(self.df.loc[errors.index, 'Record_Number'].to_string(index = False))
        print('Dropping records from data')
        self.df.drop(index = errors.index, inplace = True)

    # method for checking columns expected to be integeres, with or without 'X' as well
    def _integer_checker(self, col, min = None, max = None, include_x = False):
        data = self.df[col]
        # quicker method if range of acceptable values known
        if max != None and min != None:
            vals = list(range(min, max + 1))
            if include_x == True:
                vals.append('X')
                # if x included, values are stored as strings
                vals = [str(x) for x in vals]
            err = data[~data.isin(vals)]
        # alternative if one of min or max, or all integers
        else:
            err = data[data.apply(lambda x: not str(x).isdigit())]
            data = data.drop(index = err.index).astype(int)
            if max != None:
                err = pd.concat([err, data[data > max]])
            elif min != None:
                err = pd.concat([err, data[data < max]])
            if include_x == True:
                err = err[err != 'X']

        # handle error rows
        if len(err) > 0:
            self._error_handler(col, err)
        else:
            print(f'All data values in column \'{col}\' match expected data type')

    # method to check if values in defined list of possible values
    def _known_values_checker(self, col, vals):
        data = self.df[col]
        err = data[~data.isin(vals)]
        # handle error rows
        if len(err) > 0:
            self._error_handler(col, err)
        else:
            print(f'All data values in column \'{col}\' match expected data type')


    def _string_checker(self, col, regex):
        data = self.df[col]
        err = data[~data.apply(lambda x: bool(regex.match(x)))]
        # handle error rows
        if len(err) > 0:
            self._error_handler(col, err)
        else:
            print(f'All data values in column \'{col}\' match expected data type')

    def refine_data(self):
        self._integer_checker('Record_Number', min = 1)
        self._string_checker('Region', re.compile(r'^[A-Za-z]\d{8}$'))
        self._known_values_checker('RESIDENCE_TYPE', ['P', 'C'])
        self._integer_checker('Family_Composition', min = 0, max = 5, include_x = True)
        self._integer_checker('sex', min = 1, max = 2)
        self._integer_checker('age', min = 1, max = 8)
        self._integer_checker('Marital_Status', min = 1, max = 5)
        self._integer_checker('student', min = 1, max = 2)
        self._integer_checker('Country_Of_Birth', min = 1, max = 2)
        self._integer_checker('health', min = 1, max = 5)
        self._integer_checker('Ethnic_Group', min = 1, max = 6)
        self._integer_checker('religion', min = 1, max = 9)
        self._integer_checker('Economic_Activity', min = 1, max = 9, include_x = True)
        self._integer_checker('Occupation', min = 1, max = 9, include_x = True)
        self._integer_checker('industry', min = 1, max = 13, include_x = True)
        self._integer_checker('Hours_Worked_Per_Week', min = 1, max = 4, include_x = True)
        self._integer_checker('Approximate_Social_Grade', min = 1, max = 4, include_x = True)
    
    def drop_duplicates(self):
        len1 = len(self.df)
        self.df.drop_duplicates(subset = list(self.df.columns).remove('Record_Number'), inplace = True)
        len2 = len(self.df)
        if len1 - len2 != 0:
            print(f'{len1 - len2} duplicated rows removed')
        else:
            print('No duplicated rows found')

if __name__ == '__main__':
    dl = DataLoader(filepath)
    dl.refine_data()
    dl.drop_duplicates()
    print('Saving refined data')
    dl.df.to_csv(filepath[:-4] + '_refined.csv')