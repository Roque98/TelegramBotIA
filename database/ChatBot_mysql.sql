-- ============================================================================
-- Script SQL convertido de SQL Server a MySQL
-- Herramienta: SQLServerToMySQLConverter
-- Fecha: 2025-12-29 20:40:25
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/****** Object:  Database `abcmasplus`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
USE `abcmasplus`
;
/****** Object:  Table `dbo`.`knowledge_categories`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`knowledge_categories`(
	`id` `INT` AUTO_INCREMENT NOT NULL,
	`name` `varchar`(50) NOT NULL,
	`display_name` `nvarchar`(100) NOT NULL,
	`description` `nvarchar`(500) NULL,
	`icon` `nvarchar`(10) NULL,
	`active` `TINYINT(1)` NOT NULL,
	`created_at` `DATETIME`(7) NOT NULL,
	`updated_at` `DATETIME`(7) NOT NULL,
PRIMARY KEY 
(
	`id` ASC
) 
) 
;
/****** Object:  Table `dbo`.`knowledge_entries`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`knowledge_entries`(
	`id` `INT` AUTO_INCREMENT NOT NULL,
	`category_id` `INT` NOT NULL,
	`question` `nvarchar`(500) NOT NULL,
	`answer` `nvarchar`(max) NOT NULL,
	`keywords` `nvarchar`(max) NOT NULL,
	`related_commands` `nvarchar`(500) NULL,
	`priority` `INT` NOT NULL,
	`active` `TINYINT(1)` NOT NULL,
	`created_at` `DATETIME`(7) NOT NULL,
	`updated_at` `DATETIME`(7) NOT NULL,
	`created_by` `nvarchar`(100) NULL,
PRIMARY KEY 
(
	`id` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  View `dbo`.`vw_knowledge_base`    Script DATE: 29/12/2025 07:09:28 p. m. ******/



CREATE VIEW `dbo`.`vw_knowledge_base` AS
SELECT
    e.id,
    e.question,
    e.answer,
    e.keywords,
    e.related_commands,
    e.priority,
    c.name as category,
    c.display_name as category_display_name,
    c.icon as category_icon,
    e.created_at,
    e.updated_at
FROM knowledge_entries e
INNER JOIN knowledge_categories c ON e.category_id = c.id
WHERE e.active = 1 AND c.active = 1;
/****** Object:  Table `dbo`.`AreaAtendedora`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`AreaAtendedora`(
	`idAreaAtendedora` `INT` AUTO_INCREMENT NOT NULL,
	`idGerencia` `INT` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_AreaAtendedora` PRIMARY KEY 
(
	`idAreaAtendedora` ASC
) 
) 
;
/****** Object:  Table `dbo`.`BibliotecaPrompts`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`BibliotecaPrompts`(
	`idPrompt` `INT` AUTO_INCREMENT NOT NULL,
	`idCategoriaPrompt` `INT` NOT NULL,
	`titulo` `nvarchar`(200) NOT NULL,
	`descripcion` `nvarchar`(1000) NULL,
	`contenidoMarkdown` `nvarchar`(max) NOT NULL,
	`mensajeSistema` `nvarchar`(max) NULL,
	`version` `INT` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`favorito` `TINYINT(1)` NOT NULL,
	`cantidadEjecuciones` `INT` NOT NULL,
	`ultimaEjecucion` `DATETIME` NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaActualizacion` `DATETIME` NULL,
	`creadoPorUsuario` `nvarchar`(100) NULL,
PRIMARY KEY 
(
	`idPrompt` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`CategoriasPrompt`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`CategoriasPrompt`(
	`idCategoriaPrompt` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `nvarchar`(100) NOT NULL,
	`descripcion` `nvarchar`(500) NULL,
	`icono` `nvarchar`(50) NULL,
	`color` `nvarchar`(20) NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaActualizacion` `DATETIME` NULL,
PRIMARY KEY 
(
	`idCategoriaPrompt` ASC
) 
) 
;
/****** Object:  Table `dbo`.`ChatConversaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ChatConversaciones`(
	`IdConversacion` `INT` AUTO_INCREMENT NOT NULL,
	`IdUsuario` `INT` NOT NULL,
	`Titulo` `nvarchar`(200) NULL,
	`IdSistema` `INT` NULL,
	`Modelo` `nvarchar`(100) NULL,
	`Temperatura` `decimal`(3, 2) NULL,
	`MaxTokens` `INT` NULL,
	`MensajeSistema` `nvarchar`(max) NULL,
	`TotalMensajes` `INT` NOT NULL,
	`TotalTokensUsados` `INT` NOT NULL,
	`CostoTotal` `decimal`(10, 4) NOT NULL,
	`Favorita` `TINYINT(1)` NOT NULL,
	`Archivada` `TINYINT(1)` NOT NULL,
	`Activa` `TINYINT(1)` NOT NULL,
	`FechaCreacion` `DATETIME` NOT NULL,
	`FechaUltimaActividad` `DATETIME` NOT NULL,
 CONSTRAINT `PK_ChatConversaciones` PRIMARY KEY 
(
	`IdConversacion` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`ChatConversacionesCompartidas`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ChatConversacionesCompartidas`(
	`IdCompartida` `INT` AUTO_INCREMENT NOT NULL,
	`IdConversacion` `INT` NOT NULL,
	`TokenPublico` `nvarchar`(100) NOT NULL,
	`Titulo` `nvarchar`(200) NULL,
	`Descripcion` `nvarchar`(500) NULL,
	`PermiteComentarios` `TINYINT(1)` NOT NULL,
	`PasswordProtegida` `TINYINT(1)` NOT NULL,
	`PasswordHash` `nvarchar`(500) NULL,
	`VistasCount` `INT` NOT NULL,
	`Activa` `TINYINT(1)` NOT NULL,
	`FechaCreacion` `DATETIME` NOT NULL,
	`FechaExpiracion` `DATETIME` NULL,
 CONSTRAINT `PK_ChatConversacionesCompartidas` PRIMARY KEY 
(
	`IdCompartida` ASC
) 
) 
;
/****** Object:  Table `dbo`.`ChatMensajes`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ChatMensajes`(
	`IdMensaje` `INT` AUTO_INCREMENT NOT NULL,
	`IdConversacion` `INT` NOT NULL,
	`Rol` `nvarchar`(20) NOT NULL,
	`Contenido` `nvarchar`(max) NOT NULL,
	`TokensPrompt` `INT` NULL,
	`TokensCompletion` `INT` NULL,
	`TiempoRespuestaMs` `INT` NULL,
	`Costo` `decimal`(10, 6) NULL,
	`Modelo` `nvarchar`(100) NULL,
	`Metadata` `nvarchar`(max) NULL,
	`FechaCreacion` `DATETIME` NOT NULL,
 CONSTRAINT `PK_ChatMensajes` PRIMARY KEY 
(
	`IdMensaje` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`ChatPermisosRol`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ChatPermisosRol`(
	`IdPermisoRol` `INT` AUTO_INCREMENT NOT NULL,
	`IdRol` `INT` NOT NULL,
	`PuedeUsarChat` `TINYINT(1)` NOT NULL,
	`PuedeVerHistorial` `TINYINT(1)` NOT NULL,
	`PuedeExportarConversaciones` `TINYINT(1)` NOT NULL,
	`PuedeUsarIA` `TINYINT(1)` NOT NULL,
	`SistemasPermitidos` `nvarchar`(max) NULL,
	`LimiteConversacionesDia` `INT` NULL,
	`LimiteMensajesDia` `INT` NULL,
	`LimiteTokensDia` `INT` NULL,
	`Activo` `TINYINT(1)` NOT NULL,
	`FechaCreacion` `DATETIME` NOT NULL,
	`FechaModificacion` `DATETIME` NULL,
 CONSTRAINT `PK_ChatPermisosRol` PRIMARY KEY 
(
	`IdPermisoRol` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`ChatPlantillasPrompt`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ChatPlantillasPrompt`(
	`IdPlantilla` `INT` AUTO_INCREMENT NOT NULL,
	`Nombre` `nvarchar`(200) NOT NULL,
	`Descripcion` `nvarchar`(500) NULL,
	`Categoria` `nvarchar`(100) NULL,
	`Icono` `nvarchar`(50) NULL,
	`ContenidoPrompt` `nvarchar`(max) NOT NULL,
	`MensajeSistema` `nvarchar`(max) NULL,
	`Variables` `nvarchar`(max) NULL,
	`ModeloRecomendado` `nvarchar`(100) NULL,
	`TemperaturaRecomendada` `decimal`(3, 2) NULL,
	`IdCreador` `INT` NULL,
	`UsosCount` `INT` NOT NULL,
	`Publica` `TINYINT(1)` NOT NULL,
	`Activa` `TINYINT(1)` NOT NULL,
	`FechaCreacion` `DATETIME` NOT NULL,
 CONSTRAINT `PK_ChatPlantillasPrompt` PRIMARY KEY 
(
	`IdPlantilla` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`column_documentation`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`column_documentation`(
	`id` `INT` AUTO_INCREMENT NOT NULL,
	`table_doc_id` `INT` NOT NULL,
	`column_name` `varchar`(100) NOT NULL,
	`display_name` `nvarchar`(100) NULL,
	`description` `nvarchar`(500) NULL,
	`data_type` `varchar`(50) NULL,
	`example_value` `nvarchar`(200) NULL,
	`icon` `nvarchar`(10) NULL,
	`is_key` `TINYINT(1)` NULL,
	`created_at` `DATETIME`(7) NOT NULL,
	`updated_at` `DATETIME`(7) NOT NULL,
PRIMARY KEY 
(
	`id` ASC
) 
) 
;
/****** Object:  Table `dbo`.`ConfiguracionIAModulos`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ConfiguracionIAModulos`(
	`idConfiguracionIA` `INT` AUTO_INCREMENT NOT NULL,
	`idModulo` `INT` NOT NULL,
	`idProveedorIA` `INT` NOT NULL,
	`idModeloIA` `INT` NOT NULL,
	`apiKey` `varchar`(500) NULL,
	`creditosDisponibles` `decimal`(18, 2) NOT NULL,
	`creditosIniciales` `decimal`(18, 2) NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaActualizacion` `DATETIME` NULL,
PRIMARY KEY 
(
	`idConfiguracionIA` ASC
) 
) 
;
/****** Object:  Table `dbo`.`ConfiguracionIASistemas`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ConfiguracionIASistemas`(
	`idConfiguracionIA` `INT` AUTO_INCREMENT NOT NULL,
	`idSistemaAplicacion` `INT` NOT NULL,
	`idProveedorIA` `INT` NOT NULL,
	`idModeloIA` `INT` NOT NULL,
	`apiKey` `varchar`(500) NULL,
	`creditosDisponibles` `decimal`(18, 2) NOT NULL,
	`creditosIniciales` `decimal`(18, 2) NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaActualizacion` `DATETIME` NULL,
PRIMARY KEY 
(
	`idConfiguracionIA` ASC
) 
) 
;
/****** Object:  Table `dbo`.`EjecucionesPrompt`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`EjecucionesPrompt`(
	`idEjecucionPrompt` `INT` AUTO_INCREMENT NOT NULL,
	`idPrompt` `INT` NOT NULL,
	`promptFinal` `nvarchar`(max) NOT NULL,
	`respuestaIA` `nvarchar`(max) NULL,
	`exitoso` `TINYINT(1)` NOT NULL,
	`mensajeError` `nvarchar`(max) NULL,
	`tokensUsados` `INT` NULL,
	`costoEstimado` `decimal`(10, 6) NULL,
	`tiempoRespuestaMs` `INT` NULL,
	`idProveedorIA` `INT` NULL,
	`idModeloIA` `INT` NULL,
	`temperatura` `decimal`(3, 2) NULL,
	`maxTokens` `INT` NULL,
	`fechaEjecucion` `DATETIME` NOT NULL,
	`ejecutadoPorUsuario` `nvarchar`(100) NULL,
PRIMARY KEY 
(
	`idEjecucionPrompt` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`EtiquetasPrompt`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`EtiquetasPrompt`(
	`idEtiquetaPrompt` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `nvarchar`(50) NOT NULL,
	`color` `nvarchar`(20) NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
PRIMARY KEY 
(
	`idEtiquetaPrompt` ASC
) 
) 
;
/****** Object:  Table `dbo`.`Gerencias`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`Gerencias`(
	`idGerencia` `INT` AUTO_INCREMENT NOT NULL,
	`idResponsable` `INT` NULL,
	`gerencia` `nvarchar`(200) NOT NULL,
	`alias` `nvarchar`(50) NULL,
	`correo` `nvarchar`(150) NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_Gerencias` PRIMARY KEY 
(
	`idGerencia` ASC
) 
) 
;
/****** Object:  Table `dbo`.`GerenciasRolesIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`GerenciasRolesIA`(
	`idGerenciaRolIA` `INT` AUTO_INCREMENT NOT NULL,
	`idRol` `INT` NOT NULL,
	`idGerencia` `INT` NOT NULL,
	`fechaAsignacion` `DATETIME` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_GerenciasRolesIA` PRIMARY KEY 
(
	`idGerenciaRolIA` ASC
) 
) 
;
/****** Object:  Table `dbo`.`GerenciaUsuarios`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`GerenciaUsuarios`(
	`idGerenciaUsuario` `INT` AUTO_INCREMENT NOT NULL,
	`idUsuario` `INT` NOT NULL,
	`idGerencia` `INT` NOT NULL,
	`fechaAsignacion` `DATETIME` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_GerenciaUsuarios` PRIMARY KEY 
(
	`idGerenciaUsuario` ASC
) 
) 
;
/****** Object:  Table `dbo`.`Iconos`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`Iconos`(
	`idIcono` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `varchar`(50) NOT NULL,
	`clase` `varchar`(100) NOT NULL,
	`categoria` `varchar`(50) NOT NULL,
	`descripcion` `varchar`(200) NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
PRIMARY KEY 
(
	`idIcono` ASC
) 
) 
;
/****** Object:  Table `dbo`.`LogOperaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`LogOperaciones`(
	`idLog` `BIGINT` AUTO_INCREMENT NOT NULL,
	`idUsuario` `INT` NOT NULL,
	`idOperacion` `INT` NOT NULL,
	`telegramChatId` `BIGINT` NULL,
	`telegramUsername` `nvarchar`(100) NULL,
	`parametros` `nvarchar`(max) NULL,
	`resultado` `nvarchar`(50) NOT NULL,
	`mensajeError` `nvarchar`(max) NULL,
	`duracionMs` `INT` NULL,
	`ipOrigen` `nvarchar`(50) NULL,
	`fechaEjecucion` `DATETIME` NOT NULL,
 CONSTRAINT `PK_LogOperaciones` PRIMARY KEY 
(
	`idLog` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`MenuNavegacion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`MenuNavegacion`(
	`idMenu` `INT` AUTO_INCREMENT NOT NULL,
	`idMenuPadre` `INT` NULL,
	`nombre` `nvarchar`(100) NOT NULL,
	`titulo` `nvarchar`(200) NOT NULL,
	`url` `nvarchar`(500) NULL,
	`controlador` `nvarchar`(100) NULL,
	`accion` `nvarchar`(100) NULL,
	`icono` `nvarchar`(50) NOT NULL,
	`orden` `INT` NOT NULL,
	`nivel` `INT` NOT NULL,
	`esHeader` `TINYINT(1)` NOT NULL,
	`esTreeview` `TINYINT(1)` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`requiresAuth` `TINYINT(1)` NOT NULL,
	`roles` `nvarchar`(500) NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaModificacion` `DATETIME` NULL,
 CONSTRAINT `PK_MenuNavegacion` PRIMARY KEY 
(
	`idMenu` ASC
) 
) 
;
/****** Object:  Table `dbo`.`ModelosIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ModelosIA`(
	`idModeloIA` `INT` AUTO_INCREMENT NOT NULL,
	`idProveedorIA` `INT` NOT NULL,
	`nombre` `varchar`(100) NOT NULL,
	`nombreCompleto` `varchar`(200) NULL,
	`descripcion` `varchar`(500) NULL,
	`costoPorToken` `decimal`(18, 6) NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaActualizacion` `DATETIME` NULL,
PRIMARY KEY 
(
	`idModeloIA` ASC
) 
) 
;
/****** Object:  Table `dbo`.`Modulos`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`Modulos`(
	`idModulo` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `nvarchar`(100) NOT NULL,
	`descripcion` `nvarchar`(500) NULL,
	`icono` `nvarchar`(50) NULL,
	`orden` `INT` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
 CONSTRAINT `PK_Modulos` PRIMARY KEY 
(
	`idModulo` ASC
) 
) 
;
/****** Object:  Table `dbo`.`Operaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`Operaciones`(
	`idOperacion` `INT` AUTO_INCREMENT NOT NULL,
	`idModulo` `INT` NOT NULL,
	`nombre` `nvarchar`(100) NOT NULL,
	`descripcion` `nvarchar`(500) NULL,
	`comando` `nvarchar`(100) NULL,
	`requiereParametros` `TINYINT(1)` NOT NULL,
	`parametrosEjemplo` `nvarchar`(500) NULL,
	`nivelCriticidad` `INT` NOT NULL,
	`orden` `INT` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
 CONSTRAINT `PK_Operaciones` PRIMARY KEY 
(
	`idOperacion` ASC
) 
) 
;
/****** Object:  Table `dbo`.`ParametrosEjecucion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ParametrosEjecucion`(
	`idParametroEjecucion` `INT` AUTO_INCREMENT NOT NULL,
	`idEjecucionPrompt` `INT` NOT NULL,
	`nombreParametro` `nvarchar`(100) NOT NULL,
	`valorParametro` `nvarchar`(max) NOT NULL,
PRIMARY KEY 
(
	`idParametroEjecucion` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`PromptEtiquetas`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`PromptEtiquetas`(
	`idPromptEtiqueta` `INT` AUTO_INCREMENT NOT NULL,
	`idPrompt` `INT` NOT NULL,
	`idEtiquetaPrompt` `INT` NOT NULL,
PRIMARY KEY 
(
	`idPromptEtiqueta` ASC
) 
) 
;
/****** Object:  Table `dbo`.`ProveedoresIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`ProveedoresIA`(
	`idProveedorIA` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `varchar`(100) NOT NULL,
	`descripcion` `varchar`(500) NULL,
	`urlBase` `varchar`(500) NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaActualizacion` `DATETIME` NULL,
PRIMARY KEY 
(
	`idProveedorIA` ASC
) 
) 
;
/****** Object:  Table `dbo`.`Roles`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`Roles`(
	`idRol` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `nvarchar`(100) NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_Roles` PRIMARY KEY 
(
	`idRol` ASC
) 
) 
;
/****** Object:  Table `dbo`.`RolesCategoriesKnowledge`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`RolesCategoriesKnowledge`(
	`idRolCategoria` `INT` AUTO_INCREMENT NOT NULL,
	`idRol` `INT` NOT NULL,
	`idCategoria` `INT` NOT NULL,
	`permitido` `TINYINT(1)` NOT NULL,
	`fechaAsignacion` `DATETIME` NULL,
	`usuarioAsignacion` `INT` NULL,
	`activo` `TINYINT(1)` NULL,
PRIMARY KEY 
(
	`idRolCategoria` ASC
) 
) 
;
/****** Object:  Table `dbo`.`RolesIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`RolesIA`(
	`idRol` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `nvarchar`(100) NOT NULL,
	`descripcion` `nvarchar`(500) NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_RolesIA` PRIMARY KEY 
(
	`idRol` ASC
) 
) 
;
/****** Object:  Table `dbo`.`RolesOperaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`RolesOperaciones`(
	`idRolOperacion` `INT` AUTO_INCREMENT NOT NULL,
	`idRol` `INT` NOT NULL,
	`idOperacion` `INT` NOT NULL,
	`permitido` `TINYINT(1)` NOT NULL,
	`fechaAsignacion` `DATETIME` NOT NULL,
	`usuarioAsignacion` `INT` NULL,
	`observaciones` `nvarchar`(500) NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_RolesOperaciones` PRIMARY KEY 
(
	`idRolOperacion` ASC
) 
) 
;
/****** Object:  Table `dbo`.`SistemasAplicaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`SistemasAplicaciones`(
	`idSistemaAplicacion` `INT` AUTO_INCREMENT NOT NULL,
	`nombre` `varchar`(100) NOT NULL,
	`descripcion` `varchar`(500) NULL,
	`icono` `varchar`(100) NULL,
	`color` `varchar`(20) NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaActualizacion` `DATETIME` NULL,
PRIMARY KEY 
(
	`idSistemaAplicacion` ASC
) 
) 
;
/****** Object:  Table `dbo`.`table_documentation`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`table_documentation`(
	`id` `INT` AUTO_INCREMENT NOT NULL,
	`schema_name` `varchar`(100) NOT NULL,
	`table_name` `varchar`(100) NOT NULL,
	`display_name` `nvarchar`(100) NULL,
	`description` `nvarchar`(max) NULL,
	`usage_examples` `nvarchar`(max) NULL,
	`common_queries` `nvarchar`(max) NULL,
	`category` `nvarchar`(50) NULL,
	`active` `TINYINT(1)` NOT NULL,
	`created_at` `DATETIME`(7) NOT NULL,
	`updated_at` `DATETIME`(7) NOT NULL,
PRIMARY KEY 
(
	`id` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`UserMemoryProfiles`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`UserMemoryProfiles`(
	`idMemoryProfile` `INT` AUTO_INCREMENT NOT NULL,
	`idUsuario` `INT` NOT NULL,
	`resumenContextoLaboral` `nvarchar`(max) NULL,
	`resumenTemasRecientes` `nvarchar`(max) NULL,
	`resumenHistorialBreve` `nvarchar`(max) NULL,
	`numInteracciones` `INT` NOT NULL,
	`ultimaActualizacion` `DATETIME`(7) NOT NULL,
	`fechaCreacion` `DATETIME`(7) NOT NULL,
	`version` `INT` NOT NULL,
 CONSTRAINT `PK_UserMemoryProfiles` PRIMARY KEY 
(
	`idMemoryProfile` ASC
) 
)  TEXTIMAGE_
;
/****** Object:  Table `dbo`.`Usuarios`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`Usuarios`(
	`idUsuario` `INT` AUTO_INCREMENT NOT NULL,
	`idEmpleado` `INT` NOT NULL,
	`nombre` `nvarchar`(100) NOT NULL,
	`apellido` `nvarchar`(100) NOT NULL,
	`rol` `INT` NOT NULL,
	`email` `nvarchar`(150) NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`fechaUltimoAcceso` `DATETIME` NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_Usuarios` PRIMARY KEY 
(
	`idUsuario` ASC
) 
) 
;
/****** Object:  Table `dbo`.`UsuariosOperaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`UsuariosOperaciones`(
	`idUsuarioOperacion` `INT` AUTO_INCREMENT NOT NULL,
	`idUsuario` `INT` NOT NULL,
	`idOperacion` `INT` NOT NULL,
	`permitido` `TINYINT(1)` NOT NULL,
	`fechaAsignacion` `DATETIME` NOT NULL,
	`fechaExpiracion` `DATETIME` NULL,
	`usuarioAsignacion` `INT` NULL,
	`observaciones` `nvarchar`(500) NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_UsuariosOperaciones` PRIMARY KEY 
(
	`idUsuarioOperacion` ASC
) 
) 
;
/****** Object:  Table `dbo`.`UsuariosRolesIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`UsuariosRolesIA`(
	`idUsuarioRolIA` `INT` AUTO_INCREMENT NOT NULL,
	`idRol` `INT` NOT NULL,
	`idUsuario` `INT` NOT NULL,
	`fechaAsignacion` `DATETIME` NOT NULL,
	`activo` `TINYINT(1)` NOT NULL,
 CONSTRAINT `PK_UsuariosRolesIA` PRIMARY KEY 
(
	`idUsuarioRolIA` ASC
) 
) 
;
/****** Object:  Table `dbo`.`UsuariosTelegram`    Script DATE: 29/12/2025 07:09:28 p. m. ******/


CREATE TABLE `dbo`.`UsuariosTelegram`(
	`idUsuarioTelegram` `INT` AUTO_INCREMENT NOT NULL,
	`idUsuario` `INT` NOT NULL,
	`telegramChatId` `BIGINT` NOT NULL,
	`telegramUsername` `nvarchar`(100) NULL,
	`telegramFirstName` `nvarchar`(100) NULL,
	`telegramLastName` `nvarchar`(100) NULL,
	`alias` `nvarchar`(50) NULL,
	`esPrincipal` `TINYINT(1)` NOT NULL,
	`estado` `nvarchar`(20) NOT NULL,
	`fechaRegistro` `DATETIME` NOT NULL,
	`fechaUltimaActividad` `DATETIME` NULL,
	`fechaVerificacion` `DATETIME` NULL,
	`codigoVerificacion` `nvarchar`(10) NULL,
	`verificado` `TINYINT(1)` NOT NULL,
	`intentosVerificacion` `INT` NOT NULL,
	`notificacionesActivas` `TINYINT(1)` NOT NULL,
	`observaciones` `nvarchar`(500) NULL,
	`activo` `TINYINT(1)` NOT NULL,
	`fechaCreacion` `DATETIME` NOT NULL,
	`usuarioCreacion` `INT` NULL,
	`fechaModificacion` `DATETIME` NULL,
	`usuarioModificacion` `INT` NULL,
 CONSTRAINT `PK_UsuariosTelegram` PRIMARY KEY 
(
	`idUsuarioTelegram` ASC
) 
) 
;
SET IDENTITY_INSERT `dbo`.`AreaAtendedora` ON 

INSERT `dbo`.`AreaAtendedora` (`idAreaAtendedora`, `idGerencia`, `fechaCreacion`, `activo`) VALUES (1, 2, CAST(N'2025-07-26T10:52:46.347' AS DATETIME), 1)
INSERT `dbo`.`AreaAtendedora` (`idAreaAtendedora`, `idGerencia`, `fechaCreacion`, `activo`) VALUES (2, 3, CAST(N'2025-07-31T10:52:46.347' AS DATETIME), 1)
INSERT `dbo`.`AreaAtendedora` (`idAreaAtendedora`, `idGerencia`, `fechaCreacion`, `activo`) VALUES (3, 4, CAST(N'2025-08-05T10:52:46.347' AS DATETIME), 1)
INSERT `dbo`.`AreaAtendedora` (`idAreaAtendedora`, `idGerencia`, `fechaCreacion`, `activo`) VALUES (4, 8, CAST(N'2025-08-25T10:52:46.347' AS DATETIME), 1)
INSERT `dbo`.`AreaAtendedora` (`idAreaAtendedora`, `idGerencia`, `fechaCreacion`, `activo`) VALUES (5, 9, CAST(N'2025-08-30T10:52:46.347' AS DATETIME), 1)
INSERT `dbo`.`AreaAtendedora` (`idAreaAtendedora`, `idGerencia`, `fechaCreacion`, `activo`) VALUES (6, 10, CAST(N'2025-09-04T10:52:46.347' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`AreaAtendedora` OFF
;
SET IDENTITY_INSERT `dbo`.`BibliotecaPrompts` ON 

INSERT `dbo`.`BibliotecaPrompts` (`idPrompt`, `idCategoriaPrompt`, `titulo`, `descripcion`, `contenidoMarkdown`, `mensajeSistema`, `version`, `activo`, `favorito`, `cantidadEjecuciones`, `ultimaEjecucion`, `fechaCreacion`, `fechaActualizacion`, `creadoPorUsuario`) VALUES (1, 2, N'Generador de API REST en C#', N'Genera un controlador de API REST completo en C# con operaciones CRUD', N'# Generador de API REST en C#

Por favor, genera un controlador de API REST en C# para la entidad **{{nombre_entidad}}**.

## Requisitos:
- Operaciones CRUD completas (Create, Read, Update, Delete)
- Usar **{{framework}}** como framework
- Incluir validaciones básicas
- Documentación con comentarios TEXT
- Manejo de errores apropiado

## Campos de la entidad:
{{campos_entidad}}

## Notas adicionales:
{{notas_adicionales}}', N'Eres un experto desarrollador de C# y .NET. Genera código limpio, siguiendo las mejores prácticas y los principios SOLID.', 1, 1, 0, 0, NULL, CAST(N'2025-12-03T16:19:45.730' AS DATETIME), NULL, N'Sistema')
INSERT `dbo`.`BibliotecaPrompts` (`idPrompt`, `idCategoriaPrompt`, `titulo`, `descripcion`, `contenidoMarkdown`, `mensajeSistema`, `version`, `activo`, `favorito`, `cantidadEjecuciones`, `ultimaEjecucion`, `fechaCreacion`, `fechaActualizacion`, `creadoPorUsuario`) VALUES (2, 2, N'Revisor de Código y Buenas Prácticas', N'Analiza código fuente y sugiere mejoras basadas en buenas prácticas', N'# Revisión de Código

Por favor, analiza el siguiente código {{lenguaje}} y proporciona una revisión detallada:

```{{lenguaje}}
{{codigo}}
```

## Aspectos a revisar:
- ? Buenas prácticas del lenguaje
- ? Rendimiento y optimización
- ? Seguridad
- ? Legibilidad y mantenibilidad
- ? Posibles bugs o errores

## Contexto adicional:
{{contexto}}', N'Eres un arquitecto de software senior con amplia experiencia en revisiones de código. Proporciona críticas constructivas y sugerencias prácticas.', 2, 1, 0, 0, NULL, CAST(N'2025-12-03T16:19:45.733' AS DATETIME), CAST(N'2025-12-25T11:55:32.977' AS DATETIME), N'Sistema')
INSERT `dbo`.`BibliotecaPrompts` (`idPrompt`, `idCategoriaPrompt`, `titulo`, `descripcion`, `contenidoMarkdown`, `mensajeSistema`, `version`, `activo`, `favorito`, `cantidadEjecuciones`, `ultimaEjecucion`, `fechaCreacion`, `fechaActualizacion`, `creadoPorUsuario`) VALUES (3, 3, N'Generador de Artículos de Blog', N'Crea artículos de blog optimizados para SEO sobre cualquier tema', N'# Generador de Artículo de Blog

Crea un artículo de blog profesional sobre el siguiente tema:

## Tema Principal:
**{{tema}}**

## Audiencia Objetivo:
{{audiencia}}

## Longitud deseada:
{{longitud}} palabras aproximadamente

## Tono del artículo:
{{tono}}

## Palabras clave SEO:
{{palabras_clave}}

## Estructura requerida:
1. Título atractivo
2. Introducción enganchante
3. 3-5 secciones con subtítulos
4. Conclusión con llamada a la acción
5. Meta descripción (150 caracteres)', N'Eres un escritor profesional especializado en contenido para blogs y marketing digital. Crea contenido atractivo, informativo y optimizado para SEO.', 1, 1, 0, 0, NULL, CAST(N'2025-12-03T16:19:45.733' AS DATETIME), NULL, N'Sistema')
SET IDENTITY_INSERT `dbo`.`BibliotecaPrompts` OFF
;
SET IDENTITY_INSERT `dbo`.`CategoriasPrompt` ON 

INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (1, N'General', N'Prompts de propósito general', N'bi-star-fill', N'#6366f1', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (2, N'Desarrollo de Software', N'Prompts para generación y revisión de código', N'bi-code-slash', N'#10b981', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (3, N'Escritura y Contenido', N'Prompts para creación de contenido y redacción', N'bi-pencil-square', N'#f59e0b', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (4, N'Análisis de Datos', N'Prompts para análisis y procesamiento de datos', N'bi-graph-up', N'#3b82f6', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (5, N'Marketing', N'Prompts para estrategias de marketing y publicidad', N'bi-megaphone-fill', N'#ec4899', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (6, N'Educación', N'Prompts para enseñanza y aprendizaje', N'bi-book-fill', N'#8b5cf6', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (7, N'Traducción', N'Prompts para traducción de idiomas', N'bi-translate', N'#14b8a6', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
INSERT `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (8, N'Atención al Cliente', N'Prompts para servicio y soporte al cliente', N'bi-headset', N'#f97316', 1, CAST(N'2025-12-03T16:19:45.717' AS DATETIME), NULL)
SET IDENTITY_INSERT `dbo`.`CategoriasPrompt` OFF
;
SET IDENTITY_INSERT `dbo`.`ChatPermisosRol` ON 

INSERT `dbo`.`ChatPermisosRol` (`IdPermisoRol`, `IdRol`, `PuedeUsarChat`, `PuedeVerHistorial`, `PuedeExportarConversaciones`, `PuedeUsarIA`, `SistemasPermitidos`, `LimiteConversacionesDia`, `LimiteMensajesDia`, `LimiteTokensDia`, `Activo`, `FechaCreacion`, `FechaModificacion`) VALUES (1, 1, 1, 1, 1, 1, NULL, NULL, NULL, NULL, 1, CAST(N'2025-12-27T11:28:51.567' AS DATETIME), NULL)
SET IDENTITY_INSERT `dbo`.`ChatPermisosRol` OFF
;
SET IDENTITY_INSERT `dbo`.`ChatPlantillasPrompt` ON 

INSERT `dbo`.`ChatPlantillasPrompt` (`IdPlantilla`, `Nombre`, `Descripcion`, `Categoria`, `Icono`, `ContenidoPrompt`, `MensajeSistema`, `Variables`, `ModeloRecomendado`, `TemperaturaRecomendada`, `IdCreador`, `UsosCount`, `Publica`, `Activa`, `FechaCreacion`) VALUES (1, N'Asistente General', N'Asistente IA general para cualquier consulta', N'General', N'fa fa-comments', N'Hola, Â¿en quÃ© puedo ayudarte hoy?', N'Eres un asistente IA Ãºtil, preciso y amigable. Respondes en espaÃ±ol de forma clara y concisa.', NULL, NULL, NULL, NULL, 0, 1, 1, CAST(N'2025-12-27T11:28:51.577' AS DATETIME))
INSERT `dbo`.`ChatPlantillasPrompt` (`IdPlantilla`, `Nombre`, `Descripcion`, `Categoria`, `Icono`, `ContenidoPrompt`, `MensajeSistema`, `Variables`, `ModeloRecomendado`, `TemperaturaRecomendada`, `IdCreador`, `UsosCount`, `Publica`, `Activa`, `FechaCreacion`) VALUES (2, N'AnÃ¡lisis de CÃ³digo', N'Analiza y revisa cÃ³digo de programaciÃ³n', N'Desarrollo', N'fa fa-code', N'Por favor, analiza el siguiente cÃ³digo: {{codigo}}', N'Eres un experto en anÃ¡lisis de cÃ³digo. Proporciona revisiones detalladas, identifica bugs, sugieres mejoras y explicas el cÃ³digo de forma clara.', NULL, N'gpt-4', NULL, NULL, 0, 1, 1, CAST(N'2025-12-27T11:28:51.610' AS DATETIME))
INSERT `dbo`.`ChatPlantillasPrompt` (`IdPlantilla`, `Nombre`, `Descripcion`, `Categoria`, `Icono`, `ContenidoPrompt`, `MensajeSistema`, `Variables`, `ModeloRecomendado`, `TemperaturaRecomendada`, `IdCreador`, `UsosCount`, `Publica`, `Activa`, `FechaCreacion`) VALUES (3, N'Generador de SQL', N'Genera consultas SQL a partir de descripciÃ³n en lenguaje natural', N'Base de Datos', N'fa fa-database', N'Genera una consulta SQL para: {{descripcion}}', N'Eres un experto en SQL Server. Generas consultas SQL optimizadas, seguras y bien documentadas. Incluye comentarios explicativos.', N'`"descripcion"`', NULL, NULL, NULL, 0, 1, 1, CAST(N'2025-12-27T11:28:51.617' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`ChatPlantillasPrompt` OFF
;
SET IDENTITY_INSERT `dbo`.`ConfiguracionIAModulos` ON 

INSERT `dbo`.`ConfiguracionIAModulos` (`idConfiguracionIA`, `idModulo`, `idProveedorIA`, `idModeloIA`, `apiKey`, `creditosDisponibles`, `creditosIniciales`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (1, 1, 1, 2, N'sk-demo-key-openai-12345678901234567890123456789012', CAST(1000.00 AS DECIMAL(18,2)), CAST(1000.00 AS DECIMAL(18,2)), 1, CAST(N'2025-12-02T21:58:03.420' AS DATETIME), NULL)
INSERT `dbo`.`ConfiguracionIAModulos` (`idConfiguracionIA`, `idModulo`, `idProveedorIA`, `idModeloIA`, `apiKey`, `creditosDisponibles`, `creditosIniciales`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (2, 2, 2, 8, N'sk-demo-key-anthropic-12345678901234567890123456789012', CAST(2500.00 AS DECIMAL(18,2)), CAST(2500.00 AS DECIMAL(18,2)), 1, CAST(N'2025-12-02T21:58:03.420' AS DATETIME), NULL)
INSERT `dbo`.`ConfiguracionIAModulos` (`idConfiguracionIA`, `idModulo`, `idProveedorIA`, `idModeloIA`, `apiKey`, `creditosDisponibles`, `creditosIniciales`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (3, 2, 3, 9, N'demo-key-google-12345678901234567890123456789012345', CAST(1500.00 AS DECIMAL(18,2)), CAST(1500.00 AS DECIMAL(18,2)), 0, CAST(N'2025-12-02T21:58:03.420' AS DATETIME), NULL)
SET IDENTITY_INSERT `dbo`.`ConfiguracionIAModulos` OFF
;
SET IDENTITY_INSERT `dbo`.`ConfiguracionIASistemas` ON 

INSERT `dbo`.`ConfiguracionIASistemas` (`idConfiguracionIA`, `idSistemaAplicacion`, `idProveedorIA`, `idModeloIA`, `apiKey`, `creditosDisponibles`, `creditosIniciales`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (1, 1, 1, 2, N'sk-demo-key-openai-12345678901234567890123456789012', CAST(1000.00 AS DECIMAL(18,2)), CAST(1000.00 AS DECIMAL(18,2)), 0, CAST(N'2025-12-02T21:58:03.420' AS DATETIME), CAST(N'2025-12-05T15:21:29.743' AS DATETIME))
INSERT `dbo`.`ConfiguracionIASistemas` (`idConfiguracionIA`, `idSistemaAplicacion`, `idProveedorIA`, `idModeloIA`, `apiKey`, `creditosDisponibles`, `creditosIniciales`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (2, 2, 2, 8, N'sk-demo-key-anthropic-12345678901234567890123456789012', CAST(2500.00 AS DECIMAL(18,2)), CAST(2500.00 AS DECIMAL(18,2)), 1, CAST(N'2025-12-02T21:58:03.420' AS DATETIME), NULL)
INSERT `dbo`.`ConfiguracionIASistemas` (`idConfiguracionIA`, `idSistemaAplicacion`, `idProveedorIA`, `idModeloIA`, `apiKey`, `creditosDisponibles`, `creditosIniciales`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (3, 2, 3, 9, N'demo-key-google-12345678901234567890123456789012345', CAST(1500.00 AS DECIMAL(18,2)), CAST(1500.00 AS DECIMAL(18,2)), 0, CAST(N'2025-12-02T21:58:03.420' AS DATETIME), NULL)
INSERT `dbo`.`ConfiguracionIASistemas` (`idConfiguracionIA`, `idSistemaAplicacion`, `idProveedorIA`, `idModeloIA`, `apiKey`, `creditosDisponibles`, `creditosIniciales`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (4, 7, 1, 23, N'ENC:yM5Gn8R/cJ6zOcyPNAKNHEjf8+L6r4ofLZVl1SArOiRI1byDgy6lTAot5BwzD8h5ylMKG4TLZXWWHFbXVj3nC4woEGXwQAL2o0Z4B+1GGM/gGFuqxMFojXL+kOIYBFo081hWjebq1STENBQWJxMcCYmjAl7K/Pms7c3TrPBTzaOz5AfDZ3OuPxVSCwvfe40Fh19rf1s6adMmNGkvp22qqCXEQXXVIEaTOr0KlzqveVEAFrmrAXQ+rrSKfg6dt7FI', CAST(840.35 AS DECIMAL(18,2)), CAST(100.00 AS DECIMAL(18,2)), 1, CAST(N'2025-12-04T19:45:00.057' AS DATETIME), CAST(N'2025-12-05T16:12:37.920' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`ConfiguracionIASistemas` OFF
;
SET IDENTITY_INSERT `dbo`.`EtiquetasPrompt` ON 

INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (1, N'producción', N'#ef4444', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (2, N'desarrollo', N'#3b82f6', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (3, N'testing', N'#f59e0b', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (4, N'documentación', N'#8b5cf6', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (5, N'optimizado', N'#10b981', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (6, N'experimental', N'#ec4899', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (7, N'aprobado', N'#14b8a6', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
INSERT `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`, `nombre`, `color`, `activo`, `fechaCreacion`) VALUES (8, N'revisión', N'#f97316', 1, CAST(N'2025-12-03T16:19:45.723' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`EtiquetasPrompt` OFF
;
SET IDENTITY_INSERT `dbo`.`Gerencias` ON 

INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (1, 1, N'Gerencia General', N'GG', N'gerencia.general@abcmasplus.com', CAST(N'2025-07-21T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (2, 2, N'Gerencia de Tecnología', N'GTECH', N'tecnologia@abcmasplus.com', CAST(N'2025-07-26T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (3, 3, N'Gerencia de Recursos Humanos', N'GRH', N'rrhh@abcmasplus.com', CAST(N'2025-07-31T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (4, 4, N'Gerencia de Finanzas', N'GFIN', N'finanzas@abcmasplus.com', CAST(N'2025-08-05T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (5, 5, N'Gerencia de Operaciones', N'GOPE', N'operaciones@abcmasplus.com', CAST(N'2025-08-10T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (6, 11, N'Gerencia de Marketing', N'GMKT', N'marketing@abcmasplus.com', CAST(N'2025-08-15T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (7, 12, N'Gerencia de Ventas', N'GVTA', N'ventas@abcmasplus.com', CAST(N'2025-08-20T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (8, NULL, N'Gerencia de Logística', N'GLOG', N'logistica@abcmasplus.com', CAST(N'2025-08-25T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (9, NULL, N'Gerencia de Calidad', N'GCAL', N'calidad@abcmasplus.com', CAST(N'2025-08-30T10:52:46.327' AS DATETIME), 1)
INSERT `dbo`.`Gerencias` (`idGerencia`, `idResponsable`, `gerencia`, `alias`, `correo`, `fechaCreacion`, `activo`) VALUES (10, NULL, N'Gerencia de Atención al Cliente', N'GACL', N'atencion.cliente@abcmasplus.com', CAST(N'2025-09-04T10:52:46.327' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`Gerencias` OFF
;
SET IDENTITY_INSERT `dbo`.`GerenciasRolesIA` ON 

INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (1, 1, 1, CAST(N'2025-07-21T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (2, 1, 2, CAST(N'2025-07-26T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (3, 2, 2, CAST(N'2025-07-26T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (4, 3, 2, CAST(N'2025-07-26T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (5, 3, 3, CAST(N'2025-07-31T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (6, 5, 3, CAST(N'2025-07-31T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (7, 2, 4, CAST(N'2025-08-05T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (8, 3, 4, CAST(N'2025-08-05T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (9, 5, 5, CAST(N'2025-08-10T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (10, 4, 6, CAST(N'2025-08-15T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (11, 5, 6, CAST(N'2025-08-15T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (12, 3, 7, CAST(N'2025-08-20T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (13, 5, 7, CAST(N'2025-08-20T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (14, 5, 8, CAST(N'2025-08-25T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (15, 6, 9, CAST(N'2025-08-30T10:52:46.353' AS DATETIME), 1)
INSERT `dbo`.`GerenciasRolesIA` (`idGerenciaRolIA`, `idRol`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (16, 5, 10, CAST(N'2025-09-04T10:52:46.353' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`GerenciasRolesIA` OFF
;
SET IDENTITY_INSERT `dbo`.`GerenciaUsuarios` ON 

INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (1, 1, 1, CAST(N'2025-07-31T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (2, 1, 2, CAST(N'2025-07-31T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (3, 2, 2, CAST(N'2025-08-05T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (4, 2, 8, CAST(N'2025-08-05T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (5, 3, 3, CAST(N'2025-08-10T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (6, 4, 4, CAST(N'2025-08-15T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (7, 5, 5, CAST(N'2025-08-20T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (8, 5, 8, CAST(N'2025-08-20T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (9, 6, 2, CAST(N'2025-08-25T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (10, 7, 4, CAST(N'2025-08-30T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (11, 8, 3, CAST(N'2025-09-04T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (12, 9, 6, CAST(N'2025-09-09T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (13, 10, 1, CAST(N'2025-09-14T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (14, 10, 4, CAST(N'2025-09-14T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (15, 10, 7, CAST(N'2025-09-14T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (16, 11, 6, CAST(N'2025-09-19T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (17, 12, 7, CAST(N'2025-09-24T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (18, 12, 10, CAST(N'2025-09-24T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (19, 13, 9, CAST(N'2025-09-29T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (20, 14, 8, CAST(N'2025-10-04T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (21, 15, 5, CAST(N'2025-10-09T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (22, 16, 10, CAST(N'2025-10-14T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (23, 17, 7, CAST(N'2025-10-19T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (24, 18, 6, CAST(N'2025-10-21T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (25, 19, 2, CAST(N'2025-10-24T10:52:46.340' AS DATETIME), 1)
INSERT `dbo`.`GerenciaUsuarios` (`idGerenciaUsuario`, `idUsuario`, `idGerencia`, `fechaAsignacion`, `activo`) VALUES (26, 20, 9, CAST(N'2025-10-26T10:52:46.340' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`GerenciaUsuarios` OFF
;
SET IDENTITY_INSERT `dbo`.`Iconos` ON 

INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (1, N'Home', N'fa-home', N'General', N'Inicio', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (2, N'Dashboard', N'fa-dashboard', N'General', N'Tablero de control', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (3, N'Tachometer', N'fa-tachometer', N'General', N'Velocímetro / Dashboard', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (4, N'Star', N'fa-star', N'General', N'Estrella', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (5, N'Heart', N'fa-heart', N'General', N'Corazón / Favoritos', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (6, N'Cog', N'fa-cog', N'General', N'Configuración', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (7, N'Wrench', N'fa-wrench', N'General', N'Herramientas', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (8, N'Settings', N'fa-gear', N'General', N'Configuración alternativa', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (9, N'Flag', N'fa-flag', N'General', N'Bandera / Marcador', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (10, N'Bell', N'fa-bell', N'General', N'Notificaciones', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (11, N'Calendar', N'fa-calendar', N'General', N'Calendario', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (12, N'Clock', N'fa-clock-o', N'General', N'Reloj', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (13, N'Globe', N'fa-globe', N'General', N'Mundo / Global', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (14, N'Map', N'fa-map', N'General', N'Mapa', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (15, N'Location', N'fa-map-marker', N'General', N'Ubicación', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (16, N'Search', N'fa-search', N'General', N'Búsqueda', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (17, N'Briefcase', N'fa-briefcase', N'Negocios', N'Maletín / Portafolio', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (18, N'Building', N'fa-building', N'Negocios', N'Edificio / Empresa', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (19, N'Shopping Cart', N'fa-shopping-cart', N'Negocios', N'Carrito de compras', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (20, N'DECIMAL(19,4)', N'fa-DECIMAL(19,4)', N'Negocios', N'Dinero', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (21, N'Credit Card', N'fa-credit-card', N'Negocios', N'Tarjeta de crédito', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (22, N'Dollar', N'fa-dollar', N'Negocios', N'Dólar / Finanzas', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (23, N'Bar Chart', N'fa-bar-chart', N'Negocios', N'Gráfico de barras', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (24, N'Line Chart', N'fa-line-chart', N'Negocios', N'Gráfico de líneas', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (25, N'Pie Chart', N'fa-pie-chart', N'Negocios', N'Gráfico circular', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (26, N'Calculator', N'fa-calculator', N'Negocios', N'Calculadora', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (27, N'Suitcase', N'fa-suitcase', N'Negocios', N'Maleta', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (28, N'Balance Scale', N'fa-balance-scale', N'Negocios', N'Balanza / Justicia', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (29, N'Code', N'fa-code', N'Tecnología', N'Código / Programación', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (30, N'Terminal', N'fa-terminal', N'Tecnología', N'Terminal / Consola', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (31, N'Database', N'fa-database', N'Tecnología', N'Base de datos', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (32, N'Server', N'fa-server', N'Tecnología', N'Servidor', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (33, N'Desktop', N'fa-desktop', N'Tecnología', N'Computadora de escritorio', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (34, N'Laptop', N'fa-laptop', N'Tecnología', N'Laptop', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (35, N'Mobile', N'fa-mobile', N'Tecnología', N'Móvil / Celular', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (36, N'Tablet', N'fa-tablet', N'Tecnología', N'Tableta', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (37, N'Keyboard', N'fa-keyboard-o', N'Tecnología', N'Teclado', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (38, N'Plug', N'fa-plug', N'Tecnología', N'Conector / Plugin', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (39, N'Microchip', N'fa-microchip', N'Tecnología', N'Microchip / Hardware', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (40, N'USB', N'fa-usb', N'Tecnología', N'USB', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (41, N'Wifi', N'fa-wifi', N'Tecnología', N'WiFi / Conexión', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (42, N'Cloud', N'fa-cloud', N'Tecnología', N'Nube', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (43, N'Cloud Upload', N'fa-cloud-upload', N'Tecnología', N'Subir a la nube', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (44, N'Cloud Download', N'fa-cloud-download', N'Tecnología', N'Descargar de la nube', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (45, N'Envelope', N'fa-envelope', N'Comunicación', N'Correo electrónico', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (46, N'Comment', N'fa-comment', N'Comunicación', N'Comentario', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (47, N'Comments', N'fa-comments', N'Comunicación', N'Comentarios / Chat', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (48, N'Phone', N'fa-phone', N'Comunicación', N'Teléfono', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (49, N'Fax', N'fa-fax', N'Comunicación', N'Fax', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (50, N'Bullhorn', N'fa-bullhorn', N'Comunicación', N'Megáfono / Anuncios', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (51, N'Rss', N'fa-rss', N'Comunicación', N'RSS / Noticias', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (52, N'Inbox', N'fa-inbox', N'Comunicación', N'Bandeja de entrada', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (53, N'Paperclip', N'fa-paperclip', N'Comunicación', N'Adjunto', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (54, N'Share', N'fa-share', N'Comunicación', N'Compartir', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (55, N'File', N'fa-file', N'Archivos', N'Archivo', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (56, N'File TEXT', N'fa-file-TEXT', N'Archivos', N'Archivo de texto', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (57, N'File PDF', N'fa-file-pdf-o', N'Archivos', N'Archivo PDF', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (58, N'File Excel', N'fa-file-excel-o', N'Archivos', N'Archivo Excel', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (59, N'File Word', N'fa-file-word-o', N'Archivos', N'Archivo Word', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (60, N'File LONGBLOB', N'fa-file-LONGBLOB-o', N'Archivos', N'Archivo de imagen', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (61, N'File Archive', N'fa-file-archive-o', N'Archivos', N'Archivo comprimido', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (62, N'File Code', N'fa-file-code-o', N'Archivos', N'Archivo de código', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (63, N'Folder', N'fa-folder', N'Archivos', N'Carpeta', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (64, N'Folder Open', N'fa-folder-open', N'Archivos', N'Carpeta abierta', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (65, N'Copy', N'fa-copy', N'Archivos', N'Copiar', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (66, N'Paste', N'fa-paste', N'Archivos', N'Pegar', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (67, N'Save', N'fa-save', N'Archivos', N'Guardar', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (68, N'Download', N'fa-download', N'Archivos', N'Descargar', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (69, N'Upload', N'fa-upload', N'Archivos', N'Subir', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (70, N'User', N'fa-user', N'Usuarios', N'Usuario', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (71, N'Users', N'fa-users', N'Usuarios', N'Usuarios / Grupo', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (72, N'User Circle', N'fa-user-circle', N'Usuarios', N'Usuario con círculo', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (73, N'User Plus', N'fa-user-plus', N'Usuarios', N'Agregar usuario', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (74, N'User Times', N'fa-user-times', N'Usuarios', N'Eliminar usuario', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (75, N'Id Card', N'fa-id-card', N'Usuarios', N'Identificación', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (76, N'Address Card', N'fa-address-card', N'Usuarios', N'Tarjeta de contacto', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (77, N'Child', N'fa-child', N'Usuarios', N'Niño / Dependiente', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (78, N'Group', N'fa-group', N'Usuarios', N'Grupo / Team', 1, CAST(N'2025-12-02T09:47:31.150' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (79, N'Puzzle Piece', N'fa-puzzle-piece', N'Sistema', N'Módulo / Plugin', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (80, N'Th', N'fa-th', N'Sistema', N'Cuadrícula / Grid', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (81, N'Th List', N'fa-th-list', N'Sistema', N'Lista', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (82, N'List', N'fa-list', N'Sistema', N'Lista simple', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (83, N'Bars', N'fa-bars', N'Sistema', N'Menú hamburguesa', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (84, N'Lock', N'fa-lock', N'Sistema', N'Candado / Seguridad', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (85, N'Unlock', N'fa-unlock', N'Sistema', N'Desbloquear', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (86, N'Key', N'fa-key', N'Sistema', N'Llave / Autenticación', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (87, N'Shield', N'fa-shield', N'Sistema', N'Escudo / Protección', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (88, N'Power Off', N'fa-power-off', N'Sistema', N'Apagar / Cerrar sesión', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (89, N'Sign In', N'fa-sign-in', N'Sistema', N'Iniciar sesión', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (90, N'Sign Out', N'fa-sign-out', N'Sistema', N'Cerrar sesión', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (91, N'Eye', N'fa-eye', N'Sistema', N'Ver / Mostrar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (92, N'Eye Slash', N'fa-eye-slash', N'Sistema', N'Ocultar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (93, N'Print', N'fa-print', N'Sistema', N'Imprimir', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (94, N'Trash', N'fa-trash', N'Sistema', N'Eliminar / Papelera', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (95, N'Edit', N'fa-edit', N'Sistema', N'Editar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (96, N'Plus', N'fa-plus', N'Sistema', N'Añadir / Más', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (97, N'Minus', N'fa-minus', N'Sistema', N'Menos / Quitar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (98, N'Check', N'fa-check', N'Sistema', N'Verificar / OK', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (99, N'Times', N'fa-times', N'Sistema', N'Cerrar / Cancelar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
;
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (100, N'Refresh', N'fa-refresh', N'Sistema', N'Actualizar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (101, N'Sync', N'fa-sync', N'Sistema', N'Sincronizar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (102, N'Filter', N'fa-filter', N'Sistema', N'Filtrar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (103, N'Sort', N'fa-sort', N'Sistema', N'Ordenar', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (104, N'Question Circle', N'fa-question-circle', N'Sistema', N'Ayuda', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (105, N'Info Circle', N'fa-info-circle', N'Sistema', N'Información', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (106, N'Exclamation Triangle', N'fa-exclamation-triangle', N'Sistema', N'Advertencia', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (107, N'Bookmark', N'fa-bookmark', N'Sistema', N'Marcador', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (108, N'Tag', N'fa-tag', N'Sistema', N'Etiqueta', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
INSERT `dbo`.`Iconos` (`idIcono`, `nombre`, `clase`, `categoria`, `descripcion`, `activo`, `fechaCreacion`) VALUES (109, N'Tags', N'fa-tags', N'Sistema', N'Etiquetas', 1, CAST(N'2025-12-02T09:47:31.153' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`Iconos` OFF
;
SET IDENTITY_INSERT `dbo`.`knowledge_categories` ON 

INSERT `dbo`.`knowledge_categories` (`id`, `name`, `display_name`, `description`, `icon`, `active`, `created_at`, `updated_at`) VALUES (1, N'PROCESOS', N'Procesos', N'Procesos y procedimientos internos', N'📋', 1, CAST(N'2025-11-29T21:48:21.7166667' AS DATETIME), CAST(N'2025-11-29T21:48:21.7166667' AS DATETIME))
INSERT `dbo`.`knowledge_categories` (`id`, `name`, `display_name`, `description`, `icon`, `active`, `created_at`, `updated_at`) VALUES (2, N'POLITICAS', N'Politicas', N'Políticas de la empresa', N'📜', 1, CAST(N'2025-11-29T21:48:21.7166667' AS DATETIME), CAST(N'2025-11-29T21:48:21.7166667' AS DATETIME))
INSERT `dbo`.`knowledge_categories` (`id`, `name`, `display_name`, `description`, `icon`, `active`, `created_at`, `updated_at`) VALUES (3, N'FAQS', N'Faqs', N'Preguntas frecuentes', N'❓', 1, CAST(N'2025-11-29T21:48:21.7166667' AS DATETIME), CAST(N'2025-11-29T21:48:21.7166667' AS DATETIME))
INSERT `dbo`.`knowledge_categories` (`id`, `name`, `display_name`, `description`, `icon`, `active`, `created_at`, `updated_at`) VALUES (4, N'CONTACTOS', N'Contactos', N'Información de contacto de departamentos', N'📞', 1, CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME))
INSERT `dbo`.`knowledge_categories` (`id`, `name`, `display_name`, `description`, `icon`, `active`, `created_at`, `updated_at`) VALUES (5, N'SISTEMAS', N'Sistemas', N'Información sobre sistemas y herramientas', N'💻', 1, CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME))
INSERT `dbo`.`knowledge_categories` (`id`, `name`, `display_name`, `description`, `icon`, `active`, `created_at`, `updated_at`) VALUES (6, N'RECURSOS_HUMANOS', N'Recursos Humanos', N'Temas de RRHH: vacaciones, permisos, beneficios', N'👥', 1, CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME))
INSERT `dbo`.`knowledge_categories` (`id`, `name`, `display_name`, `description`, `icon`, `active`, `created_at`, `updated_at`) VALUES (7, N'BASE_DATOS', N'Base Datos', N'Información sobre tablas y estructura de la base de datos', N'🗄️', 1, CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`knowledge_categories` OFF
;
SET IDENTITY_INSERT `dbo`.`knowledge_entries` ON 

INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (1, 1, N'¿Cómo solicito vacaciones?', N'🏖️ **Para solicitar vacaciones:**

1️⃣ Ingresar al portal de empleados con tu usuario y contraseña
2️⃣ Ir a la sección ''Solicitudes > Vacaciones''
3️⃣ Llenar el formulario indicando las fechas deseadas
4️⃣ La solicitud debe hacerse con al menos **15 días de anticipación** ⏰
5️⃣ Esperar aprobación de tu supervisor directo ✅
6️⃣ Recibirás notificación por email cuando sea aprobada 📧', N'`"vacaciones", "solicitar", "pedir", "días libres", "descanso", "ausentarse"`', N'`"/help"`', 2, 1, CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7200000' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (2, 1, N'¿Cómo creo un ticket de soporte?', N'🎫 **Crear un ticket de soporte:**

Tienes 3 opciones:

📱 **Opción 1:** Usar el comando /crear_ticket en este bot
📧 **Opción 2:** Enviar email a soporte@empresa.com
☎️ **Opción 3:** Llamar a la extensión 123

⚠️ **Incluye siempre:**
• Descripción del problema
• Departamento
• Nivel de urgencia (🔵 bajo / 🟡 medio / 🔴 alto)', N'`"ticket", "soporte", "ayuda", "problema", "incidencia", "reporte"`', N'`"/crear_ticket"`', 3, 1, CAST(N'2025-11-29T21:48:21.7233333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7233333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (3, 1, N'¿Cómo reporto una ausencia?', N'Para reportar una ausencia:
1. Si es planificada: solicítala con al menos 48 horas de anticipación en el portal de empleados
2. Si es imprevista (enfermedad, emergencia): notifica a tu supervisor por WhatsApp o llamada antes de las 9:00 AM
3. Presenta justificante médico dentro de las 48 horas siguientes', N'`"ausencia", "falta", "no asistir", "enfermedad", "permiso"`', N'[]', 2, 1, CAST(N'2025-11-29T21:48:21.7233333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7233333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (4, 2, N'¿Qué políticas tiene la empresa?', N'📋 **Políticas de la Empresa:**

Tenemos políticas en las siguientes áreas:

⏰ **Horarios de Trabajo:**
• Lunes a Viernes: 8:00 AM - 6:00 PM
• 9 horas diarias, 45 horas semanales
• Pregunta: `/ia ¿Cuál es el horario de trabajo?`

🏖️ **Vacaciones:**
• 15-25 días según antigüedad
• Pregunta: `/ia ¿Cuántos días de vacaciones tengo?`

🏠 **Trabajo Remoto:**
• Hasta 2 días por semana (modalidad híbrida)
• Pregunta: `/ia ¿Cuál es la política de trabajo remoto?`

💡 **Tip:** Haz preguntas específicas sobre cada política para obtener información detallada', N'`"políticas", "política", "reglas", "normas", "reglamento", "normativa", "directrices"`', N'`"/help", "/ia"`', 3, 1, CAST(N'2025-11-29T21:48:21.7233333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7233333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (5, 2, N'¿Cuál es el horario de trabajo?', N'El horario laboral estándar es:
• Lunes a Viernes: 8:00 AM - 6:00 PM
• Hora de almuerzo: 12:00 PM - 2:00 PM (1 hora flexible)
• Total: 9 horas diarias, 45 horas semanales

Algunos departamentos tienen horarios especiales. Consulta con tu supervisor.', N'`"horario", "hora", "entrada", "salida", "jornada", "trabajo", "políticas", "política"`', N'[]', 2, 1, CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (6, 2, N'¿Cuántos días de vacaciones tengo al año?', N'Los días de vacaciones dependen de tu antigüedad:
• 0-1 año: 15 días
• 1-5 años: 20 días
• Más de 5 años: 25 días

Los días se acumulan por año trabajado y deben usarse antes del 31 de diciembre. No se pueden transferir al siguiente año salvo autorización especial.', N'`"vacaciones", "días", "cuántos", "derecho", "corresponden", "políticas", "política"`', N'[]', 2, 1, CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (7, 2, N'¿Cuál es la política de trabajo remoto?', N'Política de trabajo remoto (Home Office):
• Disponible para puestos elegibles según aprobación del supervisor
• Máximo 2 días por semana en modalidad híbrida
• Requiere solicitud previa en el portal con 48 horas de anticipación
• Debes estar disponible en horario laboral y con conexión estable
• Aplican mismas reglas de productividad y entregas', N'`"remoto", "home office", "casa", "teletrabajo", "virtual", "políticas", "política"`', N'[]', 1, 1, CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (8, 3, N'¿Qué hacer si olvido mi contraseña?', N'🔑 **Recuperar contraseña:**

1️⃣ En la pantalla de login, haz clic en ''¿Olvidaste tu contraseña?''
2️⃣ Ingresa tu email corporativo 📧
3️⃣ Recibirás un enlace para resetearla 🔗
4️⃣ Si no recibes el email en 5 minutos, contacta a IT (ext. 123) ⏱️

💡 **Tip:** También puedes crear un ticket usando /crear_ticket', N'`"contraseña", "password", "olvidé", "resetear", "cambiar", "recuperar"`', N'`"/crear_ticket"`', 3, 1, CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (9, 3, N'¿Cómo accedo al portal de empleados?', N'Para acceder al portal de empleados:
1. Ingresa a: https://portal.empresa.com
2. Usa tu email corporativo como usuario
3. Tu contraseña inicial es tu cédula (cámbiala en el primer ingreso)
4. Si tienes problemas, contacta a IT', N'`"portal", "acceso", "ingresar", "login", "empleados"`', N'[]', 2, 1, CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (10, 3, N'¿Dónde encuentro mi recibo de pago?', N'Tu recibo de pago está disponible en:
1. Portal de empleados > Sección ''Nómina''
2. Se publica el último día hábil de cada mes
3. Puedes descargar recibos de los últimos 12 meses
4. Para recibos más antiguos, solicita en RRHH', N'`"recibo", "pago", "nómina", "sueldo", "salario", "comprobante"`', N'[]', 2, 1, CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (11, 4, N'¿Cómo contacto al departamento de IT?', N'Contactos del departamento de IT:
• Extensión: 123
• Email: it@empresa.com
• WhatsApp: +123456789
• Horario de atención: Lunes a Viernes 8AM-6PM
• Para urgencias fuera de horario: crear ticket marcando como ''Urgente''', N'`"it", "sistemas", "soporte técnico", "tecnología", "contacto"`', N'`"/crear_ticket"`', 2, 1, CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), CAST(N'2025-11-29T21:48:21.7333333' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (12, 4, N'¿Cómo contacto a Recursos Humanos?', N'Contactos de Recursos Humanos:
• Extensión: 456
• Email: rrhh@empresa.com
• Oficina: Edificio Principal, 2do piso
• Horario de atención: Lunes a Viernes 8AM-5PM
• Para temas urgentes, solicitar cita previa', N'`"rrhh", "recursos humanos", "personal", "contacto", "talento"`', N'[]', 2, 1, CAST(N'2025-11-29T21:48:21.7366667' AS DATETIME), CAST(N'2025-11-29T21:48:21.7366667' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (13, 4, N'¿A quién contacto para temas de nómina?', N'Contactos para temas de nómina:
• Departamento: RRHH - Área de Nómina
• Email: nomina@empresa.com
• Extensión: 789
• Horario: Lunes a Viernes 8AM-12PM y 2PM-5PM
• Días de corte: 25 de cada mes', N'`"nómina", "pago", "sueldo", "salario", "planilla"`', N'[]', 2, 1, CAST(N'2025-11-29T21:48:21.7366667' AS DATETIME), CAST(N'2025-11-29T21:48:21.7366667' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (14, 5, N'¿Qué comandos puedo usar en este bot?', N'Comandos disponibles en el bot:
• /help - Ver ayuda general
• /ia <consulta> - Hacer consultas con IA
• /stats - Ver estadísticas del sistema
• /crear_ticket - Crear ticket de soporte
• /register - Registrarse en el sistema

Usa /help para ver la lista completa con descripciones.', N'`"comandos", "ayuda", "usar", "bot", "funciones", "opciones"`', N'`"/help"`', 3, 1, CAST(N'2025-11-29T21:48:21.7366667' AS DATETIME), CAST(N'2025-11-29T21:48:21.7366667' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (15, 5, N'¿Cómo me registro en el bot?', N'Para registrarte en el bot:
1. Usa el comando /register
2. El bot te solicitará tu código de verificación
3. Obtén tu código desde el Portal de Consola de Monitoreo
4. Envía el código al bot usando /verify <codigo>
5. Una vez verificado, podrás usar todas las funciones', N'`"registro", "registrar", "verificar", "activar", "cuenta"`', N'`"/register", "/verify"`', 3, 1, CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (16, 6, N'¿Qué beneficios tengo como empleado?', N'Beneficios para empleados:
• Seguro médico privado (cobertura familiar)
• Seguro de vida
• Bono anual por desempeño
• 15-25 días de vacaciones (según antigüedad)
• Capacitaciones y desarrollo profesional
• Descuentos en comercios afiliados
• Bono de alimentación

Consulta el manual de empleados para detalles completos.', N'`"beneficios", "ventajas", "seguro", "bono", "prestaciones"`', N'[]', 1, 1, CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (17, 6, N'¿Cómo solicito una constancia de trabajo?', N'Para solicitar una constancia de trabajo:
1. Envía email a rrhh@empresa.com indicando el tipo de constancia
2. Tipos disponibles: laboral, salarial, antigüedad
3. Tiempo de entrega: 48 horas hábiles
4. Retiro en oficina de RRHH con identificación
5. Servicio gratuito para empleados activos', N'`"constancia", "certificado", "carta", "trabajo", "laboral"`', N'[]', 1, 1, CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (18, 6, N'¿Qué hacer en caso de emergencia en la oficina?', N'En caso de emergencia:
1. Mantén la calma y evalúa la situación
2. Emergencia médica: llama a la enfermería (ext. 911) o 911
3. Incendio: activa alarma, evacua por salidas de emergencia
4. Sismo: protégete bajo escritorio, evacua cuando cese
5. Punto de reunión: Estacionamiento principal
6. Brigadas de emergencia identificadas con chaleco naranja', N'`"emergencia", "urgencia", "peligro", "evacuación", "seguridad"`', N'[]', 3, 1, CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (19, 7, N'¿Qué información contiene la tabla Ventas?', N'📊 **Tabla Ventas** (`Pruebas`.`dbo`.`Ventas`)

Contiene información sobre transacciones de ventas:

🔑 **customer_id** → Identificador único del cliente
📦 **product_name** → Nombre del producto vendido
🔢 **quantity** → Cantidad de unidades vendidas
💵 **unit_price** → Precio unitario del producto
💰 **total_price** → Precio total (quantity × unit_price)

✨ **Úsala para:**
• Consultas sobre ventas
• Productos más vendidos
• Ingresos totales
• Análisis de clientes
• Reportes financieros', N'`"ventas", "tabla ventas", "productos", "clientes", "transacciones", "customer_id", "product_name", "quantity", "unit_price", "total_price", "base de datos", "bd", "tabla", "campos"`', N'`"/ia", "/query"`', 2, 1, CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (20, 7, N'¿Qué tablas están disponibles en la base de datos?', N'🗄️ **Tablas Disponibles:**

📊 **1. Ventas** (`Pruebas`.`dbo`.`Ventas`)
   • Contiene: Transacciones de ventas con info de clientes, productos, cantidades y precios
   • Campos: customer_id, product_name, quantity, unit_price, total_price
   • Usa para: Ventas, análisis de productos, reportes financieros

💡 **¿Cómo consultar?**
Usa el comando `/ia` seguido de tu pregunta. El sistema generará automáticamente la consulta SQL necesaria ✨', N'`"tablas", "base de datos", "bd", "esquema", "estructura", "disponibles", "qué tablas", "cuáles tablas", "acceso"`', N'`"/ia"`', 3, 1, CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), N'migration_001')
INSERT `dbo`.`knowledge_entries` (`id`, `category_id`, `question`, `answer`, `keywords`, `related_commands`, `priority`, `active`, `created_at`, `updated_at`, `created_by`) VALUES (21, 7, N'¿Cómo puedo consultar información de la base de datos?', N'🤖 **Consultar la base de datos es súper fácil:**

Simplemente usa `/ia` + tu pregunta en lenguaje natural

📝 **Ejemplos:**

🔢 `/ia ¿Cuántas ventas hay?`
   → Cuenta total de registros

🏆 `/ia ¿Cuál es el producto más vendido?`
   → Análisis de productos

👤 `/ia Muéstrame las ventas del cliente 123`
   → Filtrado por cliente

💰 `/ia ¿Cuál es el total de ingresos?`
   → Suma de ventas

✨ **El sistema hace esto por ti:**
1️⃣ Analiza tu pregunta
2️⃣ Genera el SQL automáticamente
3️⃣ Ejecuta la consulta de forma segura
4️⃣ Te responde en lenguaje natural

💡 **No necesitas saber SQL**, solo pregunta naturalmente', N'`"consultar", "query", "preguntar", "datos", "información", "cómo consulto", "cómo pregunto", "usar ia", "comando ia"`', N'`"/ia", "/help"`', 3, 1, CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), CAST(N'2025-11-29T21:48:21.7400000' AS DATETIME), N'migration_001')
SET IDENTITY_INSERT `dbo`.`knowledge_entries` OFF
;
SET IDENTITY_INSERT `dbo`.`LogOperaciones` ON 

INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (1, 1, 1, 123456789, N'juan_perez', N'{"descripcion": "Problema con servidor"}', N'EXITOSO', NULL, 234, NULL, CAST(N'2025-10-29T09:00:55.440' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (2, 2, 8, 987654321, N'maria_lopez', N'{}', N'EXITOSO', NULL, 1567, NULL, CAST(N'2025-10-29T10:00:55.440' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (3, 8, 34, 456789123, N'laura_torres', N'{"pregunta": "¿Cómo crear un ticket?"}', N'EXITOSO', NULL, 456, NULL, CAST(N'2025-10-29T10:30:55.440' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (4, 10, 7, 789123456, N'carmen_ruiz', N'{"numero": "TK-001"}', N'DENEGADO', N'Usuario sin permisos para eliminar tickets', 0, NULL, CAST(N'2025-10-29T10:45:55.440' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (5, 5, 6, 321654987, N'luis_fernandez', N'{"numero": "TK-002", "area": "Tecnología"}', N'EXITOSO', NULL, 678, NULL, CAST(N'2025-10-29T10:50:55.440' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10001, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 16616, NULL, CAST(N'2025-11-23T17:27:33.900' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10002, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 21616, NULL, CAST(N'2025-11-26T16:17:29.907' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10003, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 20261, NULL, CAST(N'2025-11-26T16:19:46.883' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10004, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 19144, NULL, CAST(N'2025-11-26T16:31:01.863' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10005, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "hola"}', N'EXITOSO', NULL, 18735, NULL, CAST(N'2025-11-26T16:50:29.250' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10006, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "HOLA"}', N'EXITOSO', NULL, 19547, NULL, CAST(N'2025-11-26T17:06:04.560' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10007, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 20654, NULL, CAST(N'2025-11-26T17:33:03.923' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10008, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 18137, NULL, CAST(N'2025-11-26T17:37:51.517' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10009, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 18810, NULL, CAST(N'2025-11-26T19:09:41.803' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10010, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que se han vendido?"}', N'EXITOSO', NULL, 48043, NULL, CAST(N'2025-11-26T19:13:13.823' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10011, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuando productos existen en total?"}', N'ERROR', N'Can''t parse entities: can''t find end of the entity starting at byte offset 38', 18318, NULL, CAST(N'2025-11-26T19:15:33.847' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10012, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuando productos existen en total en la tabla productos?"}', N'EXITOSO', NULL, 16865, NULL, CAST(N'2025-11-26T19:16:21.967' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10013, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuales son los productos con mas stock?"}', N'EXITOSO', NULL, 14688, NULL, CAST(N'2025-11-26T19:24:17.260' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10014, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Solo regresa los primeros 5 productos con mas stock"}', N'ERROR', N'Can''t parse entities: can''t find end of the entity starting at byte offset 228', 30815, NULL, CAST(N'2025-11-26T19:27:04.867' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10015, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Solo regresa los primeros 5 productos con mas stock"}', N'EXITOSO', NULL, 28524, NULL, CAST(N'2025-11-26T19:27:39.753' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10016, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuantas Memoria USB hay?"}', N'EXITOSO', NULL, 21926, NULL, CAST(N'2025-11-26T19:29:39.130' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10017, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Como me llamo?"}', N'EXITOSO', NULL, 46625, NULL, CAST(N'2025-11-26T19:33:54.370' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10018, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Genera un hola mundo en javascritp"}', N'EXITOSO', NULL, 24023, NULL, CAST(N'2025-11-26T19:51:32.480' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10019, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cual fue la ulitma pregunta?"}', N'EXITOSO', NULL, 21893, NULL, CAST(N'2025-11-26T19:52:06.237' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10020, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 17749, NULL, CAST(N'2025-11-26T23:45:41.740' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10021, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola, como estas"}', N'EXITOSO', NULL, 18001, NULL, CAST(N'2025-11-26T23:46:15.030' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10022, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Algo"}', N'EXITOSO', NULL, 15457, NULL, CAST(N'2025-11-27T00:11:06.710' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10023, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "en la bd de productos, tenemos algo de la marca huawei?"}', N'EXITOSO', NULL, 22465, NULL, CAST(N'2025-11-27T00:12:40.577' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10024, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "en la bd de productos, tenemos algo de la marca dell?"}', N'EXITOSO', NULL, 18168, NULL, CAST(N'2025-11-27T00:20:52.800' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10025, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuánto es 81 dólares a pesos mexicanos"}', N'EXITOSO', NULL, 40429, NULL, CAST(N'2025-11-27T00:28:39.383' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10026, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuánto es 81 dólares a pesos mexicanos"}', N'EXITOSO', NULL, 69401, NULL, CAST(N'2025-11-27T00:29:57.243' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10027, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 16035, NULL, CAST(N'2025-11-27T11:50:14.870' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10028, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuál es el producto con más stock?"}', N'EXITOSO', NULL, 21488, NULL, CAST(N'2025-11-27T11:51:20.917' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10029, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "hola"}', N'EXITOSO', NULL, 17274, NULL, CAST(N'2025-11-27T17:08:19.410' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10030, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuantos usuarios existen?"}', N'EXITOSO', NULL, 15567, NULL, CAST(N'2025-11-27T18:38:13.860' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10031, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuantos usuarios existen?"}', N'EXITOSO', NULL, 14917, NULL, CAST(N'2025-11-27T18:42:17.407' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10032, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola, como estas?"}', N'ERROR', N'cannot access local variable ''UserManager'' where it is not associated with a value', 816, NULL, CAST(N'2025-11-27T18:42:32.823' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10033, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola, como estas?"}', N'ERROR', N'cannot access local variable ''UserManager'' where it is not associated with a value', 820, NULL, CAST(N'2025-11-27T18:42:54.967' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10034, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola, como estas?"}', N'EXITOSO', NULL, 13807, NULL, CAST(N'2025-11-27T18:45:29.607' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10035, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola, como estas?"}', N'EXITOSO', NULL, 15603, NULL, CAST(N'2025-11-27T18:49:05.220' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10036, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola, como estas?"}', N'EXITOSO', NULL, 33755, NULL, CAST(N'2025-11-27T19:24:29.937' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10037, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "cual es el producto mas vendido?"}', N'EXITOSO', NULL, 23758, NULL, CAST(N'2025-11-27T19:26:43.183' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10038, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 22360, NULL, CAST(N'2025-11-28T19:40:19.810' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10039, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Necesito vacaciones"}', N'EXITOSO', NULL, 20973, NULL, CAST(N'2025-11-28T19:41:11.413' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10040, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Holaa"}', N'EXITOSO', NULL, 24876, NULL, CAST(N'2025-11-28T19:55:27.670' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10041, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Necesito vacaciones"}', N'EXITOSO', NULL, 31005, NULL, CAST(N'2025-11-28T19:56:10.987' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10042, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "¿omo solicito vacaciones?"}', N'EXITOSO', NULL, 28816, NULL, CAST(N'2025-11-28T19:57:30.817' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10043, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cua es el horario de trabajo?"}', N'EXITOSO', NULL, 29819, NULL, CAST(N'2025-11-28T19:59:07.213' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10044, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Tuve una emergencia en la oficina que debo hacer?"}', N'EXITOSO', NULL, 43347, NULL, CAST(N'2025-11-28T20:02:13.437' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10045, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cual es el producto mas vendido hasta la fecha?"}', N'EXITOSO', NULL, 49439, NULL, CAST(N'2025-11-28T20:03:56.120' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10046, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "A que producto le ganamos menos? \nA que producto le ganamos mas?"}', N'EXITOSO', NULL, 37235, NULL, CAST(N'2025-11-28T20:10:43.070' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10047, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "A que producto le ganamos menos? \nA que producto le ganamos mas?"}', N'EXITOSO', NULL, 80903, NULL, CAST(N'2025-11-28T20:12:53.697' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10048, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "A que producto le ganamos menos?"}', N'EXITOSO', NULL, 50123, NULL, CAST(N'2025-11-28T20:13:56.797' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10049, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 13007, NULL, CAST(N'2025-11-28T20:24:49.910' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10050, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10651, NULL, CAST(N'2025-11-28T20:54:34.150' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10051, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que es un ticket?"}', N'EXITOSO', NULL, 23976, NULL, CAST(N'2025-11-28T20:57:08.937' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10052, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que onda"}', N'EXITOSO', NULL, 20148, NULL, CAST(N'2025-11-28T21:06:48.030' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10053, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10210, NULL, CAST(N'2025-11-29T11:50:07.097' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10054, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 14280, NULL, CAST(N'2025-11-29T12:30:38.557' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10055, 3, 34, 6234533339, NULL, N'{"query": "Te quiero"}', N'EXITOSO', NULL, 24309, NULL, CAST(N'2025-11-29T12:35:20.113' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10056, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 9864, NULL, CAST(N'2025-11-29T12:44:28.333' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10057, 3, 34, 6234533339, NULL, N'{"query": "Hola"}', N'EXITOSO', NULL, 8603, NULL, CAST(N'2025-11-29T12:44:46.000' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10058, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que día es hoy?"}', N'EXITOSO', NULL, 47477, NULL, CAST(N'2025-11-29T12:45:33.770' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10059, 3, 34, 6234533339, NULL, N'{"query": "Hablame de las políticas de la empresa"}', N'EXITOSO', NULL, 6327, NULL, CAST(N'2025-11-29T12:45:40.100' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10060, 3, 34, 6234533339, NULL, N'{"query": "Políticas de la empresa"}', N'EXITOSO', NULL, 7291, NULL, CAST(N'2025-11-29T12:50:36.967' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10061, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hablame de las políticas de las empresa"}', N'EXITOSO', NULL, 6759, NULL, CAST(N'2025-11-29T12:50:44.363' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10062, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 8269, NULL, CAST(N'2025-11-29T15:46:58.790' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10063, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Dame las políticas de la empresa"}', N'EXITOSO', NULL, 23753, NULL, CAST(N'2025-11-29T15:47:34.207' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10064, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que otras cosas sabes de la empresa?"}', N'EXITOSO', NULL, 19321, NULL, CAST(N'2025-11-29T16:04:40.863' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10065, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10928, NULL, CAST(N'2025-11-29T21:51:05.280' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10066, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Necesito vacaciones"}', N'EXITOSO', NULL, 28455, NULL, CAST(N'2025-11-29T21:51:48.933' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10067, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Dame el producto más vendido"}', N'EXITOSO', NULL, 20373, NULL, CAST(N'2025-11-29T21:52:35.373' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10068, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuál es el producto más caro?"}', N'EXITOSO', NULL, 22394, NULL, CAST(N'2025-11-29T21:54:38.470' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10069, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Quiero vacaciones"}', N'EXITOSO', NULL, 26129, NULL, CAST(N'2025-11-30T10:14:06.067' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10070, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 9763, NULL, CAST(N'2025-11-30T10:52:53.510' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10071, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que es una cuenta T?"}', N'EXITOSO', NULL, 8452, NULL, CAST(N'2025-11-30T10:53:24.517' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10072, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Analisa la venta"}', N'EXITOSO', NULL, 26219, NULL, CAST(N'2025-11-30T10:54:34.263' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10073, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cuál es el producto más vendido?"}', N'EXITOSO', NULL, 15880, NULL, CAST(N'2025-11-30T10:55:09.370' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10074, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 7536, NULL, CAST(N'2025-11-30T12:39:04.007' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10075, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Dame las políticas de la empresa"}', N'EXITOSO', NULL, 19639, NULL, CAST(N'2025-11-30T12:39:32.447' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10076, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 8119, NULL, CAST(N'2025-11-30T21:18:05.180' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10077, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 7533, NULL, CAST(N'2025-11-30T22:28:33.020' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10078, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 8709, NULL, CAST(N'2025-11-30T22:29:09.130' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10079, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 8869, NULL, CAST(N'2025-11-30T22:33:26.807' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10080, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 7800, NULL, CAST(N'2025-11-30T22:55:11.110' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10081, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Cómo solicito vacaciones?"}', N'EXITOSO', NULL, 16390, NULL, CAST(N'2025-11-30T22:57:51.420' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10082, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que otras cosas sabes de la empresa?"}', N'EXITOSO', NULL, 28469, NULL, CAST(N'2025-11-30T22:58:46.920' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10083, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "No recuerdo mi contraseña"}', N'EXITOSO', NULL, 23955, NULL, CAST(N'2025-11-30T23:04:02.753' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10084, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que pasa con la nómina"}', N'EXITOSO', NULL, 26779, NULL, CAST(N'2025-11-30T23:07:18.573' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10085, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Necesito una constancia de trabajo"}', N'EXITOSO', NULL, 19422, NULL, CAST(N'2025-11-30T23:09:09.230' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10086, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Puedo tener trabajo remoto"}', N'EXITOSO', NULL, 21984, NULL, CAST(N'2025-11-30T23:10:50.970' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10087, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Dónde encuentro mi recibo de pago?"}', N'EXITOSO', NULL, 20747, NULL, CAST(N'2025-11-30T23:13:33.660' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10088, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 9563, NULL, CAST(N'2025-12-01T10:38:21.497' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10089, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 7342, NULL, CAST(N'2025-12-01T10:57:17.930' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10090, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 9465, NULL, CAST(N'2025-12-01T11:02:25.453' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10091, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 12633, NULL, CAST(N'2025-12-01T11:07:57.193' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10092, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 11196, NULL, CAST(N'2025-12-01T11:24:06.477' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10093, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que sabes sobre contactos?"}', N'EXITOSO', NULL, 19806, NULL, CAST(N'2025-12-01T11:25:54.567' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10094, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que sabes de faqs"}', N'EXITOSO', NULL, 13359, NULL, CAST(N'2025-12-01T11:28:14.740' AS DATETIME))
;
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10095, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Si, hay una categoría que se llama Faqs que sabes sobre ello"}', N'EXITOSO', NULL, 24890, NULL, CAST(N'2025-12-01T11:29:06.177' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10096, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 18122, NULL, CAST(N'2025-12-01T15:20:08.283' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10097, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 14653, NULL, CAST(N'2025-12-01T15:50:23.463' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10098, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 9712, NULL, CAST(N'2025-12-01T15:51:18.550' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10099, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10589, NULL, CAST(N'2025-12-01T20:16:55.390' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10100, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Se me olvidó mi contraseña"}', N'EXITOSO', NULL, 21291, NULL, CAST(N'2025-12-01T21:12:42.920' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10101, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Crear ticket"}', N'EXITOSO', NULL, 24802, NULL, CAST(N'2025-12-01T21:14:10.650' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10102, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 12029, NULL, CAST(N'2025-12-02T16:31:50.630' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10103, 9, 34, 667829153, N'MikeUribeC', N'{"query": "cuantos tickets existen?"}', N'EXITOSO', NULL, 23694, NULL, CAST(N'2025-12-02T21:29:37.417' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10104, 9, 34, 667829153, N'MikeUribeC', N'{"query": "Dame el detalle del ticket más reciente"}', N'EXITOSO', NULL, 39805, NULL, CAST(N'2025-12-02T23:21:15.230' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10105, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10735, NULL, CAST(N'2025-12-03T22:03:01.650' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10106, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10883, NULL, CAST(N'2025-12-03T22:03:42.207' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10107, 9, 34, 667829153, N'MikeUribeC', N'{"query": "Cómo te llamas?"}', N'EXITOSO', NULL, 12509, NULL, CAST(N'2025-12-03T22:14:28.070' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10108, 2, 34, 1511768718, N'JrGarcia10', N'{"query": "Hola"}', N'EXITOSO', NULL, 10453, NULL, CAST(N'2025-12-05T22:44:34.360' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10109, 2, 34, 1511768718, N'JrGarcia10', N'{"query": "Quiero contactar a IT dame opciones"}', N'EXITOSO', NULL, 22331, NULL, CAST(N'2025-12-05T22:45:34.323' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10110, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 11820, NULL, CAST(N'2025-12-06T23:07:40.693' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (10111, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 7971, NULL, CAST(N'2025-12-06T23:29:58.127' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20110, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10633, NULL, CAST(N'2025-12-25T11:28:40.210' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20111, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 11418, NULL, CAST(N'2025-12-29T15:15:14.583' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20112, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Quiero saber que sabes sobre sistemas"}', N'EXITOSO', NULL, 12892, NULL, CAST(N'2025-12-29T15:17:40.383' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20113, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Si, cuáles son las preguntas frecuentes?"}', N'EXITOSO', NULL, 7107, NULL, CAST(N'2025-12-29T15:18:19.097' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20114, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Quiero pedir vacaciones"}', N'EXITOSO', NULL, 19238, NULL, CAST(N'2025-12-29T15:18:53.823' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20115, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que más sabes?, dame un dato aleatorio"}', N'EXITOSO', NULL, 8783, NULL, CAST(N'2025-12-29T15:20:15.910' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20116, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Hola"}', N'EXITOSO', NULL, 10113, NULL, CAST(N'2025-12-29T15:42:43.630' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20117, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Homa"}', N'EXITOSO', NULL, 10146, NULL, CAST(N'2025-12-29T15:58:32.860' AS DATETIME))
INSERT `dbo`.`LogOperaciones` (`idLog`, `idUsuario`, `idOperacion`, `telegramChatId`, `telegramUsername`, `parametros`, `resultado`, `mensajeError`, `duracionMs`, `ipOrigen`, `fechaEjecucion`) VALUES (20118, 1, 34, 1835573278, N'ingAngelRoque', N'{"query": "Que sabes de sistemas?"}', N'EXITOSO', NULL, 11473, NULL, CAST(N'2025-12-29T15:59:07.640' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`LogOperaciones` OFF
;
SET IDENTITY_INSERT `dbo`.`MenuNavegacion` ON 

INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (1, NULL, N'home', N'Home', NULL, N'Home', N'Index', N'fa fa-home', 1, 0, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.197' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (2, NULL, N'folderview', N'FolderView', NULL, N'FolderView', N'Index', N'fa fa-folder-open', 2, 0, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.200' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (3, NULL, N'code-generator', N'Code generator', N'#', NULL, NULL, N'fa fa-dashboard', 3, 0, 0, 1, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.200' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (4, 3, N'tipo-proyecto', N'Tipo proyecto', NULL, N'TipoProyecto', N'Index', N'fa fa-file-code-o', 1, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.207' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (5, 3, N'code-viewer', N'Code viewer', N'/CodeGeneratorViewer?idProyecto=1', N'CodeGeneratorViewer', N'Index', N'fa fa-file-code-o', 2, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.207' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (6, NULL, N'header-admin-bot', N'ADMINISTRACION BOT', N'#', NULL, NULL, N'fa fa-android', 4, 0, 1, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.210' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (7, NULL, N'admin-bot', N'Administracion Bot', N'#', NULL, NULL, N'fa fa-android', 5, 0, 0, 1, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.210' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (8, 7, N'dashboard', N'Dashboard', NULL, N'Dashboard', N'Index', N'fa fa-area-chart', 1, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.210' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (9, 7, N'modulos', N'Modulos', NULL, N'Modulo', N'Index', N'fa fa-puzzle-piece', 2, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.213' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (10, 7, N'comandos-telegram', N'Comandos Telegram', NULL, N'Operacion', N'Index', N'fa fa-code', 3, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.213' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (11, 7, N'roles-permisos', N'Roles y permisos', NULL, N'RolPermiso', N'Index', N'fa fa-lock', 4, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.217' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (12, 7, N'logs-comandos', N'Logs de comandos', NULL, N'LogOperacion', N'Index', N'fa fa-file-TEXT-o', 5, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.220' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (13, 7, N'cuentas-telegram', N'Cuentas Telegram', NULL, N'UsuarioTelegram', N'Index', N'fa fa-telegram', 6, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.220' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (14, 7, N'knowledge-base', N'Knowledge Base', NULL, N'KnowledgeBase', N'Index', N'fa fa-book', 7, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.227' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (15, 7, N'acceso-kb-rol', N'Acceso KB por Rol', NULL, N'RolKnowledge', N'Index', N'fa fa-key', 8, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.227' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (16, 7, N'roles-ia', N'Roles IA', NULL, N'RolIA', N'Index', N'fa fa-microchip', 9, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.230' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (17, 7, N'configuracion-ia', N'Configuración IA', NULL, N'ConfiguracionIA', N'Index', N'fa fa-robot', 10, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.230' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (18, 7, N'biblioteca-prompts', N'Biblioteca de Prompts', NULL, N'SmartPromptLibrary', N'Index', N'fa fa-file-TEXT', 11, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.233' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (19, 7, N'menu-navegacion', N'Menú Navegación', NULL, N'MenuNavegacion', N'Index', N'fa fa-bars', 15, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.237' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (20, NULL, N'header-mi-cuenta', N'MI CUENTA', N'#', NULL, NULL, N'fa fa-user-circle', 6, 0, 1, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.237' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (21, NULL, N'mi-cuenta', N'Mi Cuenta', N'#', NULL, NULL, N'fa fa-user-circle', 7, 0, 0, 1, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.237' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (22, 21, N'dashboard-personal', N'Dashboard Personal', NULL, N'DashboardPersonal', N'Index', N'fa fa-dashboard', 1, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.240' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (23, 21, N'mi-perfil', N'Mi Perfil', NULL, N'MiPerfil', N'Index', N'fa fa-user', 2, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.243' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (24, 21, N'mis-cuentas-telegram', N'Mis Cuentas Telegram', NULL, N'MisCuentasTelegram', N'Index', N'fa fa-telegram', 3, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.247' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (25, 21, N'mis-comandos', N'Mis Comandos', NULL, N'MisOperaciones', N'Index', N'fa fa-history', 4, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.250' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (26, 21, N'mis-permisos', N'Mis Permisoss', NULL, N'MisPermisos', N'Index', N'fa fa-shield', 5, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-08T11:00:32.250' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (27, 7, N'admin-prompts', N'Admin Prompts', NULL, N'SmartPromptLibrary', N'Admin', N'fa fa-cogs', 12, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-25T13:10:58.287' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (28, 7, N'chat-ia', N'Chat IA', NULL, N'ChatIA', N'Index', N'fa fa-comments', 13, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-27T11:28:51.637' AS DATETIME), NULL)
INSERT `dbo`.`MenuNavegacion` (`idMenu`, `idMenuPadre`, `nombre`, `titulo`, `url`, `controlador`, `accion`, `icono`, `orden`, `nivel`, `esHeader`, `esTreeview`, `activo`, `requiresAuth`, `roles`, `fechaCreacion`, `fechaModificacion`) VALUES (29, 7, N'config-chat-ia', N'Config. Chat IA', NULL, N'ChatIA', N'Configuracion', N'fa fa-cog', 14, 1, 0, 0, 1, 1, NULL, CAST(N'2025-12-27T11:28:51.640' AS DATETIME), NULL)
SET IDENTITY_INSERT `dbo`.`MenuNavegacion` OFF
;
SET IDENTITY_INSERT `dbo`.`ModelosIA` ON 

INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (1, 1, N'gpt-4', N'GPT-4', N'Modelo más avanzado de OpenAI con mayor capacidad de razonamiento', CAST(0.000030 AS DECIMAL(18,6)), 0, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), CAST(N'2025-12-04T19:20:06.460' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (2, 1, N'gpt-4-turbo', N'GPT-4 Turbo', N'Versión optimizada de GPT-4 con mayor velocidad', CAST(0.000010 AS DECIMAL(18,6)), 0, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), CAST(N'2025-12-04T19:20:06.460' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (3, 1, N'gpt-3.5-turbo', N'GPT-3.5 Turbo', N'Modelo rápido y económico para tareas generales', CAST(0.000002 AS DECIMAL(18,6)), 0, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), CAST(N'2025-12-04T19:20:06.460' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (4, 1, N'gpt-4o', N'GPT-4 Omni', N'Modelo multimodal de última generación', CAST(0.000015 AS DECIMAL(18,6)), 0, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), CAST(N'2025-12-04T19:20:06.460' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (5, 2, N'claude-3-opus', N'Claude 3 Opus', N'Modelo más potente de Anthropic para tareas complejas', CAST(0.000015 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (6, 2, N'claude-3-sonnet', N'Claude 3 Sonnet', N'Balance ideal entre rendimiento y costo', CAST(0.000003 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (7, 2, N'claude-3-haiku', N'Claude 3 Haiku', N'Modelo rápido y económico de Anthropic', CAST(0.000001 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (8, 2, N'claude-3.5-sonnet', N'Claude 3.5 Sonnet', N'Versión mejorada con mejor capacidad de razonamiento', CAST(0.000003 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (9, 3, N'gemini-pro', N'Gemini Pro', N'Modelo avanzado de Google para tareas complejas', CAST(0.000005 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (10, 3, N'gemini-ultra', N'Gemini Ultra', N'Modelo más potente de la familia Gemini', CAST(0.000020 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (11, 3, N'gemini-flash', N'Gemini Flash', N'Modelo optimizado para respuestas rápidas', CAST(0.000001 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.397' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (12, 4, N'llama-3-70b', N'Llama 3 70B', N'Modelo de código abierto de 70 mil millones de parámetros', CAST(0.000002 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.400' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (13, 4, N'llama-3-8b', N'Llama 3 8B', N'Modelo compacto de 8 mil millones de parámetros', CAST(0.000001 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.400' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (14, 5, N'mistral-large', N'Mistral Large', N'Modelo más potente de Mistral AI', CAST(0.000008 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.400' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (15, 5, N'mistral-medium', N'Mistral Medium', N'Balance entre rendimiento y costo', CAST(0.000003 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.400' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (16, 5, N'mistral-small', N'Mistral Small', N'Modelo compacto y económico', CAST(0.000001 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.400' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (17, 6, N'command', N'Command', N'Modelo para generación de texto y comandos', CAST(0.000002 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.400' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (18, 6, N'command-light', N'Command Light', N'Versión ligera del modelo Command', CAST(0.000001 AS DECIMAL(18,6)), 1, CAST(N'2025-12-02T21:58:03.400' AS DATETIME), NULL)
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (19, 1, N'gpt-5.1', N'GPT-5.1 (High Reasoning)', N'Modelo insignia con capacidades avanzadas de razonamiento y codificación. Ideal para tareas complejas.', CAST(1.250000 AS DECIMAL(18,6)), 1, CAST(N'2025-12-04T19:20:06.463' AS DATETIME), CAST(N'2025-12-04T19:20:06.463' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (20, 1, N'gpt-5-pro', N'GPT-5 Pro', N'Modelo de máxima capacidad para investigación profunda y tareas críticas. Mayor costo, máxima precisión.', CAST(15.000000 AS DECIMAL(18,6)), 1, CAST(N'2025-12-04T19:20:06.463' AS DATETIME), CAST(N'2025-12-04T19:20:06.463' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (21, 1, N'gpt-5', N'GPT-5 Standard', N'Modelo base de la quinta generación. Balanceado para uso general.', CAST(1.250000 AS DECIMAL(18,6)), 1, CAST(N'2025-12-04T19:20:06.463' AS DATETIME), CAST(N'2025-12-04T19:20:06.463' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (22, 1, N'gpt-5-mini', N'GPT-5 Mini', N'Reemplazo de GPT-4o-mini. Alta velocidad y bajo costo para tareas repetitivas y chats simples.', CAST(0.250000 AS DECIMAL(18,6)), 1, CAST(N'2025-12-04T19:20:06.463' AS DATETIME), CAST(N'2025-12-04T19:20:06.463' AS DATETIME))
INSERT `dbo`.`ModelosIA` (`idModeloIA`, `idProveedorIA`, `nombre`, `nombreCompleto`, `descripcion`, `costoPorToken`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (23, 1, N'gpt-5-nano', N'GPT-5 Nano', N'El modelo más rápido y económico. Ideal para resumen, clasificación y tareas en tiempo FLOAT.', CAST(0.050000 AS DECIMAL(18,6)), 1, CAST(N'2025-12-04T19:20:06.463' AS DATETIME), CAST(N'2025-12-04T19:20:06.463' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`ModelosIA` OFF
;
SET IDENTITY_INSERT `dbo`.`Modulos` ON 

INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (1, N'Tickets', N'Gestión de tickets y solicitudes', N'fa-ticket', 1, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (2, N'Reportes', N'Generación y consulta de reportes', N'fa-bar-chart', 2, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (3, N'Usuarios', N'Administración de usuarios', N'fa-users', 3, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (4, N'Configuración', N'Configuración del sistema', N'fa-cogs', 4, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (5, N'Notificaciones', N'Envío y gestión de notificaciones', N'fa-bell', 5, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (6, N'Consultas', N'Consultas generales de información', N'fa-search', 6, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (7, N'Aprobaciones', N'Flujo de aprobaciones', N'fa-check-square-o', 7, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
INSERT `dbo`.`Modulos` (`idModulo`, `nombre`, `descripcion`, `icono`, `orden`, `activo`, `fechaCreacion`) VALUES (8, N'IA', N'Operaciones con Inteligencia Artificial', N'fa-magic', 8, 1, CAST(N'2025-10-29T11:00:55.343' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`Modulos` OFF
;
SET IDENTITY_INSERT `dbo`.`Operaciones` ON 

INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (1, 1, N'Crear Ticket', N'Crear un nuevo ticket o solicitud', N'/crear_ticket', 1, N'/crear_ticket `descripción`', 1, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (2, 1, N'Consultar Ticket', N'Ver detalles de un ticket específico', N'/ver_ticket', 1, N'/ver_ticket `número`', 1, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (3, 1, N'Listar Mis Tickets', N'Ver todos mis tickets', N'/mis_tickets', 0, NULL, 1, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (4, 1, N'Actualizar Ticket', N'Actualizar información de un ticket', N'/actualizar_ticket', 1, N'/actualizar_ticket `número` `comentario`', 2, 4, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (5, 1, N'Cerrar Ticket', N'Cerrar un ticket existente', N'/cerrar_ticket', 1, N'/cerrar_ticket `número`', 2, 5, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (6, 1, N'Reasignar Ticket', N'Reasignar ticket a otra área', N'/reasignar_ticket', 1, N'/reasignar_ticket `número` `área`', 3, 6, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (7, 1, N'Eliminar Ticket', N'Eliminar un ticket del sistema', N'/eliminar_ticket', 1, N'/eliminar_ticket `número`', 4, 7, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (8, 2, N'Reporte Diario', N'Generar reporte diario de actividades', N'/reporte_diario', 0, NULL, 1, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (9, 2, N'Reporte Semanal', N'Generar reporte semanal', N'/reporte_semanal', 0, NULL, 1, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (10, 2, N'Reporte Mensual', N'Generar reporte mensual', N'/reporte_mensual', 0, NULL, 2, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (11, 2, N'Reporte Personalizado', N'Generar reporte con filtros específicos', N'/reporte_custom', 1, N'/reporte_custom `fecha_inicio` `fecha_fin`', 2, 4, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (12, 2, N'Exportar Excel', N'Exportar datos a Excel', N'/exportar_excel', 1, N'/exportar_excel `tipo_reporte`', 2, 5, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (13, 3, N'Listar Usuarios', N'Ver lista de usuarios del sistema', N'/listar_usuarios', 0, NULL, 1, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (14, 3, N'Crear Usuario', N'Dar de alta un nuevo usuario', N'/crear_usuario', 1, N'/crear_usuario `nombre` `email` `rol`', 3, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (15, 3, N'Modificar Usuario', N'Modificar datos de un usuario', N'/modificar_usuario', 1, N'/modificar_usuario `id` `campo` `valor`', 3, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (16, 3, N'Desactivar Usuario', N'Desactivar acceso de un usuario', N'/desactivar_usuario', 1, N'/desactivar_usuario `id`', 4, 4, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (17, 3, N'Asignar Rol', N'Asignar rol a un usuario', N'/asignar_rol', 1, N'/asignar_rol `id_usuario` `id_rol`', 3, 5, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (18, 3, N'Ver Permisos', N'Ver permisos de un usuario', N'/ver_permisos', 1, N'/ver_permisos `id_usuario`', 1, 6, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (19, 4, N'Ver Configuración', N'Ver configuración actual', N'/ver_config', 0, NULL, 1, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (20, 4, N'Modificar Configuración', N'Cambiar parámetros de configuración', N'/set_config', 1, N'/set_config `parámetro` `valor`', 4, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (21, 4, N'Backup Base Datos', N'Realizar respaldo de base de datos', N'/backup_db', 0, NULL, 4, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (22, 4, N'Ver Logs Sistema', N'Consultar logs del sistema', N'/ver_logs', 1, N'/ver_logs `fecha` `nivel`', 2, 4, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (23, 5, N'Enviar Notificación', N'Enviar notificación a usuarios', N'/enviar_notif', 1, N'/enviar_notif `usuario/grupo` `mensaje`', 2, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (24, 5, N'Broadcast', N'Enviar mensaje masivo', N'/broadcast', 1, N'/broadcast `mensaje`', 3, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (25, 5, N'Programar Notificación', N'Programar envío de notificación', N'/programar_notif', 1, N'/programar_notif `fecha_hora` `mensaje`', 2, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (26, 6, N'Consultar Status', N'Consultar estado general del sistema', N'/status', 0, NULL, 1, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (27, 6, N'Buscar Información', N'Buscar información en la base de datos', N'/buscar', 1, N'/buscar `término`', 1, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (28, 6, N'Ver Estadísticas', N'Ver estadísticas generales', N'/estadisticas', 0, NULL, 1, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (29, 6, N'Consultar Gerencias', N'Ver información de gerencias', N'/ver_gerencias', 0, NULL, 1, 4, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (30, 7, N'Listar Pendientes', N'Ver solicitudes pendientes de aprobación', N'/pendientes', 0, NULL, 1, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (31, 7, N'Aprobar Solicitud', N'Aprobar una solicitud', N'/aprobar', 1, N'/aprobar `id_solicitud`', 2, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (32, 7, N'Rechazar Solicitud', N'Rechazar una solicitud', N'/rechazar', 1, N'/rechazar `id_solicitud` `motivo`', 2, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (33, 7, N'Ver Historial Aprobaciones', N'Consultar historial de aprobaciones', N'/historial_aprob', 1, N'/historial_aprob `fecha_inicio` `fecha_fin`', 1, 4, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (34, 8, N'Consulta IA', N'Hacer consulta con IA', N'/ia', 1, N'/ia `pregunta`', 1, 1, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (35, 8, N'Análisis Predictivo', N'Solicitar análisis predictivo', N'/predecir', 1, N'/predecir `dataset`', 2, 2, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (36, 8, N'Generar Resumen', N'Generar resumen con IA', N'/resumir', 1, N'/resumir `documento`', 1, 3, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
INSERT `dbo`.`Operaciones` (`idOperacion`, `idModulo`, `nombre`, `descripcion`, `comando`, `requiereParametros`, `parametrosEjemplo`, `nivelCriticidad`, `orden`, `activo`, `fechaCreacion`) VALUES (37, 8, N'Entrenar Modelo', N'Entrenar modelo de IA', N'/entrenar_ia', 1, N'/entrenar_ia `modelo` `datos`', 4, 4, 1, CAST(N'2025-10-29T11:00:55.377' AS DATETIME))
SET IDENTITY_INSERT `dbo`.`Operaciones` OFF
;
SET IDENTITY_INSERT `dbo`.`PromptEtiquetas` ON 

INSERT `dbo`.`PromptEtiquetas` (`idPromptEtiqueta`, `idPrompt`, `idEtiquetaPrompt`) VALUES (1, 1, 5)
INSERT `dbo`.`PromptEtiquetas` (`idPromptEtiqueta`, `idPrompt`, `idEtiquetaPrompt`) VALUES (2, 1, 7)
INSERT `dbo`.`PromptEtiquetas` (`idPromptEtiqueta`, `idPrompt`, `idEtiquetaPrompt`) VALUES (7, 2, 4)
INSERT `dbo`.`PromptEtiquetas` (`idPromptEtiqueta`, `idPrompt`, `idEtiquetaPrompt`) VALUES (8, 2, 5)
INSERT `dbo`.`PromptEtiquetas` (`idPromptEtiqueta`, `idPrompt`, `idEtiquetaPrompt`) VALUES (5, 3, 5)
INSERT `dbo`.`PromptEtiquetas` (`idPromptEtiqueta`, `idPrompt`, `idEtiquetaPrompt`) VALUES (6, 3, 7)
SET IDENTITY_INSERT `dbo`.`PromptEtiquetas` OFF
;
SET IDENTITY_INSERT `dbo`.`ProveedoresIA` ON 

INSERT `dbo`.`ProveedoresIA` (`idProveedorIA`, `nombre`, `descripcion`, `urlBase`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (1, N'OpenAI', N'Proveedor de modelos GPT (ChatGPT, GPT-4, etc.)', N'https://api.openai.com/v1', 1, CAST(N'2025-12-02T21:58:03.373' AS DATETIME), NULL)
INSERT `dbo`.`ProveedoresIA` (`idProveedorIA`, `nombre`, `descripcion`, `urlBase`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (2, N'Anthropic', N'Proveedor de modelos Claude (Claude 3 Sonnet, Opus, Haiku)', N'https://api.anthropic.com/v1', 1, CAST(N'2025-12-02T21:58:03.373' AS DATETIME), NULL)
INSERT `dbo`.`ProveedoresIA` (`idProveedorIA`, `nombre`, `descripcion`, `urlBase`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (3, N'Google', N'Proveedor de modelos Gemini (Gemini Pro, Ultra)', N'https://generativelanguage.googleapis.com/v1', 1, CAST(N'2025-12-02T21:58:03.373' AS DATETIME), NULL)
INSERT `dbo`.`ProveedoresIA` (`idProveedorIA`, `nombre`, `descripcion`, `urlBase`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (4, N'Meta', N'Proveedor de modelos Llama (Llama 2, Llama 3)', N'https://api.together.xyz/v1', 1, CAST(N'2025-12-02T21:58:03.373' AS DATETIME), NULL)
INSERT `dbo`.`ProveedoresIA` (`idProveedorIA`, `nombre`, `descripcion`, `urlBase`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (5, N'Mistral AI', N'Proveedor de modelos Mistral (Mistral Large, Medium)', N'https://api.mistral.ai/v1', 1, CAST(N'2025-12-02T21:58:03.373' AS DATETIME), NULL)
INSERT `dbo`.`ProveedoresIA` (`idProveedorIA`, `nombre`, `descripcion`, `urlBase`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (6, N'Cohere', N'Proveedor de modelos de procesamiento de lenguaje natural', N'https://api.cohere.ai/v1', 1, CAST(N'2025-12-02T21:58:03.373' AS DATETIME), NULL)
SET IDENTITY_INSERT `dbo`.`ProveedoresIA` OFF
;
SET IDENTITY_INSERT `dbo`.`Roles` ON 

INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (1, N'Administrador', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (2, N'Gerente', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (3, N'Supervisor', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (4, N'Analista', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (5, N'Usuario', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (6, N'Consulta', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (7, N'Coordinador', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
INSERT `dbo`.`Roles` (`idRol`, `nombre`, `fechaCreacion`, `activo`) VALUES (8, N'Especialista', CAST(N'2025-10-29T10:52:46.300' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`Roles` OFF
;
SET IDENTITY_INSERT `dbo`.`RolesCategoriesKnowledge` ON 

INSERT `dbo`.`RolesCategoriesKnowledge` (`idRolCategoria`, `idRol`, `idCategoria`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `activo`) VALUES (1, 1, 2, 0, CAST(N'2025-12-06T23:07:10.560' AS DATETIME), 1, 1)
INSERT `dbo`.`RolesCategoriesKnowledge` (`idRolCategoria`, `idRol`, `idCategoria`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `activo`) VALUES (2, 1, 3, 0, CAST(N'2025-12-06T23:07:10.567' AS DATETIME), 1, 1)
INSERT `dbo`.`RolesCategoriesKnowledge` (`idRolCategoria`, `idRol`, `idCategoria`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `activo`) VALUES (3, 1, 4, 0, CAST(N'2025-12-06T23:07:10.560' AS DATETIME), 1, 1)
INSERT `dbo`.`RolesCategoriesKnowledge` (`idRolCategoria`, `idRol`, `idCategoria`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `activo`) VALUES (4, 1, 7, 0, CAST(N'2025-12-06T23:07:10.560' AS DATETIME), 1, 1)
INSERT `dbo`.`RolesCategoriesKnowledge` (`idRolCategoria`, `idRol`, `idCategoria`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `activo`) VALUES (5, 1, 1, 0, CAST(N'2025-12-06T23:07:10.557' AS DATETIME), 1, 1)
INSERT `dbo`.`RolesCategoriesKnowledge` (`idRolCategoria`, `idRol`, `idCategoria`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `activo`) VALUES (6, 1, 6, 0, CAST(N'2025-12-06T23:07:10.563' AS DATETIME), 1, 1)
INSERT `dbo`.`RolesCategoriesKnowledge` (`idRolCategoria`, `idRol`, `idCategoria`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `activo`) VALUES (7, 1, 5, 1, CAST(N'2025-12-06T22:59:38.617' AS DATETIME), 1, 1)
SET IDENTITY_INSERT `dbo`.`RolesCategoriesKnowledge` OFF
;
SET IDENTITY_INSERT `dbo`.`RolesIA` ON 

INSERT `dbo`.`RolesIA` (`idRol`, `nombre`, `descripcion`, `fechaCreacion`, `activo`) VALUES (1, N'Administrador IA', N'Acceso completo a funcionalidades de IA y configuración', CAST(N'2025-10-29T10:52:46.310' AS DATETIME), 1)
INSERT `dbo`.`RolesIA` (`idRol`, `nombre`, `descripcion`, `fechaCreacion`, `activo`) VALUES (2, N'Analista IA Avanzado', N'Puede usar herramientas avanzadas de análisis con IA', CAST(N'2025-10-29T10:52:46.310' AS DATETIME), 1)
INSERT `dbo`.`RolesIA` (`idRol`, `nombre`, `descripcion`, `fechaCreacion`, `activo`) VALUES (3, N'Analista IA', N'Puede usar herramientas de análisis con IA', CAST(N'2025-10-29T10:52:46.310' AS DATETIME), 1)
INSERT `dbo`.`RolesIA` (`idRol`, `nombre`, `descripcion`, `fechaCreacion`, `activo`) VALUES (4, N'Usuario IA Premium', N'Acceso a funcionalidades premium de IA', CAST(N'2025-10-29T10:52:46.310' AS DATETIME), 1)
INSERT `dbo`.`RolesIA` (`idRol`, `nombre`, `descripcion`, `fechaCreacion`, `activo`) VALUES (5, N'Usuario IA', N'Acceso básico a funcionalidades de IA', CAST(N'2025-10-29T10:52:46.310' AS DATETIME), 1)
INSERT `dbo`.`RolesIA` (`idRol`, `nombre`, `descripcion`, `fechaCreacion`, `activo`) VALUES (6, N'Consultor IA', N'Solo consulta de resultados generados por IA', CAST(N'2025-10-29T10:52:46.310' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`RolesIA` OFF
;
SET IDENTITY_INSERT `dbo`.`RolesOperaciones` ON 

INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (1, 1, 1, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (2, 1, 2, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (3, 1, 3, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (4, 1, 4, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (5, 1, 5, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (6, 1, 6, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (7, 1, 7, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (8, 1, 8, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (9, 1, 9, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (10, 1, 10, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (11, 1, 11, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (12, 1, 12, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (13, 1, 13, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (14, 1, 14, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (15, 1, 15, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (16, 1, 16, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (17, 1, 17, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (18, 1, 18, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (19, 1, 19, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (20, 1, 20, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (21, 1, 21, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (22, 1, 22, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (23, 1, 23, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (24, 1, 24, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (25, 1, 25, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (26, 1, 26, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (27, 1, 27, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (28, 1, 28, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (29, 1, 29, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (30, 1, 30, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (31, 1, 31, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (32, 1, 32, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (33, 1, 33, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (34, 1, 34, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (35, 1, 35, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (36, 1, 36, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (37, 1, 37, 1, CAST(N'2025-10-29T11:00:55.413' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (38, 2, 1, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (39, 2, 2, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (40, 2, 3, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (41, 2, 4, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (42, 2, 5, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (43, 2, 6, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (44, 2, 8, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (45, 2, 9, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (46, 2, 10, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (47, 2, 11, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (48, 2, 12, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (49, 2, 13, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (50, 2, 18, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (51, 2, 23, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (52, 2, 24, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (53, 2, 25, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (54, 2, 26, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (55, 2, 27, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (56, 2, 28, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (57, 2, 29, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (58, 2, 30, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (59, 2, 31, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (60, 2, 32, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (61, 2, 33, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (62, 2, 34, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (63, 2, 35, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (64, 2, 36, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (82, 4, 1, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (83, 4, 2, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (84, 4, 3, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (85, 4, 8, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (86, 4, 9, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (87, 4, 10, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (88, 4, 11, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (89, 4, 12, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (90, 4, 26, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (91, 4, 27, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (92, 4, 28, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (93, 4, 29, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (94, 4, 34, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (95, 4, 35, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (96, 4, 36, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (97, 5, 1, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (98, 5, 2, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (99, 5, 3, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (100, 5, 26, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (101, 5, 27, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (102, 5, 34, 1, CAST(N'2025-10-29T11:00:55.417' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (103, 6, 2, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (104, 6, 3, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (105, 6, 26, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (106, 6, 27, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (107, 6, 28, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (108, 6, 29, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (109, 7, 1, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (110, 7, 2, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (111, 7, 3, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (112, 7, 4, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (113, 7, 5, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (114, 7, 6, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (115, 7, 8, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (116, 7, 9, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
;
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (117, 7, 23, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (118, 7, 25, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (119, 7, 26, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (120, 7, 27, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (121, 7, 28, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (122, 7, 34, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (123, 8, 1, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (124, 8, 2, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (125, 8, 3, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (126, 8, 4, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (127, 8, 5, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (128, 8, 10, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (129, 8, 11, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (130, 8, 12, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (131, 8, 19, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (132, 8, 22, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (133, 8, 26, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (134, 8, 27, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (135, 8, 28, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (136, 8, 34, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (137, 8, 35, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (138, 8, 36, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
INSERT `dbo`.`RolesOperaciones` (`idRolOperacion`, `idRol`, `idOperacion`, `permitido`, `fechaAsignacion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (139, 8, 37, 1, CAST(N'2025-10-29T11:00:55.420' AS DATETIME), NULL, NULL, 1)
SET IDENTITY_INSERT `dbo`.`RolesOperaciones` OFF
;
SET IDENTITY_INSERT `dbo`.`SistemasAplicaciones` ON 

INSERT `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (1, N'Tickets', N'Gestión de tickets y solicitudes', N'fa-file', N'#3c8dbc', 1, CAST(N'2025-12-03T22:32:09.380' AS DATETIME), CAST(N'2025-12-03T23:56:56.860' AS DATETIME))
INSERT `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (2, N'Reportes', N'Generación y consulta de reportes', N'fa-bar-chart', N'#34f91a', 1, CAST(N'2025-12-03T22:32:09.380' AS DATETIME), CAST(N'2025-12-03T23:50:46.820' AS DATETIME))
INSERT `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (3, N'Sistema Web', N'Aplicación web principal', N'fa fa-globe', N'#3c8dbc', 1, CAST(N'2025-12-03T22:32:09.443' AS DATETIME), NULL)
INSERT `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (4, N'API REST', N'API de servicios REST', N'fa fa-code', N'#00a65a', 1, CAST(N'2025-12-03T22:32:09.443' AS DATETIME), NULL)
INSERT `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (5, N'Análisis de Datos', N'Sistema de análisis y reportes', N'fa fa-chart-bar', N'#f39c12', 1, CAST(N'2025-12-03T22:32:09.443' AS DATETIME), NULL)
INSERT `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (6, N'Procesamiento de Documentos', N'Sistema de procesamiento de archivos', N'fa fa-file-alt', N'#dd4b39', 1, CAST(N'2025-12-03T22:32:09.443' AS DATETIME), NULL)
INSERT `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`, `nombre`, `descripcion`, `icono`, `color`, `activo`, `fechaCreacion`, `fechaActualizacion`) VALUES (7, N'Biblioteca Prompts', N'', N'fa-file-code-o', N'#3c8dbc', 1, CAST(N'2025-12-04T19:13:13.477' AS DATETIME), NULL)
SET IDENTITY_INSERT `dbo`.`SistemasAplicaciones` OFF
;
SET IDENTITY_INSERT `dbo`.`Usuarios` ON 

INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (1, 1001, N'Juan', N'Pérez González', 1, N'juan.perez@abcmasplus.com', CAST(N'2025-07-31T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (2, 1002, N'María', N'López Hernández', 2, N'maria.lopez@abcmasplus.com', CAST(N'2025-08-05T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T08:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (3, 1003, N'Carlos', N'Martínez Silva', 2, N'carlos.martinez@abcmasplus.com', CAST(N'2025-08-10T10:52:46.320' AS DATETIME), CAST(N'2025-10-28T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (4, 1004, N'Ana', N'García Rodríguez', 3, N'ana.garcia@abcmasplus.com', CAST(N'2025-08-15T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T05:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (5, 1005, N'Luis', N'Fernández Torres', 3, N'luis.fernandez@abcmasplus.com', CAST(N'2025-08-20T10:52:46.320' AS DATETIME), CAST(N'2025-10-27T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (6, 1006, N'Patricia', N'Sánchez Morales', 4, N'patricia.sanchez@abcmasplus.com', CAST(N'2025-08-25T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (7, 1007, N'Roberto', N'Ramírez Cruz', 4, N'roberto.ramirez@abcmasplus.com', CAST(N'2025-08-30T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T07:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (8, 1008, N'Laura', N'Torres Jiménez', 5, N'laura.torres@abcmasplus.com', CAST(N'2025-09-04T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T09:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (9, 1009, N'Miguel', N'Uribe Castagne', 1, N'miguel.uribecastagne@abcmasplus.com', CAST(N'2025-09-09T10:52:46.320' AS DATETIME), CAST(N'2025-10-26T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (10, 1010, N'Carmen', N'Ruiz Mendoza', 6, N'carmen.ruiz@abcmasplus.com', CAST(N'2025-09-14T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T04:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (11, 1011, N'Jorge', N'Díaz Castro', 7, N'jorge.diaz@abcmasplus.com', CAST(N'2025-09-19T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T06:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (12, 1012, N'Sofía', N'Moreno Ortiz', 7, N'sofia.moreno@abcmasplus.com', CAST(N'2025-09-24T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (13, 1013, N'Fernando', N'Vázquez Luna', 8, N'fernando.vazquez@abcmasplus.com', CAST(N'2025-09-29T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T08:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (14, 1014, N'Isabel', N'Romero Ríos', 8, N'isabel.romero@abcmasplus.com', CAST(N'2025-10-04T10:52:46.320' AS DATETIME), CAST(N'2025-10-28T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (15, 1015, N'Ricardo', N'Herrera Peña', 5, N'ricardo.herrera@abcmasplus.com', CAST(N'2025-10-09T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T02:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (16, 1016, N'Gabriela', N'Aguilar Medina', 5, N'gabriela.aguilar@abcmasplus.com', CAST(N'2025-10-14T10:52:46.320' AS DATETIME), CAST(N'2025-10-28T22:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (17, 1017, N'Andrés', N'Castillo Ramos', 4, N'andres.castillo@abcmasplus.com', CAST(N'2025-10-19T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T10:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (18, 1018, N'Valentina', N'Guerrero Salazar', 4, N'valentina.guerrero@abcmasplus.com', CAST(N'2025-10-21T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T09:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (19, 1019, N'Daniel', N'Mendoza Fuentes', 5, N'daniel.mendoza@abcmasplus.com', CAST(N'2025-10-24T10:52:46.320' AS DATETIME), CAST(N'2025-10-29T07:52:46.320' AS DATETIME), 1)
INSERT `dbo`.`Usuarios` (`idUsuario`, `idEmpleado`, `nombre`, `apellido`, `rol`, `email`, `fechaCreacion`, `fechaUltimoAcceso`, `activo`) VALUES (20, 1020, N'Mónica', N'Cruz Navarro', 6, N'monica.cruz@abcmasplus.com', CAST(N'2025-10-26T10:52:46.320' AS DATETIME), CAST(N'2025-10-27T10:52:46.320' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`Usuarios` OFF
;
SET IDENTITY_INSERT `dbo`.`UsuariosOperaciones` ON 

INSERT `dbo`.`UsuariosOperaciones` (`idUsuarioOperacion`, `idUsuario`, `idOperacion`, `permitido`, `fechaAsignacion`, `fechaExpiracion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (1, 8, 8, 1, CAST(N'2025-10-29T11:00:55.430' AS DATETIME), CAST(N'2025-11-28T11:00:55.430' AS DATETIME), 1, N'Permiso temporal para proyecto especial', 1)
INSERT `dbo`.`UsuariosOperaciones` (`idUsuarioOperacion`, `idUsuario`, `idOperacion`, `permitido`, `fechaAsignacion`, `fechaExpiracion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (2, 10, 28, 0, CAST(N'2025-10-29T11:00:55.433' AS DATETIME), NULL, 1, N'Restricción por políticas de seguridad', 1)
INSERT `dbo`.`UsuariosOperaciones` (`idUsuarioOperacion`, `idUsuario`, `idOperacion`, `permitido`, `fechaAsignacion`, `fechaExpiracion`, `usuarioAsignacion`, `observaciones`, `activo`) VALUES (3, 15, 31, 1, CAST(N'2025-10-29T11:00:55.433' AS DATETIME), CAST(N'2025-11-13T11:00:55.433' AS DATETIME), 2, N'Reemplazo temporal durante vacaciones', 1)
SET IDENTITY_INSERT `dbo`.`UsuariosOperaciones` OFF
;
SET IDENTITY_INSERT `dbo`.`UsuariosRolesIA` ON 

INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (1, 1, 1, CAST(N'2025-07-31T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (2, 2, 2, CAST(N'2025-08-05T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (3, 2, 3, CAST(N'2025-08-10T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (4, 3, 4, CAST(N'2025-08-15T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (5, 3, 5, CAST(N'2025-08-20T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (6, 4, 6, CAST(N'2025-08-25T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (7, 3, 7, CAST(N'2025-08-30T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (8, 5, 8, CAST(N'2025-09-04T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (9, 5, 9, CAST(N'2025-09-09T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (10, 6, 10, CAST(N'2025-09-14T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (11, 4, 11, CAST(N'2025-09-19T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (12, 4, 12, CAST(N'2025-09-24T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (13, 3, 13, CAST(N'2025-09-29T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (14, 3, 14, CAST(N'2025-10-04T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (15, 5, 15, CAST(N'2025-10-09T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (16, 5, 16, CAST(N'2025-10-14T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (17, 5, 17, CAST(N'2025-10-19T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (18, 5, 18, CAST(N'2025-10-21T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (19, 5, 19, CAST(N'2025-10-24T10:52:46.360' AS DATETIME), 1)
INSERT `dbo`.`UsuariosRolesIA` (`idUsuarioRolIA`, `idRol`, `idUsuario`, `fechaAsignacion`, `activo`) VALUES (20, 6, 20, CAST(N'2025-10-26T10:52:46.360' AS DATETIME), 1)
SET IDENTITY_INSERT `dbo`.`UsuariosRolesIA` OFF
;
SET IDENTITY_INSERT `dbo`.`UsuariosTelegram` ON 

INSERT `dbo`.`UsuariosTelegram` (`idUsuarioTelegram`, `idUsuario`, `telegramChatId`, `telegramUsername`, `telegramFirstName`, `telegramLastName`, `alias`, `esPrincipal`, `estado`, `fechaRegistro`, `fechaUltimaActividad`, `fechaVerificacion`, `codigoVerificacion`, `verificado`, `intentosVerificacion`, `notificacionesActivas`, `observaciones`, `activo`, `fechaCreacion`, `usuarioCreacion`, `fechaModificacion`, `usuarioModificacion`) VALUES (1, 1, 1835573278, N'ingAngelRoque', N'Angel David', N'Roque Ayala', NULL, 1, N'ACTIVO', CAST(N'2025-11-23T16:41:43.130' AS DATETIME), CAST(N'2025-12-06T23:29:50.150' AS DATETIME), CAST(N'2025-11-23T16:43:19.000' AS DATETIME), NULL, 1, 0, 1, NULL, 1, CAST(N'2025-11-23T16:41:43.130' AS DATETIME), NULL, NULL, NULL)
INSERT `dbo`.`UsuariosTelegram` (`idUsuarioTelegram`, `idUsuario`, `telegramChatId`, `telegramUsername`, `telegramFirstName`, `telegramLastName`, `alias`, `esPrincipal`, `estado`, `fechaRegistro`, `fechaUltimaActividad`, `fechaVerificacion`, `codigoVerificacion`, `verificado`, `intentosVerificacion`, `notificacionesActivas`, `observaciones`, `activo`, `fechaCreacion`, `usuarioCreacion`, `fechaModificacion`, `usuarioModificacion`) VALUES (2, 2, 1511768718, N'JrGarcia10', N'Jesús', N'García', NULL, 1, N'ACTIVO', CAST(N'2025-11-27T00:27:23.003' AS DATETIME), CAST(N'2025-12-06T15:11:15.093' AS DATETIME), CAST(N'2025-12-02T10:43:17.437' AS DATETIME), NULL, 1, 0, 1, NULL, 1, CAST(N'2025-11-27T00:27:23.003' AS DATETIME), NULL, NULL, NULL)
INSERT `dbo`.`UsuariosTelegram` (`idUsuarioTelegram`, `idUsuario`, `telegramChatId`, `telegramUsername`, `telegramFirstName`, `telegramLastName`, `alias`, `esPrincipal`, `estado`, `fechaRegistro`, `fechaUltimaActividad`, `fechaVerificacion`, `codigoVerificacion`, `verificado`, `intentosVerificacion`, `notificacionesActivas`, `observaciones`, `activo`, `fechaCreacion`, `usuarioCreacion`, `fechaModificacion`, `usuarioModificacion`) VALUES (3, 3, 6234533339, NULL, N'Israel', N'Roque', NULL, 1, N'ACTIVO', CAST(N'2025-11-29T12:31:54.743' AS DATETIME), NULL, CAST(N'2025-11-29T12:33:35.277' AS DATETIME), NULL, 1, 0, 1, NULL, 1, CAST(N'2025-11-29T12:31:54.743' AS DATETIME), NULL, NULL, NULL)
INSERT `dbo`.`UsuariosTelegram` (`idUsuarioTelegram`, `idUsuario`, `telegramChatId`, `telegramUsername`, `telegramFirstName`, `telegramLastName`, `alias`, `esPrincipal`, `estado`, `fechaRegistro`, `fechaUltimaActividad`, `fechaVerificacion`, `codigoVerificacion`, `verificado`, `intentosVerificacion`, `notificacionesActivas`, `observaciones`, `activo`, `fechaCreacion`, `usuarioCreacion`, `fechaModificacion`, `usuarioModificacion`) VALUES (4, 9, 667829153, N'MikeUribeC', N'Mike', N'Uribe', NULL, 1, N'ACTIVO', CAST(N'2025-12-02T21:06:29.500' AS DATETIME), CAST(N'2025-12-03T22:14:15.543' AS DATETIME), CAST(N'2025-12-02T21:20:28.593' AS DATETIME), NULL, 1, 0, 1, NULL, 1, CAST(N'2025-12-02T21:06:29.500' AS DATETIME), NULL, NULL, NULL)
SET IDENTITY_INSERT `dbo`.`UsuariosTelegram` OFF
;
/****** Object:  Index `UQ_AreaAtendedora_IdGerencia`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`AreaAtendedora` ADD  CONSTRAINT `UQ_AreaAtendedora_IdGerencia` UNIQUE NONCLUSTERED 
(
	`idGerencia` ASC
) 
;
/****** Object:  Index `IX_BibliotecaPrompts_Activo`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_BibliotecaPrompts_Activo` ON `dbo`.`BibliotecaPrompts`
(
	`activo` ASC
) 
;
/****** Object:  Index `IX_BibliotecaPrompts_Categoria`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_BibliotecaPrompts_Categoria` ON `dbo`.`BibliotecaPrompts`
(
	`idCategoriaPrompt` ASC
) 
;
/****** Object:  Index `IX_BibliotecaPrompts_Favorito`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_BibliotecaPrompts_Favorito` ON `dbo`.`BibliotecaPrompts`
(
	`favorito` ASC
) 
;

/****** Object:  Index `UQ_ChatCompartidas_Token`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`ChatConversacionesCompartidas` ADD  CONSTRAINT `UQ_ChatCompartidas_Token` UNIQUE NONCLUSTERED 
(
	`TokenPublico` ASC
) 
;
/****** Object:  Index `IX_ChatMensajes_Conversacion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_ChatMensajes_Conversacion` ON `dbo`.`ChatMensajes`
(
	`IdConversacion` ASC
) 
;
/****** Object:  Index `UQ_ChatPermisosRol_Rol`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`ChatPermisosRol` ADD  CONSTRAINT `UQ_ChatPermisosRol_Rol` UNIQUE NONCLUSTERED 
(
	`IdRol` ASC
) 
;

/****** Object:  Index `UQ_column_documentation`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`column_documentation` ADD  CONSTRAINT `UQ_column_documentation` UNIQUE NONCLUSTERED 
(
	`table_doc_id` ASC,
	`column_name` ASC
) 
;
/****** Object:  Index `idx_column_documentation_table`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `idx_column_documentation_table` ON `dbo`.`column_documentation`
(
	`table_doc_id` ASC
) 
;
/****** Object:  Index `IX_ConfiguracionIA_Modulo`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_ConfiguracionIA_Modulo` ON `dbo`.`ConfiguracionIAModulos`
(
	`idModulo` ASC
)
WHERE (`activo`=(1))
 
;
/****** Object:  Index `IX_ConfiguracionIASistemas_Sistema`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_ConfiguracionIASistemas_Sistema` ON `dbo`.`ConfiguracionIASistemas`
(
	`idSistemaAplicacion` ASC
)
WHERE (`activo`=(1))
 
;
/****** Object:  Index `IX_EjecucionesPrompt_Fecha`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_EjecucionesPrompt_Fecha` ON `dbo`.`EjecucionesPrompt`
(
	`fechaEjecucion` DESC
) 
;
/****** Object:  Index `IX_EjecucionesPrompt_Prompt`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_EjecucionesPrompt_Prompt` ON `dbo`.`EjecucionesPrompt`
(
	`idPrompt` ASC
) 
;

/****** Object:  Index `UQ__Etiqueta__72AFBCC615C77AF9`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`EtiquetasPrompt` ADD UNIQUE NONCLUSTERED 
(
	`nombre` ASC
) 
;

/****** Object:  Index `UQ_Gerencias_Alias`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`Gerencias` ADD  CONSTRAINT `UQ_Gerencias_Alias` UNIQUE NONCLUSTERED 
(
	`alias` ASC
) 
;
/****** Object:  Index `UQ_GerenciasRolesIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`GerenciasRolesIA` ADD  CONSTRAINT `UQ_GerenciasRolesIA` UNIQUE NONCLUSTERED 
(
	`idRol` ASC,
	`idGerencia` ASC
) 
;
/****** Object:  Index `IX_GerenciasRolesIA_IdGerencia`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_GerenciasRolesIA_IdGerencia` ON `dbo`.`GerenciasRolesIA`
(
	`idGerencia` ASC
) 
;
/****** Object:  Index `IX_GerenciasRolesIA_IdRol`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_GerenciasRolesIA_IdRol` ON `dbo`.`GerenciasRolesIA`
(
	`idRol` ASC
) 
;
/****** Object:  Index `UQ_GerenciaUsuarios`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`GerenciaUsuarios` ADD  CONSTRAINT `UQ_GerenciaUsuarios` UNIQUE NONCLUSTERED 
(
	`idUsuario` ASC,
	`idGerencia` ASC
) 
;
/****** Object:  Index `IX_GerenciaUsuarios_IdGerencia`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_GerenciaUsuarios_IdGerencia` ON `dbo`.`GerenciaUsuarios`
(
	`idGerencia` ASC
) 
;
/****** Object:  Index `IX_GerenciaUsuarios_IdUsuario`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_GerenciaUsuarios_IdUsuario` ON `dbo`.`GerenciaUsuarios`
(
	`idUsuario` ASC
) 
;

/****** Object:  Index `UQ__Iconos__72AFBCC661400801`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`Iconos` ADD UNIQUE NONCLUSTERED 
(
	`nombre` ASC
) 
;
/****** Object:  Index `IX_Iconos_Activo`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_Iconos_Activo` ON `dbo`.`Iconos`
(
	`activo` ASC
) 
;

/****** Object:  Index `IX_Iconos_Categoria`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_Iconos_Categoria` ON `dbo`.`Iconos`
(
	`categoria` ASC
) 
;

/****** Object:  Index `UQ__knowledg__72E12F1B543BFDDA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`knowledge_categories` ADD UNIQUE NONCLUSTERED 
(
	`name` ASC
) 
;
/****** Object:  Index `idx_knowledge_categories_active`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `idx_knowledge_categories_active` ON `dbo`.`knowledge_categories`
(
	`active` ASC
) 
;
/****** Object:  Index `idx_knowledge_entries_active`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `idx_knowledge_entries_active` ON `dbo`.`knowledge_entries`
(
	`active` ASC
) 
;
/****** Object:  Index `idx_knowledge_entries_category`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `idx_knowledge_entries_category` ON `dbo`.`knowledge_entries`
(
	`category_id` ASC
) 
;
/****** Object:  Index `idx_knowledge_entries_priority`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `idx_knowledge_entries_priority` ON `dbo`.`knowledge_entries`
(
	`priority` DESC
) 
;

/****** Object:  Index `idx_knowledge_entries_question`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `idx_knowledge_entries_question` ON `dbo`.`knowledge_entries`
(
	`question` ASC
) 
;
/****** Object:  Index `IX_LogOperaciones_FechaEjecucion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_LogOperaciones_FechaEjecucion` ON `dbo`.`LogOperaciones`
(
	`fechaEjecucion` DESC
) 
;
/****** Object:  Index `IX_LogOperaciones_IdOperacion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_LogOperaciones_IdOperacion` ON `dbo`.`LogOperaciones`
(
	`idOperacion` ASC
) 
;
/****** Object:  Index `IX_LogOperaciones_IdUsuario`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_LogOperaciones_IdUsuario` ON `dbo`.`LogOperaciones`
(
	`idUsuario` ASC
) 
;

/****** Object:  Index `IX_LogOperaciones_Resultado`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_LogOperaciones_Resultado` ON `dbo`.`LogOperaciones`
(
	`resultado` ASC
) 
;
/****** Object:  Index `IX_MenuNavegacion_Activo`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_MenuNavegacion_Activo` ON `dbo`.`MenuNavegacion`
(
	`activo` ASC
) 
;
/****** Object:  Index `IX_MenuNavegacion_Padre_Orden`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_MenuNavegacion_Padre_Orden` ON `dbo`.`MenuNavegacion`
(
	`idMenuPadre` ASC,
	`orden` ASC,
	`activo` ASC
) 
;
/****** Object:  Index `IX_ModelosIA_ProveedorIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_ModelosIA_ProveedorIA` ON `dbo`.`ModelosIA`
(
	`idProveedorIA` ASC
)
WHERE (`activo`=(1))
 
;

/****** Object:  Index `UQ_Modulos_Nombre`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`Modulos` ADD  CONSTRAINT `UQ_Modulos_Nombre` UNIQUE NONCLUSTERED 
(
	`nombre` ASC
) 
;

/****** Object:  Index `UQ_Operaciones_Comando`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`Operaciones` ADD  CONSTRAINT `UQ_Operaciones_Comando` UNIQUE NONCLUSTERED 
(
	`comando` ASC
) 
;

/****** Object:  Index `IX_Operaciones_Comando`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_Operaciones_Comando` ON `dbo`.`Operaciones`
(
	`comando` ASC
) 
;
/****** Object:  Index `IX_Operaciones_IdModulo`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_Operaciones_IdModulo` ON `dbo`.`Operaciones`
(
	`idModulo` ASC
) 
;
/****** Object:  Index `UQ_PromptEtiqueta`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`PromptEtiquetas` ADD  CONSTRAINT `UQ_PromptEtiqueta` UNIQUE NONCLUSTERED 
(
	`idPrompt` ASC,
	`idEtiquetaPrompt` ASC
) 
;

/****** Object:  Index `UQ__Proveedo__72AFBCC6A05E8CF6`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`ProveedoresIA` ADD UNIQUE NONCLUSTERED 
(
	`nombre` ASC
) 
;

/****** Object:  Index `UQ_Roles_Nombre`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`Roles` ADD  CONSTRAINT `UQ_Roles_Nombre` UNIQUE NONCLUSTERED 
(
	`nombre` ASC
) 
;
/****** Object:  Index `UQ_RolCategoria`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`RolesCategoriesKnowledge` ADD  CONSTRAINT `UQ_RolCategoria` UNIQUE NONCLUSTERED 
(
	`idRol` ASC,
	`idCategoria` ASC
) 
;
/****** Object:  Index `IX_RolesCategoriesKnowledge_Categoria`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_RolesCategoriesKnowledge_Categoria` ON `dbo`.`RolesCategoriesKnowledge`
(
	`idCategoria` ASC,
	`activo` ASC
) 
;
/****** Object:  Index `IX_RolesCategoriesKnowledge_Rol`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_RolesCategoriesKnowledge_Rol` ON `dbo`.`RolesCategoriesKnowledge`
(
	`idRol` ASC,
	`activo` ASC
) 
;

/****** Object:  Index `UQ_RolesIA_Nombre`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`RolesIA` ADD  CONSTRAINT `UQ_RolesIA_Nombre` UNIQUE NONCLUSTERED 
(
	`nombre` ASC
) 
;
/****** Object:  Index `UQ_RolesOperaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`RolesOperaciones` ADD  CONSTRAINT `UQ_RolesOperaciones` UNIQUE NONCLUSTERED 
(
	`idRol` ASC,
	`idOperacion` ASC
) 
;
/****** Object:  Index `IX_RolesOperaciones_IdOperacion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_RolesOperaciones_IdOperacion` ON `dbo`.`RolesOperaciones`
(
	`idOperacion` ASC
) 
;
/****** Object:  Index `IX_RolesOperaciones_IdRol`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_RolesOperaciones_IdRol` ON `dbo`.`RolesOperaciones`
(
	`idRol` ASC
) 
;

/****** Object:  Index `UQ__Sistemas__72AFBCC602822F60`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`SistemasAplicaciones` ADD UNIQUE NONCLUSTERED 
(
	`nombre` ASC
) 
;
/****** Object:  Index `IX_SistemasAplicaciones_Activo`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_SistemasAplicaciones_Activo` ON `dbo`.`SistemasAplicaciones`
(
	`activo` ASC
)
WHERE (`activo`=(1))
 
;

/****** Object:  Index `UQ_table_documentation`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`table_documentation` ADD  CONSTRAINT `UQ_table_documentation` UNIQUE NONCLUSTERED 
(
	`schema_name` ASC,
	`table_name` ASC
) 
;
/****** Object:  Index `idx_table_documentation_active`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `idx_table_documentation_active` ON `dbo`.`table_documentation`
(
	`active` ASC
) 
;
/****** Object:  Index `UQ_UserMemoryProfiles_Usuario`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`UserMemoryProfiles` ADD  CONSTRAINT `UQ_UserMemoryProfiles_Usuario` UNIQUE NONCLUSTERED 
(
	`idUsuario` ASC
) 
;
/****** Object:  Index `IX_UserMemoryProfiles_UltimaActualizacion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UserMemoryProfiles_UltimaActualizacion` ON `dbo`.`UserMemoryProfiles`
(
	`ultimaActualizacion` DESC
) 
;
/****** Object:  Index `IX_UserMemoryProfiles_Usuario`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UserMemoryProfiles_Usuario` ON `dbo`.`UserMemoryProfiles`
(
	`idUsuario` ASC
) 
;

/****** Object:  Index `UQ_Usuarios_Email`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`Usuarios` ADD  CONSTRAINT `UQ_Usuarios_Email` UNIQUE NONCLUSTERED 
(
	`email` ASC
) 
;
/****** Object:  Index `UQ_Usuarios_IdEmpleado`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`Usuarios` ADD  CONSTRAINT `UQ_Usuarios_IdEmpleado` UNIQUE NONCLUSTERED 
(
	`idEmpleado` ASC
) 
;

/****** Object:  Index `IX_Usuarios_Email`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_Usuarios_Email` ON `dbo`.`Usuarios`
(
	`email` ASC
) 
;
/****** Object:  Index `IX_Usuarios_IdEmpleado`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_Usuarios_IdEmpleado` ON `dbo`.`Usuarios`
(
	`idEmpleado` ASC
) 
;
/****** Object:  Index `UQ_UsuariosOperaciones`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`UsuariosOperaciones` ADD  CONSTRAINT `UQ_UsuariosOperaciones` UNIQUE NONCLUSTERED 
(
	`idUsuario` ASC,
	`idOperacion` ASC
) 
;
/****** Object:  Index `IX_UsuariosOperaciones_IdOperacion`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosOperaciones_IdOperacion` ON `dbo`.`UsuariosOperaciones`
(
	`idOperacion` ASC
) 
;
/****** Object:  Index `IX_UsuariosOperaciones_IdUsuario`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosOperaciones_IdUsuario` ON `dbo`.`UsuariosOperaciones`
(
	`idUsuario` ASC
) 
;
/****** Object:  Index `UQ_UsuariosRolesIA`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`UsuariosRolesIA` ADD  CONSTRAINT `UQ_UsuariosRolesIA` UNIQUE NONCLUSTERED 
(
	`idRol` ASC,
	`idUsuario` ASC
) 
;
/****** Object:  Index `IX_UsuariosRolesIA_IdRol`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosRolesIA_IdRol` ON `dbo`.`UsuariosRolesIA`
(
	`idRol` ASC
) 
;
/****** Object:  Index `IX_UsuariosRolesIA_IdUsuario`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosRolesIA_IdUsuario` ON `dbo`.`UsuariosRolesIA`
(
	`idUsuario` ASC
) 
;
/****** Object:  Index `UQ_UsuariosTelegram_ChatId`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  CONSTRAINT `UQ_UsuariosTelegram_ChatId` UNIQUE NONCLUSTERED 
(
	`telegramChatId` ASC
) 
;
/****** Object:  Index `IX_UsuariosTelegram_ChatId`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosTelegram_ChatId` ON `dbo`.`UsuariosTelegram`
(
	`telegramChatId` ASC
) 
;

/****** Object:  Index `IX_UsuariosTelegram_Estado`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosTelegram_Estado` ON `dbo`.`UsuariosTelegram`
(
	`estado` ASC
) 
;
/****** Object:  Index `IX_UsuariosTelegram_IdUsuario`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosTelegram_IdUsuario` ON `dbo`.`UsuariosTelegram`
(
	`idUsuario` ASC
) 
;

/****** Object:  Index `IX_UsuariosTelegram_Username`    Script DATE: 29/12/2025 07:09:28 p. m. ******/
CREATE INDEX `IX_UsuariosTelegram_Username` ON `dbo`.`UsuariosTelegram`
(
	`telegramUsername` ASC
) 
;
ALTER TABLE `dbo`.`AreaAtendedora` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`AreaAtendedora` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`BibliotecaPrompts` ADD  DEFAULT ((1)) FOR `version`
;
ALTER TABLE `dbo`.`BibliotecaPrompts` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`BibliotecaPrompts` ADD  DEFAULT ((0)) FOR `favorito`
;
ALTER TABLE `dbo`.`BibliotecaPrompts` ADD  DEFAULT ((0)) FOR `cantidadEjecuciones`
;
ALTER TABLE `dbo`.`BibliotecaPrompts` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`CategoriasPrompt` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`CategoriasPrompt` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT ((0.7)) FOR `Temperatura`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT ((0)) FOR `TotalMensajes`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT ((0)) FOR `TotalTokensUsados`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT ((0)) FOR `CostoTotal`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT ((0)) FOR `Favorita`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT ((0)) FOR `Archivada`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT ((1)) FOR `Activa`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT (NOW()) FOR `FechaCreacion`
;
ALTER TABLE `dbo`.`ChatConversaciones` ADD  DEFAULT (NOW()) FOR `FechaUltimaActividad`
;
ALTER TABLE `dbo`.`ChatConversacionesCompartidas` ADD  DEFAULT ((0)) FOR `PermiteComentarios`
;
ALTER TABLE `dbo`.`ChatConversacionesCompartidas` ADD  DEFAULT ((0)) FOR `PasswordProtegida`
;
ALTER TABLE `dbo`.`ChatConversacionesCompartidas` ADD  DEFAULT ((0)) FOR `VistasCount`
;
ALTER TABLE `dbo`.`ChatConversacionesCompartidas` ADD  DEFAULT ((1)) FOR `Activa`
;
ALTER TABLE `dbo`.`ChatConversacionesCompartidas` ADD  DEFAULT (NOW()) FOR `FechaCreacion`
;
ALTER TABLE `dbo`.`ChatMensajes` ADD  DEFAULT (NOW()) FOR `FechaCreacion`
;
ALTER TABLE `dbo`.`ChatPermisosRol` ADD  DEFAULT ((0)) FOR `PuedeUsarChat`
;
ALTER TABLE `dbo`.`ChatPermisosRol` ADD  DEFAULT ((0)) FOR `PuedeVerHistorial`
;
ALTER TABLE `dbo`.`ChatPermisosRol` ADD  DEFAULT ((0)) FOR `PuedeExportarConversaciones`
;
ALTER TABLE `dbo`.`ChatPermisosRol` ADD  DEFAULT ((0)) FOR `PuedeUsarIA`
;
ALTER TABLE `dbo`.`ChatPermisosRol` ADD  DEFAULT ((1)) FOR `Activo`
;
ALTER TABLE `dbo`.`ChatPermisosRol` ADD  DEFAULT (NOW()) FOR `FechaCreacion`
;
ALTER TABLE `dbo`.`ChatPlantillasPrompt` ADD  DEFAULT ((0)) FOR `UsosCount`
;
ALTER TABLE `dbo`.`ChatPlantillasPrompt` ADD  DEFAULT ((0)) FOR `Publica`
;
ALTER TABLE `dbo`.`ChatPlantillasPrompt` ADD  DEFAULT ((1)) FOR `Activa`
;
ALTER TABLE `dbo`.`ChatPlantillasPrompt` ADD  DEFAULT (NOW()) FOR `FechaCreacion`
;
ALTER TABLE `dbo`.`column_documentation` ADD  DEFAULT ((0)) FOR `is_key`
;
ALTER TABLE `dbo`.`column_documentation` ADD  DEFAULT (NOW()) FOR `created_at`
;
ALTER TABLE `dbo`.`column_documentation` ADD  DEFAULT (NOW()) FOR `updated_at`
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos` ADD  DEFAULT ((0)) FOR `creditosDisponibles`
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos` ADD  DEFAULT ((0)) FOR `creditosIniciales`
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas` ADD  DEFAULT ((0)) FOR `creditosDisponibles`
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas` ADD  DEFAULT ((0)) FOR `creditosIniciales`
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`EjecucionesPrompt` ADD  DEFAULT ((0)) FOR `exitoso`
;
ALTER TABLE `dbo`.`EjecucionesPrompt` ADD  DEFAULT (NOW()) FOR `fechaEjecucion`
;
ALTER TABLE `dbo`.`EtiquetasPrompt` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`EtiquetasPrompt` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`Gerencias` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`Gerencias` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`GerenciasRolesIA` ADD  DEFAULT (NOW()) FOR `fechaAsignacion`
;
ALTER TABLE `dbo`.`GerenciasRolesIA` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`GerenciaUsuarios` ADD  DEFAULT (NOW()) FOR `fechaAsignacion`
;
ALTER TABLE `dbo`.`GerenciaUsuarios` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`Iconos` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`Iconos` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`knowledge_categories` ADD  DEFAULT ((1)) FOR `active`
;
ALTER TABLE `dbo`.`knowledge_categories` ADD  DEFAULT (NOW()) FOR `created_at`
;
ALTER TABLE `dbo`.`knowledge_categories` ADD  DEFAULT (NOW()) FOR `updated_at`
;
ALTER TABLE `dbo`.`knowledge_entries` ADD  DEFAULT ((1)) FOR `priority`
;
ALTER TABLE `dbo`.`knowledge_entries` ADD  DEFAULT ((1)) FOR `active`
;
ALTER TABLE `dbo`.`knowledge_entries` ADD  DEFAULT (NOW()) FOR `created_at`
;
ALTER TABLE `dbo`.`knowledge_entries` ADD  DEFAULT (NOW()) FOR `updated_at`
;
ALTER TABLE `dbo`.`knowledge_entries` ADD  DEFAULT ('system') FOR `created_by`
;
ALTER TABLE `dbo`.`LogOperaciones` ADD  DEFAULT (NOW()) FOR `fechaEjecucion`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT ('fa fa-circle-o') FOR `icono`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT ((0)) FOR `orden`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT ((0)) FOR `nivel`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT ((0)) FOR `esHeader`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT ((0)) FOR `esTreeview`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT ((1)) FOR `requiresAuth`
;
ALTER TABLE `dbo`.`MenuNavegacion` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`ModelosIA` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`ModelosIA` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`Modulos` ADD  DEFAULT ((0)) FOR `orden`
;
ALTER TABLE `dbo`.`Modulos` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`Modulos` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`Operaciones` ADD  DEFAULT ((0)) FOR `requiereParametros`
;
ALTER TABLE `dbo`.`Operaciones` ADD  DEFAULT ((1)) FOR `nivelCriticidad`
;
ALTER TABLE `dbo`.`Operaciones` ADD  DEFAULT ((0)) FOR `orden`
;
ALTER TABLE `dbo`.`Operaciones` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`Operaciones` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`ProveedoresIA` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`ProveedoresIA` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`Roles` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`Roles` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`RolesCategoriesKnowledge` ADD  DEFAULT ((1)) FOR `permitido`
;
ALTER TABLE `dbo`.`RolesCategoriesKnowledge` ADD  DEFAULT (NOW()) FOR `fechaAsignacion`
;
ALTER TABLE `dbo`.`RolesCategoriesKnowledge` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`RolesIA` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`RolesIA` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`RolesOperaciones` ADD  DEFAULT ((1)) FOR `permitido`
;
ALTER TABLE `dbo`.`RolesOperaciones` ADD  DEFAULT (NOW()) FOR `fechaAsignacion`
;
ALTER TABLE `dbo`.`RolesOperaciones` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`SistemasAplicaciones` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`SistemasAplicaciones` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`table_documentation` ADD  DEFAULT ('dbo') FOR `schema_name`
;
ALTER TABLE `dbo`.`table_documentation` ADD  DEFAULT ((1)) FOR `active`
;
ALTER TABLE `dbo`.`table_documentation` ADD  DEFAULT (NOW()) FOR `created_at`
;
ALTER TABLE `dbo`.`table_documentation` ADD  DEFAULT (NOW()) FOR `updated_at`
;
ALTER TABLE `dbo`.`UserMemoryProfiles` ADD  DEFAULT ((0)) FOR `numInteracciones`
;
ALTER TABLE `dbo`.`UserMemoryProfiles` ADD  DEFAULT (NOW()) FOR `ultimaActualizacion`
;
ALTER TABLE `dbo`.`UserMemoryProfiles` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`UserMemoryProfiles` ADD  DEFAULT ((1)) FOR `version`
;
ALTER TABLE `dbo`.`Usuarios` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`Usuarios` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`UsuariosOperaciones` ADD  DEFAULT ((1)) FOR `permitido`
;
ALTER TABLE `dbo`.`UsuariosOperaciones` ADD  DEFAULT (NOW()) FOR `fechaAsignacion`
;
ALTER TABLE `dbo`.`UsuariosOperaciones` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`UsuariosRolesIA` ADD  DEFAULT (NOW()) FOR `fechaAsignacion`
;
ALTER TABLE `dbo`.`UsuariosRolesIA` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT ((0)) FOR `esPrincipal`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT ('ACTIVO') FOR `estado`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT (NOW()) FOR `fechaRegistro`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT ((0)) FOR `verificado`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT ((0)) FOR `intentosVerificacion`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT ((1)) FOR `notificacionesActivas`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT ((1)) FOR `activo`
;
ALTER TABLE `dbo`.`UsuariosTelegram` ADD  DEFAULT (NOW()) FOR `fechaCreacion`
;
ALTER TABLE `dbo`.`AreaAtendedora`  WITH CHECK ADD  CONSTRAINT `FK_AreaAtendedora_Gerencias` FOREIGN KEY(`idGerencia`)
REFERENCES `dbo`.`Gerencias` (`idGerencia`)
;
ALTER TABLE `dbo`.`AreaAtendedora` CHECK CONSTRAINT `FK_AreaAtendedora_Gerencias`
;
ALTER TABLE `dbo`.`BibliotecaPrompts`  WITH CHECK ADD  CONSTRAINT `FK_BibliotecaPrompts_Categoria` FOREIGN KEY(`idCategoriaPrompt`)
REFERENCES `dbo`.`CategoriasPrompt` (`idCategoriaPrompt`)
;
ALTER TABLE `dbo`.`BibliotecaPrompts` CHECK CONSTRAINT `FK_BibliotecaPrompts_Categoria`
;
ALTER TABLE `dbo`.`ChatConversacionesCompartidas`  WITH CHECK ADD  CONSTRAINT `FK_ChatCompartidas_Conversacion` FOREIGN KEY(`IdConversacion`)
REFERENCES `dbo`.`ChatConversaciones` (`IdConversacion`)
ON DELETE CASCADE
;
ALTER TABLE `dbo`.`ChatConversacionesCompartidas` CHECK CONSTRAINT `FK_ChatCompartidas_Conversacion`
;
ALTER TABLE `dbo`.`ChatMensajes`  WITH CHECK ADD  CONSTRAINT `FK_ChatMensajes_Conversacion` FOREIGN KEY(`IdConversacion`)
REFERENCES `dbo`.`ChatConversaciones` (`IdConversacion`)
ON DELETE CASCADE
;
ALTER TABLE `dbo`.`ChatMensajes` CHECK CONSTRAINT `FK_ChatMensajes_Conversacion`
;
ALTER TABLE `dbo`.`column_documentation`  WITH CHECK ADD  CONSTRAINT `FK_column_documentation_table` FOREIGN KEY(`table_doc_id`)
REFERENCES `dbo`.`table_documentation` (`id`)
ON DELETE CASCADE
;
ALTER TABLE `dbo`.`column_documentation` CHECK CONSTRAINT `FK_column_documentation_table`
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos`  WITH CHECK ADD  CONSTRAINT `FK_ConfiguracionIA_ModelosIA` FOREIGN KEY(`idModeloIA`)
REFERENCES `dbo`.`ModelosIA` (`idModeloIA`)
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos` CHECK CONSTRAINT `FK_ConfiguracionIA_ModelosIA`
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos`  WITH CHECK ADD  CONSTRAINT `FK_ConfiguracionIA_Modulos` FOREIGN KEY(`idModulo`)
REFERENCES `dbo`.`Modulos` (`idModulo`)
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos` CHECK CONSTRAINT `FK_ConfiguracionIA_Modulos`
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos`  WITH CHECK ADD  CONSTRAINT `FK_ConfiguracionIA_ProveedoresIA` FOREIGN KEY(`idProveedorIA`)
REFERENCES `dbo`.`ProveedoresIA` (`idProveedorIA`)
;
ALTER TABLE `dbo`.`ConfiguracionIAModulos` CHECK CONSTRAINT `FK_ConfiguracionIA_ProveedoresIA`
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas`  WITH CHECK ADD  CONSTRAINT `FK_ConfiguracionIASistemas_ModelosIA` FOREIGN KEY(`idModeloIA`)
REFERENCES `dbo`.`ModelosIA` (`idModeloIA`)
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas` CHECK CONSTRAINT `FK_ConfiguracionIASistemas_ModelosIA`
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas`  WITH CHECK ADD  CONSTRAINT `FK_ConfiguracionIASistemas_ProveedoresIA` FOREIGN KEY(`idProveedorIA`)
REFERENCES `dbo`.`ProveedoresIA` (`idProveedorIA`)
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas` CHECK CONSTRAINT `FK_ConfiguracionIASistemas_ProveedoresIA`
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas`  WITH CHECK ADD  CONSTRAINT `FK_ConfiguracionIASistemas_SistemasAplicaciones` FOREIGN KEY(`idSistemaAplicacion`)
REFERENCES `dbo`.`SistemasAplicaciones` (`idSistemaAplicacion`)
;
ALTER TABLE `dbo`.`ConfiguracionIASistemas` CHECK CONSTRAINT `FK_ConfiguracionIASistemas_SistemasAplicaciones`
;
ALTER TABLE `dbo`.`EjecucionesPrompt`  WITH CHECK ADD  CONSTRAINT `FK_EjecucionesPrompt_Prompt` FOREIGN KEY(`idPrompt`)
REFERENCES `dbo`.`BibliotecaPrompts` (`idPrompt`)
;
ALTER TABLE `dbo`.`EjecucionesPrompt` CHECK CONSTRAINT `FK_EjecucionesPrompt_Prompt`
;
ALTER TABLE `dbo`.`Gerencias`  WITH CHECK ADD  CONSTRAINT `FK_Gerencias_Usuarios` FOREIGN KEY(`idResponsable`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`Gerencias` CHECK CONSTRAINT `FK_Gerencias_Usuarios`
;
ALTER TABLE `dbo`.`GerenciasRolesIA`  WITH CHECK ADD  CONSTRAINT `FK_GerenciasRolesIA_Gerencias` FOREIGN KEY(`idGerencia`)
REFERENCES `dbo`.`Gerencias` (`idGerencia`)
;
ALTER TABLE `dbo`.`GerenciasRolesIA` CHECK CONSTRAINT `FK_GerenciasRolesIA_Gerencias`
;
ALTER TABLE `dbo`.`GerenciasRolesIA`  WITH CHECK ADD  CONSTRAINT `FK_GerenciasRolesIA_RolesIA` FOREIGN KEY(`idRol`)
REFERENCES `dbo`.`RolesIA` (`idRol`)
;
ALTER TABLE `dbo`.`GerenciasRolesIA` CHECK CONSTRAINT `FK_GerenciasRolesIA_RolesIA`
;
ALTER TABLE `dbo`.`GerenciaUsuarios`  WITH CHECK ADD  CONSTRAINT `FK_GerenciaUsuarios_Gerencias` FOREIGN KEY(`idGerencia`)
REFERENCES `dbo`.`Gerencias` (`idGerencia`)
;
ALTER TABLE `dbo`.`GerenciaUsuarios` CHECK CONSTRAINT `FK_GerenciaUsuarios_Gerencias`
;
ALTER TABLE `dbo`.`GerenciaUsuarios`  WITH CHECK ADD  CONSTRAINT `FK_GerenciaUsuarios_Usuarios` FOREIGN KEY(`idUsuario`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`GerenciaUsuarios` CHECK CONSTRAINT `FK_GerenciaUsuarios_Usuarios`
;
ALTER TABLE `dbo`.`knowledge_entries`  WITH CHECK ADD  CONSTRAINT `FK_knowledge_entries_category` FOREIGN KEY(`category_id`)
REFERENCES `dbo`.`knowledge_categories` (`id`)
;
ALTER TABLE `dbo`.`knowledge_entries` CHECK CONSTRAINT `FK_knowledge_entries_category`
;
ALTER TABLE `dbo`.`LogOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_LogOperaciones_Operaciones` FOREIGN KEY(`idOperacion`)
REFERENCES `dbo`.`Operaciones` (`idOperacion`)
;
ALTER TABLE `dbo`.`LogOperaciones` CHECK CONSTRAINT `FK_LogOperaciones_Operaciones`
;
ALTER TABLE `dbo`.`LogOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_LogOperaciones_Usuarios` FOREIGN KEY(`idUsuario`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`LogOperaciones` CHECK CONSTRAINT `FK_LogOperaciones_Usuarios`
;
ALTER TABLE `dbo`.`MenuNavegacion`  WITH CHECK ADD  CONSTRAINT `FK_MenuNavegacion_MenuPadre` FOREIGN KEY(`idMenuPadre`)
REFERENCES `dbo`.`MenuNavegacion` (`idMenu`)
;
ALTER TABLE `dbo`.`MenuNavegacion` CHECK CONSTRAINT `FK_MenuNavegacion_MenuPadre`
;
ALTER TABLE `dbo`.`ModelosIA`  WITH CHECK ADD  CONSTRAINT `FK_ModelosIA_ProveedoresIA` FOREIGN KEY(`idProveedorIA`)
REFERENCES `dbo`.`ProveedoresIA` (`idProveedorIA`)
;
ALTER TABLE `dbo`.`ModelosIA` CHECK CONSTRAINT `FK_ModelosIA_ProveedoresIA`
;
ALTER TABLE `dbo`.`Operaciones`  WITH CHECK ADD  CONSTRAINT `FK_Operaciones_Modulos` FOREIGN KEY(`idModulo`)
REFERENCES `dbo`.`Modulos` (`idModulo`)
;
ALTER TABLE `dbo`.`Operaciones` CHECK CONSTRAINT `FK_Operaciones_Modulos`
;
ALTER TABLE `dbo`.`ParametrosEjecucion`  WITH CHECK ADD  CONSTRAINT `FK_ParametrosEjecucion_Ejecucion` FOREIGN KEY(`idEjecucionPrompt`)
REFERENCES `dbo`.`EjecucionesPrompt` (`idEjecucionPrompt`)
ON DELETE CASCADE
;
ALTER TABLE `dbo`.`ParametrosEjecucion` CHECK CONSTRAINT `FK_ParametrosEjecucion_Ejecucion`
;
ALTER TABLE `dbo`.`PromptEtiquetas`  WITH CHECK ADD  CONSTRAINT `FK_PromptEtiquetas_Etiqueta` FOREIGN KEY(`idEtiquetaPrompt`)
REFERENCES `dbo`.`EtiquetasPrompt` (`idEtiquetaPrompt`)
ON DELETE CASCADE
;
ALTER TABLE `dbo`.`PromptEtiquetas` CHECK CONSTRAINT `FK_PromptEtiquetas_Etiqueta`
;
ALTER TABLE `dbo`.`PromptEtiquetas`  WITH CHECK ADD  CONSTRAINT `FK_PromptEtiquetas_Prompt` FOREIGN KEY(`idPrompt`)
REFERENCES `dbo`.`BibliotecaPrompts` (`idPrompt`)
ON DELETE CASCADE
;
ALTER TABLE `dbo`.`PromptEtiquetas` CHECK CONSTRAINT `FK_PromptEtiquetas_Prompt`
;
ALTER TABLE `dbo`.`RolesCategoriesKnowledge`  WITH CHECK ADD  CONSTRAINT `FK_RolesCategoriesKnowledge_Categories` FOREIGN KEY(`idCategoria`)
REFERENCES `dbo`.`knowledge_categories` (`id`)
;
ALTER TABLE `dbo`.`RolesCategoriesKnowledge` CHECK CONSTRAINT `FK_RolesCategoriesKnowledge_Categories`
;
ALTER TABLE `dbo`.`RolesCategoriesKnowledge`  WITH CHECK ADD  CONSTRAINT `FK_RolesCategoriesKnowledge_Roles` FOREIGN KEY(`idRol`)
REFERENCES `dbo`.`Roles` (`idRol`)
;
ALTER TABLE `dbo`.`RolesCategoriesKnowledge` CHECK CONSTRAINT `FK_RolesCategoriesKnowledge_Roles`
;
ALTER TABLE `dbo`.`RolesOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_RolesOperaciones_Operaciones` FOREIGN KEY(`idOperacion`)
REFERENCES `dbo`.`Operaciones` (`idOperacion`)
;
ALTER TABLE `dbo`.`RolesOperaciones` CHECK CONSTRAINT `FK_RolesOperaciones_Operaciones`
;
ALTER TABLE `dbo`.`RolesOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_RolesOperaciones_Roles` FOREIGN KEY(`idRol`)
REFERENCES `dbo`.`Roles` (`idRol`)
;
ALTER TABLE `dbo`.`RolesOperaciones` CHECK CONSTRAINT `FK_RolesOperaciones_Roles`
;
ALTER TABLE `dbo`.`RolesOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_RolesOperaciones_Usuario` FOREIGN KEY(`usuarioAsignacion`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`RolesOperaciones` CHECK CONSTRAINT `FK_RolesOperaciones_Usuario`
;
ALTER TABLE `dbo`.`UserMemoryProfiles`  WITH CHECK ADD  CONSTRAINT `FK_UserMemoryProfiles_Usuarios` FOREIGN KEY(`idUsuario`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
ON DELETE CASCADE
;
ALTER TABLE `dbo`.`UserMemoryProfiles` CHECK CONSTRAINT `FK_UserMemoryProfiles_Usuarios`
;
ALTER TABLE `dbo`.`Usuarios`  WITH CHECK ADD  CONSTRAINT `FK_Usuarios_Roles` FOREIGN KEY(`rol`)
REFERENCES `dbo`.`Roles` (`idRol`)
;
ALTER TABLE `dbo`.`Usuarios` CHECK CONSTRAINT `FK_Usuarios_Roles`
;
ALTER TABLE `dbo`.`UsuariosOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosOperaciones_Operaciones` FOREIGN KEY(`idOperacion`)
REFERENCES `dbo`.`Operaciones` (`idOperacion`)
;
ALTER TABLE `dbo`.`UsuariosOperaciones` CHECK CONSTRAINT `FK_UsuariosOperaciones_Operaciones`
;
ALTER TABLE `dbo`.`UsuariosOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosOperaciones_Usuario` FOREIGN KEY(`usuarioAsignacion`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`UsuariosOperaciones` CHECK CONSTRAINT `FK_UsuariosOperaciones_Usuario`
;
ALTER TABLE `dbo`.`UsuariosOperaciones`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosOperaciones_Usuarios` FOREIGN KEY(`idUsuario`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`UsuariosOperaciones` CHECK CONSTRAINT `FK_UsuariosOperaciones_Usuarios`
;
ALTER TABLE `dbo`.`UsuariosRolesIA`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosRolesIA_RolesIA` FOREIGN KEY(`idRol`)
REFERENCES `dbo`.`RolesIA` (`idRol`)
;
ALTER TABLE `dbo`.`UsuariosRolesIA` CHECK CONSTRAINT `FK_UsuariosRolesIA_RolesIA`
;
ALTER TABLE `dbo`.`UsuariosRolesIA`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosRolesIA_Usuarios` FOREIGN KEY(`idUsuario`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`UsuariosRolesIA` CHECK CONSTRAINT `FK_UsuariosRolesIA_Usuarios`
;
ALTER TABLE `dbo`.`UsuariosTelegram`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosTelegram_UsuarioCreacion` FOREIGN KEY(`usuarioCreacion`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`UsuariosTelegram` CHECK CONSTRAINT `FK_UsuariosTelegram_UsuarioCreacion`
;
ALTER TABLE `dbo`.`UsuariosTelegram`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosTelegram_UsuarioModificacion` FOREIGN KEY(`usuarioModificacion`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`UsuariosTelegram` CHECK CONSTRAINT `FK_UsuariosTelegram_UsuarioModificacion`
;
ALTER TABLE `dbo`.`UsuariosTelegram`  WITH CHECK ADD  CONSTRAINT `FK_UsuariosTelegram_Usuarios` FOREIGN KEY(`idUsuario`)
REFERENCES `dbo`.`Usuarios` (`idUsuario`)
;
ALTER TABLE `dbo`.`UsuariosTelegram` CHECK CONSTRAINT `FK_UsuariosTelegram_Usuarios`
;
ALTER TABLE `dbo`.`knowledge_entries`  WITH CHECK ADD  CONSTRAINT `CK_knowledge_entries_priority` CHECK  ((`priority`>=(1) AND `priority`<=(3)))
;
ALTER TABLE `dbo`.`knowledge_entries` CHECK CONSTRAINT `CK_knowledge_entries_priority`
;
ALTER TABLE `dbo`.`UsuariosTelegram`  WITH CHECK ADD  CONSTRAINT `CK_UsuariosTelegram_Estado` CHECK  ((`estado`='BLOQUEADO' OR `estado`='SUSPENDIDO' OR `estado`='ACTIVO'))
;
ALTER TABLE `dbo`.`UsuariosTelegram` CHECK CONSTRAINT `CK_UsuariosTelegram_Estado`
;
/****** Object:  StoredProcedure `dbo`.`sp_ActualizarActividadTelegram`    Script DATE: 29/12/2025 07:09:29 p. m. ******/



CREATE PROCEDURE `dbo`.`sp_ActualizarActividadTelegram`
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE UsuariosTelegram
    SET fechaUltimaActividad = NOW()
    WHERE telegramChatId = @telegramChatId
        AND activo = 1;

    SELECT @@ROWCOUNT AS FilasActualizadas;
END
;
/****** Object:  StoredProcedure `dbo`.`sp_ObtenerOperacionesUsuario`    Script DATE: 29/12/2025 07:09:29 p. m. ******/



CREATE PROCEDURE `dbo`.`sp_ObtenerOperacionesUsuario`
    @idUsuario INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @rolUsuario INT;

    -- Obtener rol del usuario
    SELECT @rolUsuario = rol
    FROM Usuarios
    WHERE idUsuario = @idUsuario AND activo = 1;

    IF @rolUsuario IS NULL
    BEGIN
        -- Usuario no encontrado
        SELECT
            NULL AS Modulo,
            NULL AS IconoModulo,
            NULL AS idOperacion,
            NULL AS Operacion,
            NULL AS descripcion,
            NULL AS comando,
            NULL AS requiereParametros,
            NULL AS parametrosEjemplo,
            NULL AS nivelCriticidad,
            NULL AS OrigenPermiso,
            0 AS Permitido
        WHERE 1 = 0; -- Retornar resultado vacío
        RETURN;
    END

    -- Obtener operaciones combinando permisos de rol y usuario
    SELECT DISTINCT
        m.nombre AS Modulo,
        m.icono AS IconoModulo,
        m.orden AS OrdenModulo,
        o.idOperacion,
        o.nombre AS Operacion,
        o.descripcion,
        o.comando,
        o.requiereParametros,
        o.parametrosEjemplo,
        o.nivelCriticidad,
        o.orden AS OrdenOperacion,
        CASE
            WHEN uo.idUsuarioOperacion IS NOT NULL THEN 'Usuario'
            ELSE 'Rol'
        END AS OrigenPermiso,
        CASE
            WHEN uo.idUsuarioOperacion IS NOT NULL THEN uo.permitido
            ELSE ro.permitido
        END AS Permitido
    FROM Operaciones o
    INNER JOIN Modulos m ON o.idModulo = m.idModulo
    LEFT JOIN RolesOperaciones ro ON o.idOperacion = ro.idOperacion
        AND ro.idRol = @rolUsuario
        AND ro.activo = 1
    LEFT JOIN UsuariosOperaciones uo ON o.idOperacion = uo.idOperacion
        AND uo.idUsuario = @idUsuario
        AND uo.activo = 1
        AND (uo.fechaExpiracion IS NULL OR uo.fechaExpiracion > NOW())
    WHERE o.activo = 1
        AND m.activo = 1
        AND (
            (uo.idUsuarioOperacion IS NOT NULL AND uo.permitido = 1)
            OR (uo.idUsuarioOperacion IS NULL AND ro.idRolOperacion IS NOT NULL AND ro.permitido = 1)
        )
    ORDER BY m.orden, o.orden, o.nombre;
END
;
/****** Object:  StoredProcedure `dbo`.`sp_RegistrarLogOperacion`    Script DATE: 29/12/2025 07:09:29 p. m. ******/



CREATE PROCEDURE `dbo`.`sp_RegistrarLogOperacion`
    @idUsuario INT,
    @comando VARCHAR(100),
    @telegramChatId BIGINT = NULL,
    @telegramUsername VARCHAR(100) = NULL,
    @parametros NVARCHAR(MAX) = NULL,
    @resultado VARCHAR(50) = 'EXITOSO',
    @mensajeError NVARCHAR(MAX) = NULL,
    @duracionMs INT = NULL,
    @ipOrigen VARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @idOperacion INT;

    -- Buscar la operación por comando
    SELECT @idOperacion = idOperacion
    FROM Operaciones
    WHERE comando = @comando;

    -- Si no encuentra la operación, buscar una operación genérica o crear un log sin idOperacion
    IF @idOperacion IS NULL
    BEGIN
        -- Intentar encontrar una operación genérica para "comando desconocido"
        SELECT @idOperacion = idOperacion
        FROM Operaciones
        WHERE nombre = 'Operación Desconocida' OR comando IS NULL
        ORDER BY idOperacion
        OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY;
    END

    -- Insertar log
    INSERT INTO LogOperaciones (
        idUsuario,
        idOperacion,
        telegramChatId,
        telegramUsername,
        parametros,
        resultado,
        mensajeError,
        duracionMs,
        ipOrigen,
        fechaEjecucion
    )
    VALUES (
        @idUsuario,
        @idOperacion,
        @telegramChatId,
        @telegramUsername,
        @parametros,
        @resultado,
        @mensajeError,
        @duracionMs,
        @ipOrigen,
        NOW()
    );

    -- Retornar el ID del log insertado
    SELECT SCOPE_IDENTITY() AS idLog;
END
;
/****** Object:  StoredProcedure `dbo`.`sp_search_knowledge`    Script DATE: 29/12/2025 07:09:29 p. m. ******/



CREATE PROCEDURE `dbo`.`sp_search_knowledge`
    @query VARCHAR(500),
    @category VARCHAR(50) = NULL,
    @top_k INT = 3,
    @min_priority INT = 1
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP (@top_k)
        e.id,
        e.question,
        e.answer,
        e.keywords,
        e.related_commands,
        e.priority,
        c.name as category,
        c.display_name as category_display_name,
        c.icon as category_icon,
        -- Score simple basado en prioridad
        CASE
            WHEN e.priority = 3 THEN 1.5
            WHEN e.priority = 2 THEN 1.2
            ELSE 1.0
        END as score
    FROM knowledge_entries e
    INNER JOIN knowledge_categories c ON e.category_id = c.id
    WHERE
        e.active = 1
        AND c.active = 1
        AND e.priority >= @min_priority
        AND (@category IS NULL OR c.name = @category)
        AND (
            e.question LIKE '%' + @query + '%'
            OR e.answer LIKE '%' + @query + '%'
            OR e.keywords LIKE '%' + @query + '%'
        )
    ORDER BY
        e.priority DESC,
        LENGTH(e.question) ASC; -- Preguntas más cortas primero
END
;
/****** Object:  StoredProcedure `dbo`.`sp_VerificarPermisoOperacion`    Script DATE: 29/12/2025 07:09:29 p. m. ******/



CREATE PROCEDURE `dbo`.`sp_VerificarPermisoOperacion`
    @idUsuario INT,
    @comando VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @tienePermiso TINYINT(1) = 0;
    DECLARE @mensaje VARCHAR(500);
    DECLARE @idOperacion INT;
    DECLARE @nombreOperacion VARCHAR(100);
    DECLARE @descripcionOperacion VARCHAR(500);
    DECLARE @requiereParametros TINYINT(1);
    DECLARE @parametrosEjemplo VARCHAR(500);
    DECLARE @rolUsuario INT;

    -- Verificar que el usuario existe y está activo
    IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE idUsuario = @idUsuario AND activo = 1)
    BEGIN
        SELECT
            0 AS TienePermiso,
            'Usuario no encontrado o inactivo' AS Mensaje,
            NULL AS NombreOperacion,
            NULL AS DescripcionOperacion,
            NULL AS RequiereParametros,
            NULL AS ParametrosEjemplo;
        RETURN;
    END

    -- Obtener rol del usuario
    SELECT @rolUsuario = rol FROM Usuarios WHERE idUsuario = @idUsuario;

    -- Buscar la operación por comando
    SELECT
        @idOperacion = idOperacion,
        @nombreOperacion = nombre,
        @descripcionOperacion = descripcion,
        @requiereParametros = requiereParametros,
        @parametrosEjemplo = parametrosEjemplo
    FROM Operaciones
    WHERE comando = @comando AND activo = 1;

    -- Verificar que la operación existe
    IF @idOperacion IS NULL
    BEGIN
        SELECT
            0 AS TienePermiso,
            'Operación no encontrada' AS Mensaje,
            NULL AS NombreOperacion,
            NULL AS DescripcionOperacion,
            NULL AS RequiereParametros,
            NULL AS ParametrosEjemplo;
        RETURN;
    END

    -- Verificar permisos específicos del usuario (prioridad alta)
    IF EXISTS (
        SELECT 1
        FROM UsuariosOperaciones
        WHERE idUsuario = @idUsuario
            AND idOperacion = @idOperacion
            AND activo = 1
            AND (fechaExpiracion IS NULL OR fechaExpiracion > NOW())
    )
    BEGIN
        SELECT @tienePermiso = permitido
        FROM UsuariosOperaciones
        WHERE idUsuario = @idUsuario
            AND idOperacion = @idOperacion
            AND activo = 1
            AND (fechaExpiracion IS NULL OR fechaExpiracion > NOW());

        SET @mensaje = CASE
            WHEN @tienePermiso = 1 THEN 'Permiso concedido (permiso específico de usuario)'
            ELSE 'Permiso denegado (permiso específico de usuario)'
        END;
    END
    ELSE
    BEGIN
        -- Verificar permisos del rol
        IF EXISTS (
            SELECT 1
            FROM RolesOperaciones
            WHERE idRol = @rolUsuario
                AND idOperacion = @idOperacion
                AND activo = 1
        )
        BEGIN
            SELECT @tienePermiso = permitido
            FROM RolesOperaciones
            WHERE idRol = @rolUsuario
                AND idOperacion = @idOperacion
                AND activo = 1;

            SET @mensaje = CASE
                WHEN @tienePermiso = 1 THEN 'Permiso concedido (permiso de rol)'
                ELSE 'Permiso denegado (permiso de rol)'
            END;
        END
        ELSE
        BEGIN
            SET @tienePermiso = 0;
            SET @mensaje = 'Permiso no configurado para este usuario o rol';
        END
    END

    -- Retornar resultado
    SELECT
        @tienePermiso AS TienePermiso,
        @mensaje AS Mensaje,
        @nombreOperacion AS NombreOperacion,
        @descripcionOperacion AS DescripcionOperacion,
        @requiereParametros AS RequiereParametros,
        @parametrosEjemplo AS ParametrosEjemplo;
END
;
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Control de acceso a categorías de KnowledgeBase por rol. Define qué roles tienen acceso a qué categorías de la base de conocimiento.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'RolesCategoriesKnowledge'
;




-- ============================================================================
-- Fin del script
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;
