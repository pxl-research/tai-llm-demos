import os
import os.path

# Root directory for your repo
REPO_ROOT = "../"

# Output file
OUTPUT_FILE = "dependabot_new.yml"

dependabot_config = """
version: 2
updates:
"""

# Walk through all directories and find 'requirements.txt'
for root, dirs, files in os.walk(REPO_ROOT):
    if "requirements.txt" in files:
        relative_path = os.path.relpath(root, REPO_ROOT)
        dependabot_config += f"""
  - package-ecosystem: pip
    directory: "/{relative_path}"
    schedule:
      interval: daily
      time: "04:00"
    groups:
      python-packages:
        patterns:
          - "*"
    pull-request-branch-name:
      separator: "-"
    labels:
      - "dependencies"
      - "python"
    reviewers:
      - "stilkin-pxl"
"""

# Save the configuration
with open(OUTPUT_FILE, "w") as f:
    f.write(dependabot_config)

print(f"Generated {OUTPUT_FILE}")
