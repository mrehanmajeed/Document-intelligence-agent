import fitz
import easyocr
import numpy as np

# Initialize EasyOCR reader lazily to save startup time
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader

def extract_text(file_data):
    text = []

    try:
        with fitz.open("pdf", file_data) as doc:
            for page in doc:
                page_text = page.get_text()
                if page_text.strip():
                    text.append(page_text)
                else:
                    # Fallback to OCR if no text found on page
                    pix = page.get_pixmap()
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    
                    reader = get_reader()
                    ocr_result = reader.readtext(img, detail=0)
                    text.append("\n".join(ocr_result))

        return "\n".join(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""