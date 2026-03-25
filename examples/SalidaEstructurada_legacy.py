import os
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Modelo
modelo = os.getenv("OPENAI_MODEL", "gpt-5-nano-2025-08-07")

# Inicializar cliente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Definir la clase Rectangulo con Pydantic para salida estructurada
class Rectangulo(BaseModel):
    base: float = Field(description="Longitud de la base del rectángulo en metros. Valor por default: 5")
    altura: float = Field(description="Longitud de la altura del rectángulo en metros. Valor por default: 5")
    color: str = Field(description="Color del rectángulo. Valor por default: rojo")
    ubicacion: str = Field(description="Lugar donde se encuentra el rectángulo. Valor por default: Desconocido")


# Hacer una petición con salida estructurada
response = client.responses.parse(
    model= modelo,
    input=[
        {"role": "system", "content": "Extrae la información del rectángulo del texto proporcionado."},
        {
            "role": "user",
            "content": "Tenemos un rectángulo azul y rojo",
        },
    ],
    text_format=Rectangulo,
)

# Obtener el objeto parseado
rectangulo = response.output_parsed

# Mostrar los datos estructurados
print("=== Datos del Rectángulo (Salida Estructurada) ===")
print(f"Base: {rectangulo.base} metros")
print(f"Altura: {rectangulo.altura} metros")
print(f"Color: {rectangulo.color}")
print(f"Ubicación: {rectangulo.ubicacion}")
print(f"\nÁrea del rectángulo: {rectangulo.base * rectangulo.altura} m²")
print(f"Perímetro del rectángulo: {2 * (rectangulo.base + rectangulo.altura)} m")

# Mostrar el objeto completo
print(f"\nObjeto completo: {rectangulo}")