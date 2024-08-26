from PyPDF2 import PdfMerger

def merger_pdf(pdf_files):

    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open("merger_output.pdf", "wb") as output_pdf:
        merger.write(output_pdf)

    merger.close()
    return output_pdf