
import sys
import os
try:
    from docx import Document
except ImportError:
    print("python-docx not installed")
    sys.exit(1)

def read_docx(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    doc = Document(path)
    print(f"--- START OF DOCUMENT: {path} ---")
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    
    print("\n".join(full_text))
    print("--- END OF DOCUMENT ---")

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        read_docx(args[0])
    else:
        # Default to root file if exists, else docs
        if os.path.exists("Project Report_final.docx"):
            read_docx("Project Report_final.docx")
        else:
             read_docx("d:\\Syllabus Optimizer\\docs\\Project Report_final.docx")
