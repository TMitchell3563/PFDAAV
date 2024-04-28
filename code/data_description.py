import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets
import math

__name__ = "__main__"

class DataDescriber:
    """
    This class produces descriptions of a dataset.
    """
    def __init__(self, filepath):
        """
        Constructor for DataDescriber.

        Parameters:
        - filepath (str): filepath where .csv data is found.
        """
        try:
            self.df = pd.read_csv(filepath)
            self.df.set_index(self.df.columns[0], drop = True, inplace = True)
        except Exception as e:
            print('File could not be read')
            print(f'Error: {e}')

    def _value_interpreter(self):
        """ 
        Method to read in descriptions from helper file.
        """
        # Read in data
        desc_df = pd.read_excel('..\data\Teaching_File_Variable_List.xlsx')
        desc_df.drop(0, inplace = True)

        # Clean data, replacing NaN values
        for i in range(len(desc_df['Variable Name'])):
            try:
                if math.isnan(desc_df.iloc[i, 0]):
                    desc_df.iloc[i, 0] = desc_df.iloc[i - 1, 0]
                    desc_df.iloc[i, 1] = desc_df.iloc[i - 1, 1]
            except:
                next

        # Create columns for alphanumeric character and description
        desc_df[['Alphanumerical', 'Desc']] = desc_df['Variable Values'].str.split('.', expand=True)
        desc_df.drop(columns=['Variable Values'], inplace=True)
        desc_df['Desc'] = desc_df['Desc'].str.strip()
        desc_df.loc[desc_df['Variable Name'] == 'Student (Schoolchild or full-time student)', 'Variable Name'] = 'Student'
        desc_df.loc[desc_df['Variable Name'] == 'Health (General health)', 'Variable Name'] = 'Health'

        # Record in dictionary
        self.variable_dict = {k:{v: s for v, s in zip(desc_df.loc[desc_df['Variable Name'] == k, 'Alphanumerical'], desc_df.loc[desc_df['Variable Name'] == k, 'Desc'])} for k in desc_df['Variable Name']}

    def _sort_list(self, list):
        """
        Sorts column values, taking into account whether string or int.

        Paramters:
        - list (List[str, int]): list of values to sort.

        Returns:
        List[str, int]: list in sorted order.
        """
        if 'X' in list:
            sorted_cols = [str(x) for x in sorted([int(x) for x in list if x != 'X'])]
            sorted_cols.append('X')
        else:
            sorted_cols = sorted(list)
        return(sorted_cols)

    def no_records(self):
        """
        Prints the number of records in the dataset.
        """
        n = len(self.df)
        print(f'The data set has {n} rows')

    def col_types(self):
        """
        Prints the type of data for each column in the dataset.
        """
        for i in self.df.columns:
            dtype = type(self.df[i][0])
            print(f'Column {i} is of data type {dtype}')
        
    def unique_values(self):
        """
        Prints the unique values for each column in dataset.
        """
        self._value_interpreter()
        cols = [x for x in list(self.df.columns) if x not in ['Record_Number', 'Region']]
        for i in cols:
            vals = self.df[i].unique()
            vals.sort()
            vals_int = [f'{x} ({self.variable_dict[i][str(x)]})' for x in vals]
            print(f'Column {i} takes values {vals_int}')

    def _grouped_no_records(self, col1, col2, col1_vals = 'None', col2_vals = 'None', summary_stats = 'None', proportional = 'Count'):
        """
        Groups dataset by specified columns and produces heatmap

        Parameters:
        - col1 (str): name of first column to groupby.
        - col2 (str): name of second column to groupby.
        - col1_vals (List[str]): values of column 1 to display.
        - col2_vals (List[str]): values of column 2 to display.
        - summary_stats (str): choose whether to display counts for only one column rather than a heatmap.
        - proportional (str): choose whether to display count of records, or proportion of dataset.
        """
        grouped_mi = self.df.groupby([col1, col2])['Record_Number'].count()
        grouped_df = pd.DataFrame(grouped_mi)
        # If specified, only select values parsed to function
        if col1_vals != 'None':
            grouped_df = grouped_df[grouped_df.index.get_level_values(0).isin(col1_vals)] 
        if col2_vals != 'None':
            grouped_df = grouped_df[grouped_df.index.get_level_values(1).isin(col2_vals)]
        # If specified, group all values of specified column
        if summary_stats == col1:
            if col1 == col2:
                grouped_df.index = grouped_df.index.droplevel(1)
            else:
                grouped_df.index = grouped_df.index.droplevel(col2)
            grouped_df = grouped_df.groupby(col1).sum()
            if proportional == 'Proportion':
                grouped_df = grouped_df.div(grouped_df.sum().sum())
                grouped_df.rename(columns = {'Record_Number': 'Proportion of Records'}, inplace = True)
                fmt = '.2f'
            else:
                grouped_df.rename(columns = {'Record_Number': 'Number of Records'}, inplace = True)
                fmt = 'd'
            plt.figure(figsize=(14, 10))
            sns.heatmap(grouped_df, annot=True, cmap="YlGnBu", fmt=fmt, cbar=True, square = True, cbar_kws={'shrink': 0.5},
                    linecolor='gray', linewidth=0.2)
            return
        if summary_stats == col2:
            if col1 == col2:
                grouped_df.index = grouped_df.index.droplevel(1)
            else:
                grouped_df.index = grouped_df.index.droplevel(col1)
            grouped_df = grouped_df.groupby(col2).sum()
            if proportional == 'Proportion':
                grouped_df = grouped_df.div(grouped_df.sum().sum())
                grouped_df.rename(columns = {'Record_Number': 'Proportion of Records'}, inplace = True)
                fmt = '.2f'
            else:
                grouped_df.rename(columns = {'Record_Number': 'Number of Records'}, inplace = True)
                fmt = 'd'
            plt.figure(figsize=(14, 10))
            sns.heatmap(grouped_df, annot=True, cmap="YlGnBu", fmt=fmt, cbar=True, square = True, cbar_kws={'shrink': 0.5},
                        linecolor='gray', linewidth=0.2)
            return
        grouped_df = grouped_df.unstack().fillna(0).astype(int)
        grouped_df.columns = grouped_df.columns.droplevel()
        sorted_cols = self._sort_list(grouped_df.columns)
        grouped_df = grouped_df.reindex(sorted_cols, axis = 1)
        fmt = 'd'

        if proportional == 'Proportion':
            grouped_df = grouped_df.div(grouped_df.sum().sum())
            fmt = '.2f'
        
        # Plot heatmap
        plt.figure(figsize=(14, 10))
        sns.heatmap(grouped_df, annot=True, cmap="coolwarm", fmt=fmt, cbar=True, square = True, cbar_kws={'shrink': 0.5},
                    linecolor='gray', linewidth=0.2)
        plt.show()
        
    def _update_col1_values(self, col1):
        """
        Updates widgets according to column 1 selected

        Parameters:
        - col1 (str): column 1 selected to filter by
        """
        unique_values = self._sort_list(self.df[col1].unique())
        self.col1_vals.options = unique_values
        self.col1_vals.value = unique_values
        self.col1_vals.description = f'{col1}: '
        if col1 != self.dropdown2.value:
            self.dropdown4.options = ['None', col1, self.dropdown2.value]
        else:
            self.dropdown4.options = ['None', col1]
    
    def _update_col2_values(self, col2):
        """
        Updates widgets according to column 2 selected

        Parameters:
        - col1 (str): column 2 selected to filter by
        """
        unique_values = self._sort_list(self.df[col2].unique())
        self.col2_vals.options = unique_values
        self.col2_vals.value = unique_values
        self.col2_vals.description = f'{col2}: '
        if col2 != self.dropdown1.value:
            self.dropdown4.options = ['None', self.dropdown1.value, col2]
        else:
            self.dropdown4.options = ['None', col2]

        
    def group_data(self):
        """
        Produces widgets to interact with heatmap created by _grouped_no_records
        """
        # Dropdown menu widgets for column 1, column 2, and summary_stats
        self.dropdown1 = widgets.Dropdown(options=self.df.columns.drop('Record_Number'), value='Age', description='Factor: ')
        self.dropdown2 = widgets.Dropdown(options=self.df.columns.drop('Record_Number'), value='Health', description='Factor: ')
        self.dropdown3 = widgets.Dropdown(options=['Count', 'Proportion'], value='Count', description='Factor: ')
        # Checkbox widgets for selecting column values to display
        style = {'description_width': 'initial'}
        col1_values = self._sort_list(self.df[self.dropdown1.value].unique())
        self.col1_vals = widgets.SelectMultiple(options=col1_values, value=col1_values, description=f'{self.dropdown1.value}:', style = style)
        col2_values = self._sort_list(self.df[self.dropdown2.value].unique())
        self.col2_vals = widgets.SelectMultiple(options=col2_values, value=col2_values, description=f'{self.dropdown2.value}:', style = style)
        self.dropdown4 = widgets.Dropdown(options = ['None', self.dropdown1.value, self.dropdown2.value], value = 'None', description = 'Summary stats: ', style = style)
        
        # Update checkbox values when dropdown values change
        self.dropdown1.observe(lambda change: self._update_col1_values(change.new), names='value')
        self.dropdown2.observe(lambda change: self._update_col2_values(change.new), names='value')
        
        # Interact function to update the plot based on widget selections
        interact(self._grouped_no_records, col1=self.dropdown1, col2 = self.dropdown2, col1_vals=self.col1_vals, 
                 col2_vals= self.col2_vals, summary_stats = self.dropdown4, proportional = self.dropdown3)
