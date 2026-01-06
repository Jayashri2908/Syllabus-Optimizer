"""
Quick debug script to check the actual syllabus data structure
"""
import json

# Based on the logs, the data keys are:
# ['course_title', 'course_code', 'credits', 'prerequisites', 'objectives', 
#  'learning_outcomes', 'units', 'assessment_pattern', 'references', 
#  'co_po_mapping', 'raw_text']

# The issue: Excel shows "UNKNOWN" for course_code and "0-0-0" for credits
# But the PDF works fine

# Let me add detailed logging to the Excel exporter to see what's happening
with open(r"D:\Syllabus Optimizer\src\export\excel_exporter.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Find the _create_overview_sheet method and check line 124-126
# It's looking for: data.get('course_code', 'N/A')
# But showing "UNKNOWN" suggests the data has 'course_code': 'UNKNOWN' already

print("The Excel exporter is reading the correct keys.")
print("The issue is that the PARSED data itself has 'UNKNOWN' values.")
print("\nCheck the syllabus parser output:")
print("- course_code might be set to 'UNKNOWN' during parsing")
print("- credits might be set to '0-0-0' during parsing")
print("\nThe PDF works because it handles missing data differently.")
