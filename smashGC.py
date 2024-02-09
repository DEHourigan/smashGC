#!/usr/bin/env python3
import os
import csv
import sys
import argparse
from Bio import SeqIO
from Bio.SeqUtils import GC
from Bio.SeqUtils import gc_fraction


def process_genbank_file(directory, gbkfile_name, start_region, end_region, locus, assembly):
    """
    Process a GenBank file to calculate average GC content and GC content within a specific window.
    
    :param directory: Path to the directory containing GenBank files.
    :param gbkfile_name: Name of the GenBank file.
    :param start_region: Start index of the window for GC calculation.
    :param end_region: End index of the window for GC calculation.
    :param locus: The locus identifier to match.
    :param assembly: The assembly identifier for the record.
    :return: List of dictionaries with the results.
    """
    genbank_file = os.path.join(directory, gbkfile_name)
    try:
        records = list(SeqIO.parse(genbank_file, "genbank"))
    except Exception as e:
        print(f"Error reading {genbank_file}: {e}")
        return []
    
    return [
        {
            "assembly": assembly,
            "nucleotide_accession": record.id,
            "file": gbkfile_name,
            "avg_GC_content": gc_fraction(record.seq),
			"avg_GC_window": gc_fraction(record.seq[start_region:end_region]),
            "window_start": start_region,
            "window_end": end_region,
            "product": None  # Placeholder for product column, if needed.
        }
        for record in records if record.id == locus
    ]

def main():
    parser = argparse.ArgumentParser(description="Calculate GC content for specific regions in GenBank files.")
    parser.add_argument('--input_folder', type=str, required=True, help='Path to the directory containing GenBank files.')
    parser.add_argument('--table', type=str, required=True, help='Path to the antismash table (TSV format).')

    args = parser.parse_args()

    directory = args.input_folder
    table_file = args.table

    all_results = []

    try:
        with open(table_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                filename = row.get('filename')  # Use .get() to safely handle missing 'filename' keys
                if not filename:  # Check if filename is None or empty
                    identifying_info = row.get('assembly', 'Unknown assembly')  # Adjust key as appropriate
                    print(f"Warning: Missing 'filename' in row with assembly: {identifying_info}. Skipping...")
                    continue  # Skip this row

                results = process_genbank_file(
                    directory,
                    os.path.basename(filename),  # Safe to use filename here as it's checked to be not None/empty
                    int(row['orig_start']),
                    int(row['orig_end']),
                    row['locus'],
                    row['assembly']
                )
                all_results.extend(results)
    except Exception as e:
        print(f"Error processing table file {table_file}: {e}")
        sys.exit(2)

    # Writing results to CSV
    output_file = "gc_content_table.csv"
    headers = ["assembly", "nucleotide_accession", "file", "avg_GC_content", "avg_GC_window", "window_start", "window_end", "product"]
    try:
        with open(output_file, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Table saved as {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    main()
