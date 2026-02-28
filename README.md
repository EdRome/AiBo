# AiBo

Asistente de registro de venta, gasto e inventario a través de un chatbot en WhatsApp.

## 🚀 Características

- **Chatbot de WhatsApp**: Flujo conversacional 

## 📁 Estructura del Proyecto

```
AiBo/
├── cloud_task/
│   ├── __init__.py
│   └── cloud_task.py
├── config/
│   ├── __init__.py
│   └── config.py
├── data/
│   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   ├── managers.py
│   │   ├── memory.py
│   │   ├── messages.py
│   │   ├── sales.py
│   │   └── utils.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── etapa1/
│   │   │   ├── __init__.py
│   │   │   └── negocio.py
│   │   ├── etapa2/ # Obsoleta
│   │   │   ├── __init__.py
│   │   │   ├── channels.py
│   │   │   └── needs.py
│   │   ├── etapa3/ # Obsoleta
│   │   │   ├── __init__.py
│   │   │   └── pain_point.py
│   │   ├── etapa4/ # Obsoleta
│   │   │   ├── __init__.py
│   │   │   └── pain_point_summary.py
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   └── memory.py
│   │   ├── menu/
│   │   │   ├── __init__.py
│   │   │   ├── ventas.py
│   │   │   └── inventario.py
│   │   ├── sqlalchemy/
│   │   │   ├── __init__.py
│   │   │   ├── ventas.py
│   │   │   └── inventario.py
│   │   ├── venta/
│   │   │   ├── __init__.py
│   │   │   ├── DetalleVenta.py
│   │   │   ├── RegistroVenta.py
│   │   │   └── SalesSummary.py
│   ├── sql_esquemas/
│   │   ├── inventario.py
│   │   └── ventas.py
├── llm/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── entity_extractor.py
│   │   ├── phrase_analyzer.py
│   │   ├── summary_creator.py
│   │   └── sales_extractor.py
│   ├── prompt/
│   │   ├── __init__.py
│   │   ├── entity_extractor.py
│   │   ├── phrase_analyzer.py
│   │   ├── sales_extractor.py
│   │   ├── summary_creator.py
│   │   └── utils.py
├── state_machines/
│   ├── Menu/
│   │   ├── __init__.py
│   │   ├── Inventory.py
│   │   ├── Menu.py
│   │   └── Sales.py
│   ├── Onboarding/
│   │   ├── __init__.py
│   │   ├── executor.py
│   │   └── utils.py
│   ├── __init__.py
│   ├── executor.py
│   └── utils.py
├── whatsapp/
│   ├── messages/
│   │   ├── __init__.py
│   │   ├── messages_en.json
│   │   ├── messages_es.json
│   │   └── multiidioma.py
│   ├── send_message/
│   │   └── send_message.py
│   ├── __init__.py
├── app.py
├── Dockerfile
├── requirements.txt
└── README.md