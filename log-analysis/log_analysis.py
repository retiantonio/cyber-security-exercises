import subprocess
import csv
import re
import datetime

from collections import defaultdict

output_csv ="logs_monitoring.csv"

result = subprocess.run(["journalctl", "-u", "ssh"],
                        capture_output = True,
                        text = True)

logs = result.stdout.splitlines() #all the logs

date_re = re.compile(r"^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})")

ip_pattern = re.compile(
    r'(?:(?<=from\s)|(?<=rhost=))'
    r'('
    r'(?:\b(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
    r'(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}\b)'
    r'|'
    r'(?:\b[0-9a-fA-F:]+:+[0-9a-fA-F]+\b)'
    r')'
)

data = defaultdict(lambda: {"count": 0, "first": None, "last": None})

for line in logs:
    date_match = date_re.search(line)
    ip_match = ip_pattern.search(line)

    if not(date_match and ip_match):
        continue

    date_str = date_match.group(1)
    ip = ip_match.group(1)

    try:
        date = datetime.datetime.strptime(f"{datetime.datetime.now().year} {date_str}", "%Y %b %d %H:%M:%S")
    except ValueError:
        continue

    info = data[ip]
    info["count"] += 1
    if info["first"] is None or date < info["first"]:
        info["first"] = date
    if info["last"] is None or date > info["last"]:
        info["last"] = date

with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["IP", "Count", "First_Seen", "Last_Seen"])
    for ip, info in sorted(data.items(), key=lambda x: x[1]["count"]):
        writer.writerow([
            ip,
            info["count"],
            info["first"].strftime("%Y-%m-%d %H:%M:%S") if info["first"] else "",
            info["last"].strftime("%Y-%m-%d %H:%M:%S") if info["last"] else "",
        ])

print(f"Saved {len(data)} IP entries to {output_csv}")