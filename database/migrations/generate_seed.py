"""
Script para generar el archivo SQL de seed data desde el código Python.
Genera 002_seed_knowledge_base.sql con todas las entradas actuales.
"""
import json
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent.knowledge import get_knowledge_base, KnowledgeCategory


def escape_sql_string(s: str) -> str:
    """Escapar comillas simples para SQL Server."""
    return s.replace("'", "''")


def generate_seed_sql():
    """Generar el archivo SQL de seed data."""

    knowledge_base = get_knowledge_base()

    sql_parts = []

    # Header
    sql_parts.append("""-- ============================================================================
-- Migración 002: Seed data de Knowledge Base
-- Fecha: 2025-11-29
-- Descripción: Carga las entradas iniciales de conocimiento desde el código
-- Base de datos: abcmasplus
-- ============================================================================

USE [abcmasplus];
GO

-- ============================================================================
-- 1. Insertar Categorías
-- ============================================================================

PRINT 'Insertando categorías...';

-- Limpiar datos existentes (opcional - comentar si quieres mantener datos)
-- DELETE FROM knowledge_entries;
-- DELETE FROM knowledge_categories;

SET IDENTITY_INSERT knowledge_categories ON;

""")

    # Categorías
    categories = {
        'PROCESOS': (1, '📋', 'Procesos y procedimientos internos'),
        'POLITICAS': (2, '📜', 'Políticas de la empresa'),
        'FAQS': (3, '❓', 'Preguntas frecuentes'),
        'CONTACTOS': (4, '📞', 'Información de contacto de departamentos'),
        'SISTEMAS': (5, '💻', 'Información sobre sistemas y herramientas'),
        'RECURSOS_HUMANOS': (6, '👥', 'Temas de RRHH: vacaciones, permisos, beneficios'),
        'BASE_DATOS': (7, '🗄️', 'Información sobre tablas y estructura de la base de datos')
    }

    for cat_name, (cat_id, icon, desc) in categories.items():
        display_name = KnowledgeCategory[cat_name].value.replace('_', ' ').title()
        sql_parts.append(f"""
INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES ({cat_id}, '{cat_name}', N'{display_name}', N'{escape_sql_string(desc)}', N'{icon}', 1);
""")

    sql_parts.append("""
SET IDENTITY_INSERT knowledge_categories OFF;

PRINT '  Categorías insertadas: 7';

-- ============================================================================
-- 2. Insertar Entradas de Conocimiento
-- ============================================================================

PRINT 'Insertando entradas de conocimiento...';

""")

    # Mapeo de categorías a IDs
    category_id_map = {cat: cat_id for cat, (cat_id, _, _) in categories.items()}

    # Entradas
    for idx, entry in enumerate(knowledge_base, 1):
        category_id = category_id_map[entry.category.name]
        question = escape_sql_string(entry.question)
        answer = escape_sql_string(entry.answer)
        keywords_json = json.dumps(entry.keywords, ensure_ascii=False)
        keywords_json_escaped = escape_sql_string(keywords_json)

        related_commands = entry.related_commands if entry.related_commands else []
        related_json = json.dumps(related_commands, ensure_ascii=False)
        related_json_escaped = escape_sql_string(related_json)

        priority = entry.priority

        sql_parts.append(f"""
-- Entrada {idx}: {entry.question[:50]}...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    {category_id},
    N'{question}',
    N'{answer}',
    N'{keywords_json_escaped}',
    N'{related_json_escaped}',
    {priority},
    1,
    'migration_001'
);
""")

    # Footer
    sql_parts.append(f"""
PRINT '  Entradas insertadas: {len(knowledge_base)}';

-- ============================================================================
-- 3. Verificación
-- ============================================================================

PRINT '';
PRINT 'Verificando datos insertados...';

SELECT
    c.display_name as Categoria,
    COUNT(e.id) as Total_Entradas,
    SUM(CASE WHEN e.priority = 3 THEN 1 ELSE 0 END) as Prioridad_Alta,
    SUM(CASE WHEN e.priority = 2 THEN 1 ELSE 0 END) as Prioridad_Media,
    SUM(CASE WHEN e.priority = 1 THEN 1 ELSE 0 END) as Prioridad_Normal
FROM knowledge_categories c
LEFT JOIN knowledge_entries e ON c.id = e.category_id
GROUP BY c.display_name
ORDER BY c.display_name;

PRINT '';
PRINT '============================================================================';
PRINT 'Migración 002 completada exitosamente';
PRINT '============================================================================';
PRINT 'Total de categorías: 7';
PRINT 'Total de entradas: {len(knowledge_base)}';
PRINT '';
PRINT 'Siguiente paso: Actualizar KnowledgeManager para leer desde BD';
PRINT '============================================================================';
GO
""")

    # Escribir archivo
    output_file = Path(__file__).parent / '002_seed_knowledge_base.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(sql_parts))

    print(f"[OK] Archivo generado: {output_file}")
    print(f"Total de entradas: {len(knowledge_base)}")
    print(f"Total de categorias: {len(categories)}")


if __name__ == '__main__':
    generate_seed_sql()
