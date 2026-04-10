"""
Alert Entities — Modelos Pydantic para el dominio de alertas PRTG.

Jerarquía:
  AlertEvent        — Evento activo de PRTG (una fila de PrtgObtenerEventosEnriquecidos)
  HistoricalTicket  — Ticket histórico de un evento similar
  Template          — Template de la aplicación afectada
  EscalationLevel   — Un nivel de la matriz de escalamiento
  AreaContacto      — Datos de contacto de una gerencia
  AlertContext      — Agregado completo de un evento enriquecido (se pasa al PromptBuilder)
"""

from typing import Optional

from pydantic import BaseModel, Field


class AlertEvent(BaseModel):
    """Evento activo de monitoreo PRTG."""

    equipo: str = Field(alias="Equipo", default="")
    ip: str = Field(alias="IP", default="")
    sensor: str = Field(alias="Sensor", default="")
    status: str = Field(alias="Status", default="")
    mensaje: str = Field(alias="Mensaje", default="")
    prioridad: int = Field(alias="Prioridad", default=0)

    id_area_atendedora: Optional[int] = Field(alias="idAreaAtendedora", default=None)
    id_area_administradora: Optional[int] = Field(alias="idAreaAdministradora", default=None)
    area_atendedora: str = Field(alias="AreaAtendedora", default="")
    responsable_atendedor: str = Field(alias="ResponsableAtendedor", default="")
    area_administradora: str = Field(alias="AreaAdministradora", default="")
    responsable_administrador: str = Field(alias="ResponsableAdministrador", default="")

    # Marcador interno: "BAZ_CDMX" o "EKT" — indica de qué instancia vino
    origen: str = Field(alias="_origen", default="BAZ_CDMX")

    model_config = {"populate_by_name": True}

    @property
    def es_ekt(self) -> bool:
        return self.origen == "EKT"

    @property
    def es_url_sensor(self) -> bool:
        return self.sensor.startswith("http")


class HistoricalTicket(BaseModel):
    """Ticket histórico de un evento similar al activo."""

    ticket: Optional[str] = Field(alias="Ticket", default=None)
    alerta: str = Field(alias="alerta", default="")
    detalle: str = Field(alias="detalle", default="")
    accion_correctiva: str = Field(alias="accionCorrectiva", default="")

    model_config = {"populate_by_name": True}

    @property
    def accion_formateada(self) -> str:
        """Reemplaza el marcador [Salto] de la BD por saltos de línea reales."""
        return self.accion_correctiva.replace("[Salto]", "\n")


class Template(BaseModel):
    """Template de la aplicación asociada al evento."""

    id_template: Optional[int] = Field(alias="idTemplate", default=None)
    aplicacion: str = Field(alias="Aplicacion", default="")
    gerencia_desarrollo: str = Field(alias="GerenciaDesarrollo", default="")
    instancia: str = Field(default="")  # "BAZ", "COMERCIO" o vacío

    model_config = {"populate_by_name": True}

    @property
    def etiqueta(self) -> str:
        """Etiqueta legible para el prompt según la instancia."""
        if self.instancia.upper() == "COMERCIO":
            return "ABCEKT"
        return "ABCMASplus"

    @property
    def es_ekt(self) -> bool:
        return self.instancia.upper() == "COMERCIO"


class EscalationLevel(BaseModel):
    """Un nivel de la matriz de escalamiento del template."""

    nivel: int = Field(alias="nivel", default=1)
    nombre: str = Field(alias="Nombre", default="")
    puesto: str = Field(alias="puesto", default="")
    extension: str = Field(alias="Extension", default="")
    celular: str = Field(alias="celular", default="")
    correo: str = Field(alias="correo", default="")
    tiempo_escalacion: str = Field(alias="TiempoEscalacion", default="")

    model_config = {"populate_by_name": True}


class AreaContacto(BaseModel):
    """Datos de contacto de una gerencia."""

    gerencia: str = Field(alias="Gerencia", default="")
    correos: str = Field(alias="direccion_correo", default="")
    extensiones: str = Field(alias="extensiones", default="")

    model_config = {"populate_by_name": True}


class AlertContext(BaseModel):
    """
    Contexto completo de un evento de alerta, enriquecido con todos los datos
    necesarios para construir el prompt de análisis.
    """

    evento: AlertEvent
    tickets: list[HistoricalTicket] = Field(default_factory=list)
    template: Optional[Template] = None
    matriz: list[EscalationLevel] = Field(default_factory=list)
    contacto_atendedora: Optional[AreaContacto] = None
    contacto_administradora: Optional[AreaContacto] = None
    query_usuario: str = ""
