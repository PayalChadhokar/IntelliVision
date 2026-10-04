import easyocr

# Load OCR model only once when Flask starts
reader = easyocr.Reader(["en"], gpu=False)


def extract_text(image_path):

    results = reader.readtext(image_path)

    extracted_lines = []

    for result in results:
        text = result[1]
        extracted_lines.append(text)

    return "\n".join(extracted_lines)