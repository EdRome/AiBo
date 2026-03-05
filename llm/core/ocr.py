import os
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import MODEL_GEMINI_FLASH, OCR_TEMPERATURE, OCR_THINKING_BUDGET
from llm.prompt.ocr import EXTRAER_DATOS_VENTA
from llm.prompt.utils import INSTRUCCION_IDIOMA, CONTEXTO_ASISTENTE
from data.models.venta.RegistroVenta import BatchVentas

model = ChatGoogleGenerativeAI(
    model=MODEL_GEMINI_FLASH,
    temperature=OCR_TEMPERATURE,
    thinking_budget=OCR_THINKING_BUDGET,
    api_key=os.environ.get("GEMINI_API_KEY")
)

def ocr_v1(image: bytes):
    image_base64 = base64.b64encode(image).decode("utf-8")
    ocr = model.with_structured_output(BatchVentas)

    prompt_texto = INSTRUCCION_IDIOMA + CONTEXTO_ASISTENTE + EXTRAER_DATOS_VENTA
    
    mensaje = HumanMessage(
        content=[
            {"type": "text", "text": prompt_texto},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            },
        ]
    )

    response = ocr.invoke([mensaje])
    return response