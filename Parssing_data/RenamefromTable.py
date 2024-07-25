#!/usr/bin/env python3

"""
RenamefromTable.py

Author: Maria Rossello
Date created: 30/11/2022

Description:
This script processes a table of equivalences to replace names in a given file. 
It reads a tab-separated table of equivalences and a file to convert, and replaces 
the names in the file based on the equivalences table. The output can be saved to 
a file or printed to the terminal.

Usage:
python RenamefromTable.py -t <table_file> -f <input_file> [-o <output_file>]

Arguments:
    -t, --table <table_file>: Path to the table of equivalences (tab-separated).
    -f, --file <input_file>: Path to the file to convert.
    -o, --output <output_file>: Path to the output file (optional). If not provided, output is printed to the terminal.

Requirements:
    - Python 3.9 or later
    - pandas
"""

#########################################################################################################
# PROGRAM ARGUMENTS
#########################################################################################################

import sys
import pandas as pd
import argparse

parser = argparse.ArgumentParser(prog='RenamefromTable.py',
                                 description='''This script processes a table of equivalences to replace names in a given file.''',
                                 formatter_class=argparse.RawTextHelpFormatter)

required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

required.add_argument('-t', '--table',
                      help='''Table of equivalences. First column should have the name that is in the file to convert,
                      second column the new name. Must be tab separated.''',
                      type=argparse.FileType('r'),
                      required=True)

required.add_argument('-f', '--file',
                      help='File to convert. Can be a long table.',
                      type=argparse.FileType('r'),
                      required=True)

optional.add_argument('-o', '--output',
                      help='Output file name.',
                      type=argparse.FileType('w'),
                      required=False)

args = parser.parse_args()

if args.table is None or args.file is None:
    parser.print_help()
    sys.exit(1)

#########################################################################################################
# FUNCTIONS
#########################################################################################################

def replace_names(line, equivalences):
    """
    Replace names in a line based on a dictionary of equivalences.

    Args:
        line (str): Line of text to process.
        equivalences (dict): Dictionary with the equivalences for name replacement.

    Returns:
        str: Line with names replaced based on the equivalences.
    """
    parts = line.split()
    new_line = []
    for part in parts:
        if part in equivalences:
            new_line.append(equivalences[part])
        else:
            new_line.append(part)
    return ' '.join(new_line)

#########################################################################################################
# MAIN EXECUTION
#########################################################################################################

def main():
    """
    Main function to execute the script.
    """
    # Transform the table of equivalences to a dictionary
    table_df = pd.read_csv(args.table, sep='\t', header=None)
    equivalences = dict(zip(table_df.iloc[:,0], table_df.iloc[:,1]))

    try:
        if args.output:
            with args.output as f:
                # Process and save the input file line by line
                for line in args.file:
                    output_line = replace_names(line.strip(), equivalences)
                    f.write(output_line + '\n')
        else:
            # Process and print the input file line by line to the terminal
            for line in args.file:
                output_line = replace_names(line.strip(), equivalences)
                print(output_line)
    except BrokenPipeError:
        pass

if __name__ == "__main__":
    main()