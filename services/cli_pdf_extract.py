"""Command-line bridge for PDF text extraction via PyMuPDF."""

import sys
import os
import json
import base64
import warnings

# Suppress deprecation warnings from libraries to ensure clean JSON output
warnings.filterwarnings("ignore")

# Ensure app root is on python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_service import extract_text_from_pdf_bytes

def main():
    try:
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
            with open(filepath, "rb") as f:
                pdf_bytes = f.read()
            filename = filepath.split("/")[-1]
        else:
            raw_input = sys.stdin.read().strip()
            if not raw_input:
                print(json.dumps({"success": False, "message": "No data provided."}))
                return
            payload = json.loads(raw_input)
            b64_data = payload.get("base64", "")
            filename = payload.get("filename", "uploaded_doc.pdf")
            pdf_bytes = base64.b64decode(b64_data)

        result = extract_text_from_pdf_bytes(pdf_bytes, filename)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "message": f"Extraction error: {str(e)}"}))

if __name__ == "__main__":
    main()
