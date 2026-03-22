"""
Conversor de SQL Server a MySQL.

Esta herramienta convierte scripts SQL de SQL Server a MySQL, manejando:
- Tipos de datos
- Sintaxis de IDENTITY/AUTO_INCREMENT
- Funciones específicas
- Comentarios y delimitadores
- Índices y constraints

Uso:
    python scripts/sql_converter.py <archivo_entrada.sql> [archivo_salida.sql]
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple


class SQLServerToMySQLConverter:
    """Conversor de scripts SQL Server a MySQL."""

    # Mapeo de tipos de datos
    DATA_TYPE_MAP = {
        # Tipos de texto
        r'\bNVARCHAR\(MAX\)\b': 'TEXT',
        r'\bNVARCHAR\((\d+)\)': r'VARCHAR(\1)',
        r'\bVARCHAR\(MAX\)\b': 'TEXT',
        r'\bNTEXT\b': 'LONGTEXT',
        r'\bTEXT\b': 'TEXT',
        r'\bNCHAR\((\d+)\)': r'CHAR(\1)',

        # Tipos numéricos
        r'\bBIGINT\b': 'BIGINT',
        r'\bINT\b': 'INT',
        r'\bSMALLINT\b': 'SMALLINT',
        r'\bTINYINT\b': 'TINYINT',
        r'\bBIT\b': 'TINYINT(1)',  # En MySQL, BIT(1) o TINYINT(1)
        r'\bDECIMAL\((\d+),\s*(\d+)\)': r'DECIMAL(\1,\2)',
        r'\bNUMERIC\((\d+),\s*(\d+)\)': r'DECIMAL(\1,\2)',
        r'\bMONEY\b': 'DECIMAL(19,4)',
        r'\bSMALLMONEY\b': 'DECIMAL(10,4)',
        r'\bFLOAT\b': 'FLOAT',
        r'\bREAL\b': 'FLOAT',

        # Tipos de fecha/hora
        r'\bDATETIME2\(\d+\)\b': 'DATETIME',
        r'\bDATETIME2\b': 'DATETIME',
        r'\bDATETIME\b': 'DATETIME',
        r'\bSMALLDATETIME\b': 'DATETIME',
        r'\bDATE\b': 'DATE',
        r'\bTIME\b': 'TIME',
        r'\bTIMESTAMP\b': 'TIMESTAMP',

        # Tipos binarios
        r'\bVARBINARY\(MAX\)\b': 'LONGBLOB',
        r'\bVARBINARY\((\d+)\)': r'VARBINARY(\1)',
        r'\bBINARY\((\d+)\)': r'BINARY(\1)',
        r'\bIMAGE\b': 'LONGBLOB',

        # Tipos especiales
        r'\bUNIQUEIDENTIFIER\b': 'VARCHAR(36)',
        r'\bXML\b': 'TEXT',
    }

    # Funciones SQL Server -> MySQL
    FUNCTION_MAP = {
        r'\bGETDATE\(\)': 'NOW()',
        r'\bGETUTCDATE\(\)': 'UTC_TIMESTAMP()',
        r'\bSYSDATETIME\(\)': 'NOW()',
        r'\bISNULL\(': 'IFNULL(',
        r'\bLEN\(': 'LENGTH(',
        r'\bCONVERT\(': 'CAST(',
        r'\bCAST\(([^)]+)\s+AS\s+': r'CAST(\1 AS ',
    }

    def __init__(self, input_file: str, output_file: str = None):
        """
        Inicializar el conversor.

        Args:
            input_file: Ruta del archivo SQL Server
            output_file: Ruta del archivo MySQL de salida (opcional)
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else None

        if not self.output_file:
            # Generar nombre automáticamente
            self.output_file = self.input_file.parent / f"{self.input_file.stem}_mysql.sql"

    def convert(self) -> str:
        """
        Realizar la conversión completa.

        Returns:
            Contenido SQL convertido
        """
        print(f"Leyendo archivo: {self.input_file}")

        # Leer el archivo (manejar diferentes encodings)
        content = self._read_file()

        print(f"Tamano original: {len(content):,} caracteres")
        print(f"Convirtiendo SQL Server -> MySQL...")

        # Aplicar conversiones en orden
        content = self._remove_sql_server_specific(content)
        content = self._convert_data_types(content)
        content = self._convert_identity_to_auto_increment(content)
        content = self._convert_functions(content)
        content = self._convert_brackets_to_backticks(content)
        content = self._convert_go_statements(content)
        content = self._fix_constraints(content)
        content = self._add_mysql_header(content)

        print(f"Tamano convertido: {len(content):,} caracteres")
        print(f"Guardando en: {self.output_file}")

        # Guardar archivo
        self._write_file(content)

        print(f"Conversion completada exitosamente")

        return content

    def _read_file(self) -> str:
        """Leer archivo con manejo de diferentes encodings."""
        # Intentar diferentes encodings
        encodings = ['utf-16', 'utf-16-le', 'utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(self.input_file, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"   Archivo leido con encoding: {encoding}")
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"   Error con encoding {encoding}: {e}")
                continue

        # Último intento: leer como binario y decodificar
        with open(self.input_file, 'rb') as f:
            raw_content = f.read()
            # Intentar detectar BOM
            if raw_content.startswith(b'\xff\xfe'):
                content = raw_content.decode('utf-16-le')
            elif raw_content.startswith(b'\xfe\xff'):
                content = raw_content.decode('utf-16-be')
            else:
                content = raw_content.decode('utf-8', errors='ignore')

            print(f"   Archivo leido con auto-deteccion")
            return content

    def _write_file(self, content: str):
        """Guardar archivo convertido."""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _remove_sql_server_specific(self, content: str) -> str:
        """Eliminar comandos específicos de SQL Server."""
        print("   Eliminando comandos especificos de SQL Server...")

        # Patrones a eliminar
        patterns_to_remove = [
            r'USE\s+\[master\]\s*GO',
            r'ALTER\s+DATABASE\s+\[.*?\]\s+SET\s+.*?GO',
            r'IF\s+\(\s*1\s*=\s*FULLTEXTSERVICEPROPERTY.*?\).*?end\s*GO',
            r'EXEC\s+\[.*?\]\.\[.*?\]\.\[sp_fulltext_database\].*?GO',
            r'SET\s+ANSI_NULLS\s+(ON|OFF)\s*GO',
            r'SET\s+QUOTED_IDENTIFIER\s+(ON|OFF)\s*GO',
            r'SET\s+ANSI_PADDING\s+(ON|OFF)\s*GO',
            r'WITH\s+CATALOG_COLLATION\s+=\s+DATABASE_DEFAULT\s*,\s*LEDGER\s+=\s+OFF',
            r'CONTAINMENT\s+=\s+NONE',
            r'\(\s*NAME\s+=\s+N\'.*?\'\s*,\s*FILENAME\s+=.*?\)',
            r'ON\s+PRIMARY\s*\(.*?\)\s+LOG\s+ON\s*\(.*?\)',
        ]

        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)

        # Eliminar CREATE DATABASE con opciones complejas
        content = re.sub(
            r'CREATE\s+DATABASE\s+\[.*?\].*?(?=USE\s+\[|CREATE\s+TABLE|$)',
            '',
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        return content

    def _convert_data_types(self, content: str) -> str:
        """Convertir tipos de datos de SQL Server a MySQL."""
        print("   Convirtiendo tipos de datos...")

        for sql_server_type, mysql_type in self.DATA_TYPE_MAP.items():
            content = re.sub(sql_server_type, mysql_type, content, flags=re.IGNORECASE)

        return content

    def _convert_identity_to_auto_increment(self, content: str) -> str:
        """Convertir IDENTITY a AUTO_INCREMENT."""
        print("   Convirtiendo IDENTITY -> AUTO_INCREMENT...")

        # Patrón: [campo] [tipo] IDENTITY(1,1) NOT NULL
        content = re.sub(
            r'\bIDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)',
            'AUTO_INCREMENT',
            content,
            flags=re.IGNORECASE
        )

        return content

    def _convert_functions(self, content: str) -> str:
        """Convertir funciones de SQL Server a MySQL."""
        print("   Convirtiendo funciones...")

        for sql_server_func, mysql_func in self.FUNCTION_MAP.items():
            content = re.sub(sql_server_func, mysql_func, content, flags=re.IGNORECASE)

        return content

    def _convert_brackets_to_backticks(self, content: str) -> str:
        """Convertir [] de SQL Server a `` de MySQL."""
        print("   Convirtiendo brackets [] -> backticks ``...")

        # Reemplazar [nombre] con `nombre`
        content = re.sub(r'\[([^\]]+)\]', r'`\1`', content)

        return content

    def _convert_go_statements(self, content: str) -> str:
        """Convertir GO a delimitadores MySQL."""
        print("   Convirtiendo GO -> ;...")

        # GO es un separador de lotes en SQL Server
        # En MySQL usamos ; como delimitador
        content = re.sub(r'\bGO\b', ';', content, flags=re.IGNORECASE)

        # Limpiar múltiples ; seguidos
        content = re.sub(r';(\s*;)+', ';', content)

        return content

    def _fix_constraints(self, content: str) -> str:
        """Ajustar sintaxis de constraints para MySQL."""
        print("   Ajustando constraints...")

        # PRIMARY KEY CLUSTERED -> PRIMARY KEY
        content = re.sub(
            r'PRIMARY\s+KEY\s+CLUSTERED',
            'PRIMARY KEY',
            content,
            flags=re.IGNORECASE
        )

        # NONCLUSTERED INDEX -> INDEX
        content = re.sub(
            r'CREATE\s+NONCLUSTERED\s+INDEX',
            'CREATE INDEX',
            content,
            flags=re.IGNORECASE
        )

        # WITH (PAD_INDEX = OFF, ...) -> eliminar opciones
        content = re.sub(
            r'WITH\s*\([^)]*PAD_INDEX[^)]*\)',
            '',
            content,
            flags=re.IGNORECASE
        )

        # ON [PRIMARY] -> eliminar
        content = re.sub(
            r'ON\s+`PRIMARY`',
            '',
            content,
            flags=re.IGNORECASE
        )

        return content

    def _add_mysql_header(self, content: str) -> str:
        """Agregar header MySQL."""
        header = """-- ============================================================================
-- Script SQL convertido de SQL Server a MySQL
-- Herramienta: SQLServerToMySQLConverter
-- Fecha: {date}
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

"""
        from datetime import datetime
        header = header.format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        footer = """

-- ============================================================================
-- Fin del script
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;
"""

        return header + content + footer


def main():
    """Función principal."""
    print("=" * 80)
    print("CONVERSOR SQL SERVER -> MySQL")
    print("=" * 80)
    print()

    if len(sys.argv) < 2:
        print("ERROR: Debe especificar el archivo de entrada")
        print()
        print("Uso:")
        print(f"   python {sys.argv[0]} <archivo_entrada.sql> [archivo_salida.sql]")
        print()
        print("Ejemplo:")
        print(f"   python {sys.argv[0]} database/script.sql database/script_mysql.sql")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Verificar que el archivo existe
    if not Path(input_file).exists():
        print(f"ERROR: Archivo no encontrado: {input_file}")
        sys.exit(1)

    try:
        # Crear conversor y ejecutar
        converter = SQLServerToMySQLConverter(input_file, output_file)
        converter.convert()

        print()
        print("=" * 80)
        print("CONVERSION COMPLETADA")
        print("=" * 80)
        print()
        print(f"Archivo de salida: {converter.output_file}")
        print()
        print("IMPORTANTE:")
        print("   - Revisa el archivo generado antes de ejecutarlo")
        print("   - Algunos procedimientos almacenados pueden requerir ajustes manuales")
        print("   - Verifica indices y constraints")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR EN LA CONVERSION")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
