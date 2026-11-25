from neo4j import GraphDatabase

class BlogApp:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    # 1. CREAR USUARIO (1-to-N con Articles y Comments)
    def crear_usuario(self, name, email):
        query = "MERGE (u:User {email: $email}) SET u.name = $name RETURN u"
        with self.driver.session(database=self.database) as session:
            session.run(query, name=name, email=email)
            print(f"✅ Usuario '{name}' ({email}) registrado.")

    # 2. PUBLICAR ARTÍCULO (Conecta con User, Category y Tag)
    def crear_articulo(self, email_autor, title, date, text, category_name, tag_name):
        query = """
        MATCH (u:User {email: $email})
        MERGE (c:Category {name: $cat_name})
        ON CREATE SET c.url = '/cat/' + toLower(replace($cat_name, ' ', '-'))
        MERGE (t:Tag {name: $tag_name})
        ON CREATE SET t.url = '/tags/' + toLower(replace($tag_name, ' ', '-'))
        CREATE (a:Article {title: $title, date: $date, text: $text})
        CREATE (u)-[:WROTE]->(a)
        CREATE (a)-[:IN_CATEGORY]->(c)
        CREATE (a)-[:TAGGED_WITH]->(t)
        RETURN a.title AS titulo
        """
        with self.driver.session(database=self.database) as session:
            res = session.run(query, email=email_autor, title=title, date=date,
                              text=text, cat_name=category_name, tag_name=tag_name).single()
            if res:
                print(f"✅ Artículo '{res['titulo']}' publicado exitosamente.")
            else:
                print("❌ Error: No se encontró un usuario con ese email.")

    # 3. AGREGAR COMENTARIO (Conecta con User y Article)
    def agregar_comentario(self, email_usuario, article_title, comment_name, url):
        query = """
        MATCH (u:User {email: $email})
        MATCH (a:Article {title: $title})
        CREATE (com:Comment {name: $com_name, url: $url})
        CREATE (u)-[:COMMENTED]->(com)
        CREATE (a)-[:HAS_COMMENT]->(com)
        RETURN com.name AS comentario
        """
        with self.driver.session(database=self.database) as session:
            res = session.run(query, email=email_usuario, title=article_title,
                              com_name=comment_name, url=url).single()
            if res:
                print("✅ Comentario agregado al artículo.")
            else:
                print("❌ Error: Verifica que el email del usuario y el título del artículo existan.")

    # 4. LEER ARTÍCULOS Y SUS RELACIONES
    def listar_articulos(self):
        query = """
        MATCH (u:User)-[:WROTE]->(a:Article)
        OPTIONAL MATCH (a)-[:IN_CATEGORY]->(c:Category)
        OPTIONAL MATCH (a)-[:TAGGED_WITH]->(t:Tag)
        OPTIONAL MATCH (a)-[:HAS_COMMENT]->(com:Comment)
        RETURN a.title AS Titulo, a.date AS Fecha, a.text AS Texto,
               u.name AS Autor,
               collect(DISTINCT c.name) AS Categorias,
               collect(DISTINCT t.name) AS Tags,
               collect(DISTINCT com.name) AS Comentarios
        """
        with self.driver.session(database=self.database) as session:
            resultados = session.run(query)
            print("\n" + "="*45)
            print("           ARTÍCULOS DEL BLOG")
            print("="*45)
            hay_datos = False
            for r in resultados:
                hay_datos = True
                print(f"Título:      {r['Titulo']} ({r['Fecha']})")
                print(f"Autor:       {r['Autor']}")
                print(f"Contenido:   {r['Texto']}")
                print(f"Categorías:  {', '.join(r['Categorias']) or 'Ninguna'}")
                print(f"Etiquetas:   {', '.join(r['Tags']) or 'Ninguna'}")
                print(f"Comentarios: {', '.join(r['Comentarios']) or 'Sin comentarios'}")
                print("-" * 45)
            if not hay_datos:
                print("No hay artículos registrados todavía.")

    # 5. ACTUALIZAR ARTÍCULO
    def actualizar_articulo(self, title, nuevo_texto):
        query = """
        MATCH (a:Article {title: $title})
        SET a.text = $nuevo_texto
        RETURN a.title AS titulo
        """
        with self.driver.session(database=self.database) as session:
            res = session.run(query, title=title, nuevo_texto=nuevo_texto).single()
            if res:
                print(f"✅ Texto del artículo '{res['titulo']}' actualizado.")
            else:
                print("❌ No se encontró ningún artículo con ese título.")

    # 6. ELIMINAR ARTÍCULO (Junto con sus comentarios)
    def eliminar_articulo(self, title):
        query = """
        MATCH (a:Article {title: $title})
        OPTIONAL MATCH (a)-[:HAS_COMMENT]->(c:Comment)
        DETACH DELETE a, c
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, title=title)
            print(f"✅ Artículo '{title}' y sus comentarios fueron eliminados.")

if __name__ == "__main__":
    URI = "neo4j+ssc://0566f582.databases.neo4j.io"
    USER = "0566f582"
    PASSWORD = "5R8ek5LvTkd87y8kvGbeh4CKyEQIrPZ09sOgQXAsgTI"
    DATABASE = "0566f582"

    app = BlogApp(URI, USER, PASSWORD, DATABASE)

    try:
        while True:
            print("\n=== GESTOR DE BLOG EN NEO4J ===")
            print("1. Registrar Usuario")
            print("2. Publicar Artículo")
            print("3. Comentar Artículo")
            print("4. Ver Artículos")
            print("5. Actualizar Texto de Artículo")
            print("6. Eliminar Artículo")
            print("7. Salir")
            opcion = input("Selecciona una opción: ")

            if opcion == "1":
                app.crear_usuario(input("Nombre: "), input("Email: "))
            elif opcion == "2":
                app.crear_articulo(
                    input("Email del autor: "),
                    input("Título: "),
                    input("Fecha (YYYY-MM-DD): "),
                    input("Texto del artículo: "),
                    input("Categoría: "),
                    input("Etiqueta (Tag): ")
                )
            elif opcion == "3":
                app.agregar_comentario(
                    input("Email del usuario que comenta: "),
                    input("Título del artículo: "),
                    input("Comentario: "),
                    input("URL del comentario (ej. /comments/2): ")
                )
            elif opcion == "4":
                app.listar_articulos()
            elif opcion == "5":
                app.actualizar_articulo(
                    input("Título del artículo a editar: "),
                    input("Nuevo texto: ")
                )
            elif opcion == "6":
                app.eliminar_articulo(input("Título del artículo a eliminar: "))
            elif opcion == "7":
                print("Cerrando conexión...")
                break
            else:
                print("Opción no válida.")
    finally:
        app.close()