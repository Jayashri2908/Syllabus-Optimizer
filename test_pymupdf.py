import fitz  # PyMuPDF

doc = fitz.open("uploads/ML.pdf")
print(f"Pages: {len(doc)}")
for i, page in enumerate(doc):
    text = page.get_text()
    print(f"  Page {i+1}: {len(text)} chars")
    if text.strip():
        print(f"  Preview: {text[:300]}")
    else:
        print("  No text found by PyMuPDF either")
    blocks = page.get_text("dict")
    block_list = blocks.get("blocks", [])
    print(f"  Blocks: {len(block_list)}")
    for b in block_list[:3]:
        btype = b.get("type", "?")
        print(f"    Block type: {btype} (0=text, 1=image)")
doc.close()

# Now test rendering page to image for OCR alternative
page = fitz.open("uploads/ML.pdf")[0]
pix = page.get_pixmap(dpi=300)
pix.save("uploads/test_page1.png")
print(f"\nRendered page 1 to image: {pix.width}x{pix.height} pixels")
print("This image could be fed to an OCR engine without needing Poppler!")
