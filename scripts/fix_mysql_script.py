"""
Post-procesador para scripts MySQL convertidos.

Arregla problemas comunes después de la conversión:
- Agrega CREATE DATABASE IF NOT EXISTS
- Elimina backticks dobles
- Limpia prefijos de esquema (dbo.)
- Arregla tipos de datos que no se convirtieron bien

Uso:
    python scripts/fix_mysql_script.py <archivo.sql>
"""
import re
import sys
from pathlib import Path


def fix_mysql_script(input_file: str):
    """
    Arreglar script MySQL.

    Args:
        input_file: Ruta del archivo SQL a arreglar
    """
    input_path = Path(input_file)
    print(f"Leyendo: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Tamano original: {len(content):,} caracteres")
    print("Aplicando correcciones...")

    # 1. Agregar CREATE DATABASE antes del USE
    print("  - Agregando CREATE DATABASE IF NOT EXISTS")
    content = re.sub(
        r'(SET time_zone = "\+00:00";)\s*\n\s*\n\s*/\*\*\*\*\*\* Object:  Database.*?\*\*\*\*\*\*/\s*\n\s*USE `(\w+)`',
        r'\1\n\n-- Crear base de datos si no existe\nCREATE DATABASE IF NOT EXISTS `\2`\n  CHARACTER SET utf8mb4\n  COLLATE utf8mb4_unicode_ci;\n\nUSE `\2`',
        content,
        flags=re.DOTALL
    )

    # 2. Eliminar backticks dobles en definiciones de columnas
    print("  - Eliminando backticks dobles")
    # Patrón: `nombre` `tipo` -> `nombre` tipo
    content = re.sub(r'`(\w+)` `(\w+)`', r'`\1` \2', content)

    # 3. Eliminar prefijo dbo. de nombres de tablas
    print("  - Eliminando prefijo dbo.")
    content = re.sub(r'`dbo`\.`(\w+)`', r'`\1`', content)
    content = re.sub(r'dbo\.(\w+)', r'\1', content)

    # 4. Arreglar DATETIME(7) -> DATETIME
    print("  - Corrigiendo DATETIME(7) -> DATETIME")
    content = re.sub(r'DATETIME\(\d+\)', 'DATETIME', content)

    # 5. Arreglar nvarchar -> VARCHAR
    print("  - Corrigiendo nvarchar -> VARCHAR")
    content = re.sub(r'`nvarchar`', 'VARCHAR', content, flags=re.IGNORECASE)
    content = re.sub(r'\bnvarchar\b', 'VARCHAR', content, flags=re.IGNORECASE)

    # 6. Arreglar varchar -> VARCHAR (normalizar)
    print("  - Normalizando varchar -> VARCHAR")
    content = re.sub(r'`varchar`', 'VARCHAR', content, flags=re.IGNORECASE)

    # 7. Arreglar VARCHAR(max) -> TEXT
    print("  - Corrigiendo VARCHAR(max) -> TEXT")
    content = re.sub(r'VARCHAR\(max\)', 'TEXT', content, flags=re.IGNORECASE)

    # 8. Arreglar INT, BIGINT, etc (quitar backticks)
    print("  - Normalizando tipos de datos")
    # Primero TINYINT(1) específicamente
    content = re.sub(r'`TINYINT\(1\)`', 'TINYINT(1)', content, flags=re.IGNORECASE)

    # Luego otros tipos
    data_types = ['INT', 'BIGINT', 'SMALLINT', 'TINYINT', 'DECIMAL', 'FLOAT',
                  'DOUBLE', 'DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'TEXT',
                  'LONGTEXT', 'MEDIUMTEXT', 'BLOB', 'LONGBLOB']
    for dtype in data_types:
        content = re.sub(f'`{dtype}`', dtype, content, flags=re.IGNORECASE)

    # 9. Eliminar "TEXTIMAGE_" y similares (artefactos de SQL Server)
    print("  - Eliminando artefactos de SQL Server")
    content = re.sub(r'\s+TEXTIMAGE_\s*;', ';', content)
    content = re.sub(r'\s+ON `PRIMARY`\s*', ' ', content)

    # 10. Arreglar ENGINE y opciones de tabla
    print("  - Agregando ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")
    content = re.sub(
        r'\)\s*;(\s*/\*\*\*\*\*\*)',
        r') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\1',
        content
    )

    # 11. Limpiar múltiples líneas en blanco
    print("  - Limpiando formato")
    content = re.sub(r'\n{3,}', '\n\n', content)

    # 12. Arreglar ASC en índices (MySQL no lo necesita explícitamente)
    content = re.sub(r'ASC\s*\)', ')', content)

    # 13. Arreglar varchar sin backticks
    content = re.sub(r'\bvarchar\(', 'VARCHAR(', content, flags=re.IGNORECASE)

    # 14. Eliminar backslashes de escape innecesarios
    print("  - Eliminando backslashes innecesarios")
    content = content.replace(r'TINYINT\(1\)', 'TINYINT(1)')

    # 15. Eliminar SET IDENTITY_INSERT (específico de SQL Server)
    print("  - Eliminando SET IDENTITY_INSERT")
    content = re.sub(r'SET IDENTITY_INSERT `\w+` (ON|OFF)\s*', '', content, flags=re.IGNORECASE)

    # 16. Convertir CAST(N'...' AS DATETIME) a formato MySQL
    print("  - Convirtiendo CAST a formato MySQL")
    content = re.sub(
        r"CAST\(N'([^']+)'\s+AS\s+DATETIME\)",
        r"'\1'",
        content,
        flags=re.IGNORECASE
    )

    # 17. Separar INSERT statements que están juntos
    print("  - Separando INSERT statements")
    content = re.sub(r'\)\s+INSERT\s+', ');\nINSERT ', content, flags=re.IGNORECASE)

    # 18. Agregar ; al final de INSERTs que no lo tienen
    print("  - Agregando ; faltantes en INSERTs")
    # Buscar INSERT ... VALUES (...) sin ; antes del salto de línea
    content = re.sub(
        r'(INSERT\s+`?\w+`?\s+\([^)]+\)\s+VALUES\s+\([^)]+\))(\s*\n)',
        r'\1;\2',
        content,
        flags=re.IGNORECASE
    )

    # 19. Agregar DROP TABLE IF EXISTS antes de cada CREATE TABLE
    print("  - Agregando DROP TABLE IF EXISTS")
    content = re.sub(
        r'(CREATE TABLE\s+`(\w+)`)',
        r'DROP TABLE IF EXISTS `\2`;\n\1',
        content,
        flags=re.IGNORECASE
    )

    # 20. Agregar DROP VIEW IF EXISTS antes de cada CREATE VIEW
    print("  - Agregando DROP VIEW IF EXISTS")
    content = re.sub(
        r'(CREATE VIEW\s+`(\w+)`)',
        r'DROP VIEW IF EXISTS `\2`;\n\1',
        content,
        flags=re.IGNORECASE
    )

    # 21. Arreglar ALTER TABLE - eliminar ENGINE/CHARSET
    print("  - Corrigiendo ALTER TABLE statements")
    content = re.sub(
        r'(ALTER TABLE[^;]+)\s+ENGINE=InnoDB[^;]*',
        r'\1',
        content,
        flags=re.IGNORECASE
    )

    # 22. Arreglar NONCLUSTERED en índices
    print("  - Eliminando NONCLUSTERED de índices")
    content = re.sub(r'\bNONCLUSTERED\b', '', content, flags=re.IGNORECASE)

    # 23. Arreglar espacios en ADD CONSTRAINT
    print("  - Corrigiendo ADD CONSTRAINT")
    content = re.sub(r'\bADD\s*CONSTRAINT\b', 'ADD CONSTRAINT', content, flags=re.IGNORECASE)

    # 24. Eliminar ENGINE/CHARSET de CREATE INDEX
    print("  - Corrigiendo CREATE INDEX statements")
    content = re.sub(
        r'(CREATE\s+(?:UNIQUE\s+)?INDEX[^;]+)\s+ENGINE=InnoDB[^;]*',
        r'\1',
        content,
        flags=re.IGNORECASE
    )

    # 25. Eliminar cláusulas WHERE de índices filtrados (no soportado en MySQL)
    print("  - Eliminando WHERE de indices filtrados")
    content = re.sub(
        r'(CREATE\s+(?:UNIQUE\s+)?INDEX\s+`\w+`\s+ON\s+`\w+`\s*\([^)]+\))\s*WHERE\s*\([^)]+\)',
        r'\1',
        content,
        flags=re.IGNORECASE
    )

    # 26. Limpiar paréntesis dobles en CREATE INDEX
    print("  - Limpiando parentesis dobles")
    content = re.sub(r'\)\s*\)\s*;', r');', content)

    print(f"Tamano final: {len(content):,} caracteres")

    # Guardar archivo
    output_path = input_path.parent / f"{input_path.stem}_fixed.sql"
    print(f"Guardando en: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Listo!")
    return output_path


def main():
    """Función principal."""
    print("=" * 80)
    print("POST-PROCESADOR MYSQL")
    print("=" * 80)
    print()

    if len(sys.argv) < 2:
        print("ERROR: Debe especificar el archivo SQL")
        print()
        print("Uso:")
        print(f"   python {sys.argv[0]} <archivo.sql>")
        print()
        print("Ejemplo:")
        print(f"   python {sys.argv[0]} database/ChatBot_mysql.sql")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"ERROR: Archivo no encontrado: {input_file}")
        sys.exit(1)

    try:
        output_file = fix_mysql_script(input_file)

        print()
        print("=" * 80)
        print("CORRECCION COMPLETADA")
        print("=" * 80)
        print()
        print(f"Archivo corregido: {output_file}")
        print()
        print("Ahora puedes ejecutar el archivo en MySQL:")
        print(f"   mysql -u root -p < {output_file}")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
