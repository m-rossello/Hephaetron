#!/usr/bin/env python3

"""
RenameTable.py

Author: Maria Rossello
Date updated: Ago 2024
Contact: mariarossello@ub.edu

Description:
This script processes a table of equivalences to replace names in a given file.
It reads a tab-separated table of equivalences and a file to convert, and replaces 
the names in the specified column or all columns of the file based on the equivalences table. 
The output can be saved to a file or printed to the terminal.

Usage:
python RenameTable.py -t <table_file> -f <input_file> [-c <column_number>] [-o <output_file>]

Arguments:
    -t, --table <table_file>: Path to the table of equivalences. First column should have the name that is in the file to convert, second column the new name. Must be tab separated.
    -f, --file <input_file>: Path to the file to convert.
    -c, --column <column_number>: The column number in the input file to apply the replacements (optional). If not provided, all columns will be checked.
    -o, --output <output_file>: Path to the output file (optional). If not provided, output is printed to the terminal.

Requirements:
    - Python 3.9 or later
    - pandas
    - argparse
"""

#########################################################################################################
# PROGRAM ARGUMENTS
#########################################################################################################

import sys
import pandas as pd
import argparse

# Setting up argument parser
parser = argparse.ArgumentParser(prog='RenameTable.py',
                                 description='''This script processes a table of equivalences to replace names in a given file.''',
                                 formatter_class=argparse.RawTextHelpFormatter)

# Defining required and optional arguments
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

# Adding required arguments
required.add_argument('-t', '--table',
                      help='''Table of equivalences. First column should have the name that is in the file to convert,
                      second column the new name. Must be tab separated.''',
                      type=argparse.FileType('r'),
                      required=True)

required.add_argument('-f', '--file',
                      help='File to convert. Can be a long table.',
                      type=argparse.FileType('r'),
                      required=True)

# Adding optional argument for column number
optional.add_argument('-c', '--column',
                      help='Column number in the input file to apply the replacements (optional).',
                      type=int,
                      required=False)

# Adding optional argument for output file
optional.add_argument('-o', '--output',
                      help='Output file name.',
                      type=argparse.FileType('w'),
                      required=False)

# Parsing arguments
args = parser.parse_args()

# Validate required arguments
if args.table is None or args.file is None:
    parser.print_help()
    sys.exit(1)

#########################################################################################################
# FUNCTIONS
#########################################################################################################

def open_table_files(file_path):
    """
    Reads the equivalences table or input file.
    
    Args:
        file_path (str): Path to the table file or input file.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the table or input file.
    """
    table = pd.read_csv(file_path, sep='\t', header=None, comment='#', dtype=str)
    return table

def make_dict_from_table(table_df):
    """
    Reads a tab-separated file and returns a dictionary where keys are the first column 
    and values are the second column.
    
    Args:
        table_df (pandas.DataFrame): DataFrame containing the equivalences table.
    
    Returns:
        dict: Dictionary mapping original names to new names.
    """
    equivalences_dict = dict(zip(table_df.iloc[:, 0], table_df.iloc[:, 1]))
    return equivalences_dict

def substitute_column_values(df, substitutions_dict, column_index):
    """
    Substitutes values in a specified column of a DataFrame using a given dictionary.
    Handles cells containing lists or individual values.

    Args:
    - df (pd.DataFrame): The DataFrame whose column values are to be substituted.
    - substitutions_dict (dict): A dictionary where keys are the values to be replaced and values are the replacements.
    - column_index (int): The column index in which to apply the substitutions.

    Returns:
    - pd.DataFrame: A new DataFrame with substituted values in the specified column.
    """

    def substitute_value(value):
        if isinstance(value, list):
        # The value is a list
            return [substitutions_dict.get(str(item), str(item)) for item in value]
        else:
        # The value is not a list
            return substitutions_dict.get(str(value), str(value))

    df.iloc[:, column_index] = df.iloc[:, column_index].map(substitute_value)
    return df

def substitute_all_values(df, substitutions_dict):
    """
    Substitutes values in all columns of a DataFrame using a given dictionary.
    Handles cells containing lists or individual values.

    Args:
    - df (pd.DataFrame): The DataFrame whose values are to be substituted. Each cell may contain a list of values or a single value.
    - substitutions_dict (dict): A dictionary where keys are the values to be replaced and values are the replacements.

    Returns:
    - pd.DataFrame: A new DataFrame with substituted values.
    """

    def substitute_in_cell(cell):
        if isinstance(cell, list):
        # The value is a list
            return ' '.join([substitutions_dict.get(str(item), str(item)) for item in cell])
        else:
        # The value is not a list
            return substitutions_dict.get(str(cell), str(cell))
    
    return df.applymap(substitute_in_cell)

#########################################################################################################
# PROCESS DATA
#########################################################################################################

# Open files
equivalences_table = open_table_files(args.table)
file_df = open_table_files(args.file)
file_df = file_df.applymap(lambda x: x.split(' ') if isinstance(x, str) else x)

# Transform the table of equivalences to a dictionary
equivalences_dict = make_dict_from_table(equivalences_table)

# Apply the renaming to the specified column or all columns
if args.column is not None:
    col_index = int(args.column) - 1
    substituted_df = substitute_column_values(file_df, equivalences_dict, col_index)
else:
    substituted_df = substitute_all_values(file_df, equivalences_dict)

# Write or print the output
try:
    if args.output:
        substituted_df.to_csv(args.output, index=False, sep='\t', header=False)
    else:
        final_file = substituted_df.to_csv(sep='\t', index=False, header=False, lineterminator='\n')
        print(final_file)
except BrokenPipeError:
    pass
