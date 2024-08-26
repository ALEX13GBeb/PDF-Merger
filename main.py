import os
from merge import merger_pdf

pdf_files=[path for path in os.listdir() if path.endswith(".pdf")]

merger_pdf(pdf_files)

print(f"Succesfully merged {len(pdf_files)} pdfs into output_pdf")
