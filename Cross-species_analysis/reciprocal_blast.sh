#!/bin/bash

#########################################################################################################
# Script Name: reciprocal_blast.sh
# Author: Maria Rossello
# Date created: July 2024
# Contact: mariarossello@ub.edu
#
# Description:
#     This script performs reciprocal BLASTP searches between two species databases using a query FASTA file.
#     It identifies reciprocal best hits and saves the results to an output directory.
#     Species A is the query species, and species B is the target species for the initial BLAST search.
#
# Usage:
#     ./reciprocal_blast.sh -q query_fasta -a species_A_db -b species_B_db -o output_directory [-e evalue]
#
# Arguments:
#     -q, --query: Path to the query FASTA file (from species A).
#     -a, --species_A_db: Name of the BLAST database for species A (query species).
#     -b, --species_B_db: Name of the BLAST database for species B (target species).
#     -o, --output_directory: Path to the directory where output files will be saved.
#     -e, --evalue: (Optional) E-value threshold for BLAST searches. Default is 1e-3.
#
# Requirements:
#     - BLAST+ suite installed and accessible in the PATH.
#     - BLASTDB environment variable set to the directory containing BLAST databases.
#########################################################################################################

# Default E-value threshold
EVALUE="1e-3"

#########################################################################################################
# PROGRAM ARGUMENTS
#########################################################################################################

# Usage function to display help for the needy
usage() {
  echo "Usage: $0 -q query_fasta -a species_A_db -b species_B_db -o output_directory [-e evalue]"
  exit 1
}

# Parse command-line arguments
while getopts ":q:a:b:o:e:" opt; do
  case $opt in
    q) QUERY="$OPTARG"
    ;;
    a) SPECIES_A_DB="$OPTARG"
    ;;
    b) SPECIES_B_DB="$OPTARG"
    ;;
    o) OUT_DIR="$OPTARG"
    ;;
    e) EVALUE="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
        usage
    ;;
    :) echo "Option -$OPTARG requires an argument." >&2
       usage
    ;;
  esac
done

# Check if all mandatory arguments are provided
if [ -z "$QUERY" ] || [ -z "$SPECIES_A_DB" ] || [ -z "$SPECIES_B_DB" ] || [ -z "$OUT_DIR" ]; then
  usage
fi

# Check if BLASTDB environment variable is set
if [ -z "$BLASTDB" ]; then
  echo "Error: BLASTDB environment variable is not set. Please set it to the directory containing your BLAST databases."
  exit 1
fi

# Create output directory if it doesn't exist
mkdir -p $OUT_DIR

#########################################################################################################
# FUNCTIONS
#########################################################################################################

# Function to check if a file is not empty
check_file_not_empty() {
  if [ ! -s "$1" ]; then
    echo "Error: $2"
    exit 1
  fi
}

#########################################################################################################
# PROCESS DATA
#########################################################################################################

# Intermediate and final result files
TEMP_HITS="${OUT_DIR}/temp_hits.fasta"
FINAL_RESULTS="${OUT_DIR}/final_reciprocal_hits.txt"

# Check if databases exist
if [ ! -e "${BLASTDB}/${SPECIES_A_DB}.pin" ] || [ ! -e "${BLASTDB}/${SPECIES_B_DB}.pin" ]; then
  echo "Error: One or both of the specified BLAST databases do not exist in the BLASTDB directory."
  exit 1
fi

#--------------------------------------------------------------------------------------------------------
# Step 1: BLASTP - Query species A against species B database
#--------------------------------------------------------------------------------------------------------

blastp -query $QUERY -db $SPECIES_B_DB -evalue $EVALUE \
       -out ${OUT_DIR}/initial_blastp.out -outfmt 6  -max_target_seqs 1

# Check if BLASTP found any hits
check_file_not_empty "${OUT_DIR}/initial_blastp.out" "No hits found for the query against species B database."

#--------------------------------------------------------------------------------------------------------
# Step 2: Extract top hit sequences
#--------------------------------------------------------------------------------------------------------

awk '!seen[$1]++' ${OUT_DIR}/initial_blastp.out | awk '{print $2}' > ${OUT_DIR}/top_hits.txt

# Check if top hits file is not empty
check_file_not_empty "${OUT_DIR}/top_hits.txt" "No top hits found to extract."

#--------------------------------------------------------------------------------------------------------
# Step 3: Retrieve sequences of top hits from species B database
#--------------------------------------------------------------------------------------------------------

blastdbcmd -db $SPECIES_B_DB -entry_batch ${OUT_DIR}/top_hits.txt -out $TEMP_HITS

# Check if temp hits file is not empty
check_file_not_empty "$TEMP_HITS" "No sequences retrieved for top hits."

#--------------------------------------------------------------------------------------------------------
# Step 4: BLASTP - Top hits against species A database
#--------------------------------------------------------------------------------------------------------

blastp -query $TEMP_HITS -db $SPECIES_A_DB -evalue $EVALUE \
       -out ${OUT_DIR}/reciprocal_blastp.out -outfmt 6  -max_target_seqs 1 

# Check if reciprocal BLASTP found any hits
check_file_not_empty "${OUT_DIR}/reciprocal_blastp.out" "No reciprocal hits found against species A database."

#--------------------------------------------------------------------------------------------------------
# Step 5: Identify reciprocal best hits
#--------------------------------------------------------------------------------------------------------

awk '{print $1"\t"$2}' ${OUT_DIR}/reciprocal_blastp.out > $FINAL_RESULTS

# Check if final results file is not empty
check_file_not_empty "$FINAL_RESULTS" "No reciprocal best hits identified."

#########################################################################################################
# CLEANUP
#########################################################################################################

# Clean up temporary files
rm $TEMP_HITS

# Completion message
echo "Reciprocal BLAST completed. Results are in $FINAL_RESULTS"
