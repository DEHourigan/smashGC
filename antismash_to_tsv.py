import os
import re
from Bio import SeqIO
import argparse

def extract_data_from_gbk(gbk_file):
    with open(gbk_file, "r") as handle:
        content = handle.read()
        
        orig_start_match = re.search(r"Orig\. start\s*::\s*(\d+)", content)
        orig_end_match = re.search(r"Orig\. end\s*::\s*(\d+)", content)
        orig_start = orig_start_match.group(1) if orig_start_match else None
        orig_end = orig_end_match.group(1) if orig_end_match else None

        handle.seek(0)  # Reset the file cursor to the beginning

        for record in SeqIO.parse(handle, "genbank"):
            locus = record.name
            product = category = detection_rule = None
            for feature in record.features:
                if feature.type == "region":
                    product = feature.qualifiers.get("product", [""])[0]
                    category = feature.qualifiers.get("category", [""])[0]
                    detection_rule = feature.qualifiers.get("rules", [""])[0]

            if not orig_start or not orig_end:
                print(f"Missing start/end data in {gbk_file}")

            return [product, category, detection_rule, gbk_file, locus, orig_start, orig_end]

def main(input_dir, output_file):
    with open(output_file, "w") as out:
        out.write("product\tcategory\tdetection_rule\tassembly\tfilename\tlocus\torig_start\torig_end\n")
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if "region" in file and file.endswith(".gbk"):
                    full_path = os.path.join(root, file)
                    assembly = os.path.basename(root)  # Extract the assembly name
                    print(f"Processing {full_path}")  # Debugging line
                    data = extract_data_from_gbk(full_path)
                    if data:
                        # Convert all data elements to strings and replace None with an empty string
                        data_str = [str(item) if item is not None else "" for item in data[:3] + [assembly] + data[3:]]
                        out.write("\t".join(data_str) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract data from GenBank files and write to a TSV.")
    parser.add_argument("--input-dir", required=True, help="Directory containing the GenBank files.")
    parser.add_argument("--tsvout", required=True, help="Path to the output TSV file.")
    args = parser.parse_args()
    main(args.input_dir, args.tsvout)
