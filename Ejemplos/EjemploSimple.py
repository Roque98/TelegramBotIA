import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Modelo
modelo = os.getenv("OPENAI_MODEL", "gpt-5-nano-2025-08-07")

# Inicializar cliente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from openai import OpenAI
client = OpenAI()

# Hacer una petición
response = client.responses.create(
    model=modelo,
    input="Hola, ¿cómo estás?"
)

print(response.output_text)
print(response)