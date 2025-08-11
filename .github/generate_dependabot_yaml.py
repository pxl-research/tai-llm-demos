import os
import os.path

# Root directory for your repo
REPO_ROOT = "../"

# Output file
OUTPUT_FILE = "dependabot_new.yml"

dependabot_config = """
version: 2
defaults: &defaults
  package-ecosystem: pip
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

updates:
"""

# Walk through all directories and find 'requirements.txt'
for root, dirs, files in os.walk(REPO_ROOT):
    if "requirements.txt" in files:
        relative_path = os.path.relpath(root, REPO_ROOT)
        print(relative_path)
        dependabot_config += f"""
  - directory: "/{relative_path}"
    <<: *defaults
"""

# Save the configuration
with open(OUTPUT_FILE, "wt") as f:
    f.write(dependabot_config)

print(f"Generated {OUTPUT_FILE}")
