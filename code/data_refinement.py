## code to read in and refine data. Can be called from terminal, or DataLoader class imported

import pandas as pd
import re
import argparse

# define class to load and refine data
class DataLoader:
    """ 
    This class loads in and refines the parsed dataset
    """
    def __init__(self, filepath):
        """
        Constructor for DataDescriber.

        Parameters:
        - filepath (str): filepath where .csv data is found.
        """
        try:
            self.df = pd.read_csv(filepath)
        except Exception as e:
            print('File could not be read')
            print(f'Error: {e}')

    def _rename_cols(self):
        """ 
        Method to convert all columns in dataset to standardised capitalised format
        """
        # Create a dictionary to map current column names to new column names
        new_column_names = {}
        for column in self.df.columns:
            # Split the column name by underscores and capitalize the first letter of each word
            words = column.split('_')
            capitalized_words = [word.capitalize() for word in words]
            # Join the words back together with underscores
            new_column_name = '_'.join(capitalized_words)
            # Store the mapping in the dictionary
            new_column_names[column] = new_column_name

        self.df.rename(columns=new_column_names, inplace=True)
        
    def _error_handler(self, col, errors):
        """ 
        Method to print error rows and drop from df

        Parameters:
         - col (str): column that contains error
         - errors (list): list of values causing errors in column

        Returns:
        Prints error warnings and drops rows with errors in
        """
        print(f'The following records contain invalid data types in column \'{col}\': ')
        print(self.df.loc[errors.index, 'Record_Number'].to_string(index = False))
        print('Dropping records from data')
        self.df.drop(index = errors.index, inplace = True)

    def _integer_checker(self, col, min = None, max = None, include_x = False):
        """ 
        Method for checking columns expected to be integeres, with or without 'X' as well

        Parameters:
         - col (str): column to check
         - min (int): minimum integer value column can take
         - max (int): maximum integer value column can take
         - include_x (bool): True if 'X' is a valid value
        """
        data = self.df[col]
        # Quicker method if range of acceptable values known
        if max != None and min != None:
            vals = list(range(min, max + 1))
            if include_x == True:
                vals.append('X')
                # If x included, values are stored as strings
                vals = [str(x) for x in vals]
            err = data[~data.isin(vals)]
        # Alternative if one of min or max, or all integers acceptable
        else:
            err = data[data.apply(lambda x: not str(x).isdigit())]
            data = data.drop(index = err.index).astype(int)
            if max != None:
                err = pd.concat([err, data[data > max]])
            elif min != None:
                err = pd.concat([err, data[data < max]])
            if include_x == True:
                err = err[err != 'X']

        # Handle error rows
        if len(err) > 0:
            self._error_handler(col, err)
        else:
            print(f'All data values in column \'{col}\' match expected data type')

    def _known_values_checker(self, col, vals):
        """ 
        Method to check if values in defined list of possible values

        Parameters:
         - col (str): column to check values of
         - vals (list): list of acceptable values for column
        """
        data = self.df[col]
        err = data[~data.isin(vals)]
        # Handle error rows
        if len(err) > 0:
            self._error_handler(col, err)
        else:
            print(f'All data values in column \'{col}\' match expected data type')


    def _string_checker(self, col, regex):
        """ 
        Method to check if values are of acceptable regular expression form

        Parameters:
         - col (str): column to check values of
         - regex (str): form of acceptable entries
        """
        data = self.df[col]
        err = data[~data.apply(lambda x: bool(regex.match(x)))]
        # Handle error rows
        if len(err) > 0:
            self._error_handler(col, err)
        else:
            print(f'All data values in column \'{col}\' match expected data type')

    def refine_data(self):
        """ 
        Method to check values of 'Scotland_teaching_file_1PCT.csv' as defined in 'Teaching_File_Variable_List.csv'. Drops rows that aren't. See data folder for more info
        """
        self._integer_checker('Record_Number', min = 1)
        self._string_checker('Region', re.compile(r'^[A-Za-z]\d{8}$'))
        self._known_values_checker('Residence_Type', ['P', 'C'])
        self._integer_checker('Family_Composition', min = 0, max = 5, include_x = True)
        self._integer_checker('Sex', min = 1, max = 2)
        self._integer_checker('Age', min = 1, max = 8)
        self._integer_checker('Marital_Status', min = 1, max = 5)
        self._integer_checker('Student', min = 1, max = 2)
        self._integer_checker('Country_Of_Birth', min = 1, max = 2)
        self._integer_checker('Health', min = 1, max = 5)
        self._integer_checker('Ethnic_Group', min = 1, max = 6)
        self._integer_checker('Religion', min = 1, max = 9)
        self._integer_checker('Economic_Activity', min = 1, max = 9, include_x = True)
        self._integer_checker('Occupation', min = 1, max = 9, include_x = True)
        self._integer_checker('Industry', min = 1, max = 13, include_x = True)
        self._integer_checker('Hours_Worked_Per_Week', min = 1, max = 4, include_x = True)
        self._integer_checker('Approximate_Social_Grade', min = 1, max = 4, include_x = True)
    
    def drop_duplicates(self):
        """ 
        Method to drop rows if duplicated exactly.
        """
        len1 = len(self.df)
        self.df.drop_duplicates(subset = list(self.df.columns).remove('Record_Number'), inplace = True)
        len2 = len(self.df)
        # Print statement clarifying whether rows dropped or not
        if len1 - len2 != 0:
            print(f'{len1 - len2} duplicated rows removed')
        else:
            print('No duplicated rows found')

# If code ran from terminal, cover all relevant data analysis steps. See data_refinement.bat for command line prompt
if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="Filepath")
    args = parser.parse_args()
    dl = DataLoader(args.filepath)
    dl._rename_cols()
    dl.refine_data()
    dl.drop_duplicates()
    print('Saving refined data')
    dl.df.to_csv(args.filepath[:-4] + '_refined.csv')