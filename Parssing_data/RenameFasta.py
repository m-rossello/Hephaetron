#!/usr/bin/env python3

"""
RenameFastaHeaders.py

Author: Maria Rossello
Date updated: July 2024
Contact: mariarossello@ub.edu

Description:
This script processes a table of equivalences to replace headers in a given FASTA file.
It reads a tab-separated table of equivalences and a FASTA file, and replaces 
the headers in the FASTA file based on the equivalences table. 
The output can be saved to a file or printed to the terminal.

Usage:
python RenameFastaHeaders.py -t <table_file> -f <input_file> [-o <output_file>]

Arguments:
    -t, --table <table_file>: Path to the table of equivalences. First column should have the name that is in the FASTA headers to convert, second column the new name. Must be tab separated.
    -f, --file <input_file>: Path to the FASTA file to convert. Use '-' to read from standard input.
    -o, --output <output_file>: Path to the output file (optional). If not provided, output is printed to the terminal.

Requirements:
    - Python 3.9 or later
    - pandas
    - argparse
    - BioPython
"""

#########################################################################################################
# PROGRAM ARGUMENTS
#########################################################################################################

import sys
import pandas as pd
import argparse
from Bio import SeqIO

# Setting up argument parser
parser = argparse.ArgumentParser(prog='RenameFastaHeaders.py',
                                 description='''This script processes a table of equivalences to replace headers in a given FASTA file.''',
                                 formatter_class=argparse.RawTextHelpFormatter)

# Defining required and optional arguments
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

# Adding required arguments
required.add_argument('-t', '--table',
                      help='''Table of equivalences. First column should have the name that is in the FASTA headers to convert,
                      second column the new name. Must be tab separated.''',
                      type=argparse.FileType('r'),
                      required=True)

required.add_argument('-f', '--file',
                      help='FASTA file to convert. Use "-" to read from standard input.',
                      type=str,
                      required=True)

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

def open_table_file(file_path):
    """
    Reads the equivalences table and ensures it has two columns.
    
    Args:
        file_path (str): Path to the table file.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the equivalences table.
    
    Raises:
        ValueError: If the table does not have exactly two columns.
    """
    table = pd.read_csv(file_path, sep='\t', header=None, comment='#', dtype=str)
    if table.shape[1] != 2:
        raise ValueError("The table of equivalences must have exactly two columns.")
    return table

def make_dict_from_table(table_df):
    """
    Reads a tab-separated file and returns a dictionary where keys are the first column 
    and values are the second column.
    
    Args:
        table_df (pandas.DataFrame): DataFrame containing the equivalences table.
    
    Returns:
        dict: Dictionary mapping original headers to new headers.
    """
    equivalences_dict = dict(zip(table_df.iloc[:, 0], table_df.iloc[:, 1]))
    return equivalences_dict

def rename_fasta_headers(fasta_file, equivalences_dict):
    """
    Renames headers in a FASTA file using a given dictionary.
    
    Args:
        fasta_file (str): Path to the input FASTA file or '-' for standard input.
        equivalences_dict (dict): Dictionary where keys are the headers to be replaced 
                                  and values are the new headers.
    
    Returns:
        list: List of SeqRecord objects with renamed headers.
    """
    if fasta_file == '-':
        fasta_input = sys.stdin
    else:
        fasta_input = fasta_file

    records = []
    for record in SeqIO.parse(fasta_input, "fasta"):
        if record.id in equivalences_dict:
            new_id = equivalences_dict[record.id]
            record.id = new_id
            record.description = new_id
        records.append(record)
    return records

#########################################################################################################
# PROCESS DATA
#########################################################################################################

# Open files
equivalences_table = open_table_file(args.table)
equivalences_dict = make_dict_from_table(equivalences_table)

# Rename the FASTA headers
renamed_records = rename_fasta_headers(args.file, equivalences_dict)

# Write or print the output
try:
    if args.output:
        SeqIO.write(renamed_records, args.output.name, "fasta")
    else:
        SeqIO.write(renamed_records, sys.stdout, "fasta")
except BrokenPipeError:
    pass
