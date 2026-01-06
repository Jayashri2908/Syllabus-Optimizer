"""
Quick fix script to remove duplicate export endpoints from main.py
"""

file_path = r"D:\Syllabus Optimizer\webapp\backend\main.py"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the duplicate section and remove it
# We want to keep lines 1-533, and then add the if __name__ block
# Remove lines 536-586 (the duplicate export endpoints)

new_lines = []
skip_mode = False

for i, line in enumerate(lines, 1):
    # Start skipping at line 536 (# Export Endpoints comment)
    if i == 536:
        skip_mode = True
    # Stop skipping at line 589 (if __name__)
    elif i == 589:
        skip_mode = False
    
    if not skip_mode:
        new_lines.append(line)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Fixed! Removed duplicate export endpoints (lines 536-588)")
print(f"   File now has {len(new_lines)} lines instead of {len(lines)}")
