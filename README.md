# Gestor de Blog con Neo4j y Python

Aplicación de consola desarrollada en **Python** conectada a **Neo4j AuraDB** para administrar un sistema de blog basado en grafos.

## Modelo de Datos
* **Nodos:** `User`, `Article`, `Comment`, `Tag`, `Category`
* **Relaciones:** `WROTE`, `COMMENTED`, `HAS_COMMENT`, `TAGGED_WITH`, `IN_CATEGORY`

## Requisitos e Instalación
1. Tener instalado Python 3.10 o superior.
2. Instalar el controlador oficial de Neo4j:
   ```bash
   pip install neo4j