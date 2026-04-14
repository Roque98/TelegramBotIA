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

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode="before")
    @classmethod
    def _coerce_nulls(cls, data: Any) -> Any:
        """Coerciona NULLs de BD a defaults — evita descartar filas con campos opcionales nulos."""
        if not isinstance(data, dict):
            return data
        _str_fields = {
            "Equipo", "IP", "Sensor", "Status", "Mensaje",
            "AreaAtendedora", "ResponsableAtendedor",
            "AreaAdministradora", "ResponsableAdministrador", "_origen",
        }
        for field in _str_fields:
            if data.get(field) is None:
                data[field] = ""
        if data.get("Prioridad") is None:
            data["Prioridad"] = 0
        return data

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

    @model_validator(mode="before")
    @classmethod
    def _coerce_nulls(cls, data: Any) -> Any:
        """Convierte NULL de BD a string vacío para evitar ValidationError en campos str."""
        if not isinstance(data, dict):
            return data
        for field in ("alerta", "detalle", "accionCorrectiva"):
            if data.get(field) is None:
                data[field] = ""
        return data

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

    # Campos adicionales de Template_GetById
    atendedor_id_gerencia: Optional[int] = Field(alias="Atendedor_idGerencia", default=None)
    gerencia_atendedora: str = Field(alias="GerenciaAtendedora", default="")
    id_gerencia_desarrollo: Optional[int] = Field(alias="idGerenciaDesarrollo", default=None)
    ambiente: str = Field(alias="ambiente", default="")
    negocio: str = Field(alias="Negocio", default="")
    tipo_template: str = Field(alias="TipoTemplate", default="")
    es_aws: bool = Field(alias="esAws", default=False)
    es_vertical: bool = Field(alias="esVertical", default=False)

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _coerce_types(cls, data: Any) -> Any:
        """Coerciona valores de BD: None → default, int → str para campos str."""
        if not isinstance(data, dict):
            return data
        for field in ("Aplicacion", "GerenciaDesarrollo", "GerenciaAtendedora",
                      "ambiente", "Negocio", "TipoTemplate"):
            v = data.get(field)
            if v is None:
                data[field] = ""
            elif not isinstance(v, str):
                data[field] = str(v)
        for field in ("esAws", "esVertical", "ArquitecturaPersonalizada"):
            if data.get(field) is None:
                data[field] = False
        return data

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

    @model_validator(mode="before")
    @classmethod
    def _coerce_types(cls, data: Any) -> Any:
        """Coerciona tipos de BD: TiempoEscalacion llega como int, campos str pueden ser None."""
        if not isinstance(data, dict):
            return data
        # TiempoEscalacion viene como int desde la BD
        if "TiempoEscalacion" in data and not isinstance(data["TiempoEscalacion"], str):
            data["TiempoEscalacion"] = str(data["TiempoEscalacion"]) if data["TiempoEscalacion"] is not None else ""
        # Campos str que pueden venir como None
        for field in ("Nombre", "puesto", "Extension", "celular", "correo"):
            if data.get(field) is None:
                data[field] = ""
        return data


class AreaContacto(BaseModel):
    """Datos de contacto de una gerencia."""

    gerencia: str = Field(alias="Gerencia", default="")
    correos: str = Field(alias="direccion_correo", default="")
    extensiones: str = Field(alias="extensiones", default="")
    responsable: str = Field(alias="RESPONSABLE", default="")

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _coerce_nulls(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        for field in ("Gerencia", "direccion_correo", "extensiones", "RESPONSABLE"):
            if data.get(field) is None:
                data[field] = ""
        return data


class InventoryItem(BaseModel):
    """
    Equipo del inventario obtenido por IP.

    Unifica EquiposFisicos y MaquinasVirtuales en un modelo común.
    El campo 'fuente' indica la tabla de origen: 'Fisico' | 'Virtual'.
    """

    ip: str = Field(alias="ip", default="")
    hostname: str = Field(alias="hostname", default="")
    id_area_atendedora: Optional[int] = Field(alias="id_area_atendedora", default=None)
    id_area_administradora: Optional[int] = Field(alias="id_area_administradora", default=None)
    area_atendedora: str = Field(alias="area_atendedora", default="")
    area_administradora: str = Field(alias="area_administradora", default="")
    fuente: str = Field(alias="fuente", default="")           # "Fisico" | "Virtual"
    tipo_equipo: str = Field(alias="tipo_equipo", default="") # solo EquiposFisicos
    version_os: str = Field(alias="version_os", default="")
    status: str = Field(alias="status", default="")
    capa: str = Field(alias="capa", default="")
    ambiente: str = Field(alias="ambiente", default="")
    impacto: str = Field(alias="impacto", default="")
    urgencia: str = Field(alias="urgencia", default="")
    prioridad: str = Field(alias="prioridad", default="")
    negocio: str = Field(alias="negocio", default="")         # solo EquiposFisicos
    grupo_correo: str = Field(alias="grupo_correo", default="")  # solo EquiposFisicos

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _coerce_nulls(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        for field in (
            "ip", "hostname", "area_atendedora", "area_administradora",
            "fuente", "tipo_equipo", "version_os", "status",
            "capa", "ambiente", "impacto", "urgencia", "prioridad",
            "negocio", "grupo_correo",
        ):
            v = data.get(field)
            if v is None:
                data[field] = ""
            elif not isinstance(v, str):
                data[field] = str(v)
        return data


class HistoricalAlertEvent(BaseModel):
    """Evento resuelto de monitoreo PRTG desde EventosPRTG_Historico."""

    equipo: str = Field(alias="Equipo", default="")
    ip: str = Field(alias="IP", default="")
    sensor: str = Field(alias="Sensor", default="")
    status: str = Field(alias="Status", default="")
    mensaje: str = Field(alias="Mensaje", default="")
    fecha_insercion: Optional[datetime] = Field(alias="fechaInsercion", default=None)
    fecha_resolucion: Optional[datetime] = Field(alias="fechaResolucion", default=None)

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _coerce_nulls(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        for field in ("Equipo", "IP", "Sensor", "Status", "Mensaje"):
            if data.get(field) is None:
                data[field] = ""
        return data

    @property
    def fecha_resolucion_str(self) -> str:
        if self.fecha_resolucion:
            return self.fecha_resolucion.strftime("%Y-%m-%d %H:%M")
        if self.fecha_insercion:
            return self.fecha_insercion.strftime("%Y-%m-%d %H:%M")
        return "fecha desconocida"


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
