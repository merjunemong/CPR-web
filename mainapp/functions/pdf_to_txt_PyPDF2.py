import PyPDF2

def pdf_to_text(filePath):
    with open(filePath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page = reader.pages[0]
        text = page.extract_text()
        text.replace("\n", " ")
        return text
