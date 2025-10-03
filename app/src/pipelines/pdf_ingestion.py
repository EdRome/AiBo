import pypdf
import os

def pdf_as_markdown(pdf_path, path_markdown_output):
    try:
        with open(pdf_path, "rb") as file:
            lector_pdf = pypdf.PdfReader(file)

            texto_completo = ""

            for numero_pagina in range(len(lector_pdf.pages)):
                pagina = lector_pdf.pages[numero_pagina]
                texto_pagina = pagina.extract_text()

                texto_completo += f"\n\n# Página {numero_pagina + 1}\n\n"
                texto_completo += texto_pagina

        texto_limpio = os.linesep.join([s for s in texto_completo.splitlines() if s])

        with open(path_markdown_output, "w", encoding="utf-8") as file:
            file.write(texto_limpio)

        print(f"Éxito. Texto extraído y guardado en {path_markdown_output}")

    except FileNotFoundError:
        print(f"Error. El archivo {pdf_path} no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento del PDF: {e}")

nombre_pdf = r"C:\Users\eduar\Documents\startup\MVP\AiBo\app\docs\RMF2025\2aRM_RMF_2025-07042025-DOF.pdf"
nombre_markdown = r"C:\Users\eduar\Documents\startup\MVP\AiBo\app\docs\RMF2025\2aRM_RMF_2025-07042025-DOF.md"

pdf_as_markdown(nombre_pdf, nombre_markdown)