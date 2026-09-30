"""Test PyMuPDF + EasyOCR pipeline on ML.pdf"""
import pymupdf
import easyocr
import numpy as np
import time

print("=" * 60)
print("Testing PyMuPDF + EasyOCR on ML.pdf")
print("=" * 60)

start = time.time()

# Step 1: Render PDF page to image using PyMuPDF (no Poppler needed!)
doc = pymupdf.open("uploads/ML.pdf")
print(f"\nPDF has {len(doc)} pages")

# Initialize EasyOCR (first run downloads ~100MB model)
print("\nInitializing EasyOCR (first run downloads model)...")
reader = easyocr.Reader(["en"], gpu=False)  # CPU mode

full_text = ""
for i, page in enumerate(doc):
    print(f"\nProcessing page {i+1}...")
    
    # Render page at 300 DPI for quality OCR
    pix = page.get_pixmap(dpi=300)
    
    # Convert to numpy array for EasyOCR
    img_data = pix.samples
    img = np.frombuffer(img_data, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    
    # Run OCR
    results = reader.readtext(img, detail=0, paragraph=True)
    page_text = "\n".join(results)
    full_text += page_text + "\n\n"
    
    print(f"  Page {i+1}: extracted {len(page_text)} chars")
    print(f"  Preview: {page_text[:200]}...")

elapsed = time.time() - start
print(f"\n{'=' * 60}")
print(f"Total extracted: {len(full_text)} chars in {elapsed:.1f}s")
print(f"{'=' * 60}")
print(f"\nFull text preview (first 1000 chars):\n")
print(full_text[:1000])
