import json
from pathlib import Path
import hashlib
import fnmatch
import zipfile
import os
import sys

def get_md5(file_name: str):
    hash_md5 = hashlib.md5()
    
    with open(file_name, "rb") as fin:
        while len(chunk := fin.read(512)) > 0:
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()


with open("./02_Fisiere_si_hashuri/script_input.json", "r") as fin:
    data = json.load(fin)

suspicious_file_names = data.get("file_patterns", [])
suspicious_md5_hashes = data.get("md5_hashes", [])

results = {
        "name_matches" : {pattern : [] for pattern in suspicious_file_names},
        "md5_matches" : {hash: [] for hash in suspicious_md5_hashes}
        }

for root, dirs, files in Path(sys.argv[1]).walk():
    for file in files:
        filePath = Path(root) / file
        md5File = get_md5(filePath)
        if md5File in suspicious_md5_hashes:
            results["md5_matches"][md5File].append(str(filePath))
            continue
        
        for pattern in suspicious_file_names:
            if fnmatch.fnmatch(file.lower(), pattern.lower()):
                results["name_matches"][pattern].append(str(filePath))

output_json = "scan_results.json"
with open(output_json, "w") as f:
    json.dump(results, f, indent = 4)

