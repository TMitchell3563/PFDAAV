import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets import interact, widgets

__name__ = "__main__"

class DataPlotter:
    def __init__(self, filepath):
        """ 
        Method to create instance of DataPlotter class

        Parameters:
         - filepath (str): filepath of .csv file containing data to read in
        """
        try:
            self.df = pd.read_csv(filepath)
            self.df.set_index(self.df.columns[0], drop = True, inplace = True)
        except Exception as e:
            print('File could not be read')
            print(f'Error: {e}')

    def _plot_bar_chart(self, col):
        """ 
        Method to plot bar chart of number of occurrences of each category for a column

        Parameters:
         - col (str): string containing oolumn header to plot bar chart for

        Returns:
        Bar chart of number of occurrences of each category for a column
        """
        # Get the value counts for the column
        counts = self.df[col].value_counts().sort_index()

        # Plotting
        plt.figure(figsize=(8, 6))
        counts.plot(kind='bar')
        plt.title('Number of Occurrences')
        plt.xlabel(col)
        plt.ylabel('Occurrences')
        plt.xticks(rotation=0)  # Rotate x labels if needed
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.show()

    def bar_chart(self):
        """ 
        Method to plot interactive bar chart using ipywidgets
        """
        # Dropdown menu widget
        self.dropdown = widgets.Dropdown(options=self.df.columns.drop('Record_Number'), value='age', description='Factor: ')

        # Interactive widget to update the plot based on dropdown selection
        interact(self._plot_bar_chart, col=self.dropdown)
        
    def _plot_pie_chart(self, col, explode_val, explode_max):
        """ 
        Method to plot a pie chart showing percentage of entries belonging to each category

        Parameters:
         - col (str): string containing oolumn header to plot pie chart for
         - explode_val (float [0, inf)): number defining how much to explode small values
         - explode_max (float [0, 1]): number defining max percentage to explode

        Returns:
        Pie chart showing percentage of entries belonging to each category
        """
        # Get the value counts for the column
        counts = self.df[col].value_counts().sort_index()

        # Highlight the dominant category
        explode = [0 if counts[x] / sum(counts) >= explode_max else explode_val for x in counts.index]
        # Plot the pie chart            
        plt.figure(figsize=(8, 6))
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, explode=explode)
        plt.title(f'Proportion of Occurrences for each category of {col.capitalize()}')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.show() 

    def pie_chart(self):
        """ 
        Method to create an interactive pie chart using ipywidgets
        """
        # Dropdown menu widget
        self.dropdown = widgets.Dropdown(options=self.df.columns.drop('Record_Number'), value='Age', description='Factor: ')

        # Sliders to control explosion
        layout = widgets.Layout(width = '20%')
        style = {'description_width': 'initial'}
        self.explode_slider = widgets.FloatSlider(value=0.25, min=0, max=1.0, step=0.05, description='Small value explosion: ', layout = layout, style=style)
        self.explode_max_slider = widgets.FloatSlider(value=0.05, min=0, max=1, step=0.005, description='Max value to explode: ', layout = layout, style=style)

        # Interactive widget to update the plot based on dropdown selection
        interact(self._plot_pie_chart, col=self.dropdown, explode_val = self.explode_slider, explode_max = self.explode_max_slider)
