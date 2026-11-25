from flask import Flask, render_template, request, redirect, url_for, flash
from neo4j import GraphDatabase

app = Flask(__name__)
app.secret_key = "clave_secreta_blog_neo4j"

# Credenciales de Neo4j Aura
URI = "neo4j+ssc://0566f582.databases.neo4j.io"
USER = "0566f582"
PASSWORD = "5R8ek5LvTkd87y8kvGbeh4CKyEQIrPZ09sOgQXAsgTI"
DATABASE = "0566f582"


class BlogWebDB:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def obtener_articulos(self):
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
        ORDER BY a.date DESC
        """
        with self.driver.session(database=self.database) as session:
            return [dict(r) for r in session.run(query)]

    def crear_usuario(self, name, email):
        query = "MERGE (u:User {email: $email}) SET u.name = $name RETURN u"
        with self.driver.session(database=self.database) as session:
            session.run(query, name=name, email=email)

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
            return res is not None

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
            return res is not None

    def actualizar_articulo(self, title, nuevo_texto):
        query = """
        MATCH (a:Article {title: $title})
        SET a.text = $nuevo_texto
        RETURN a.title AS titulo
        """
        with self.driver.session(database=self.database) as session:
            res = session.run(query, title=title, nuevo_texto=nuevo_texto).single()
            return res is not None

    def eliminar_articulo(self, title):
        query = """
        MATCH (a:Article {title: $title})
        OPTIONAL MATCH (a)-[:HAS_COMMENT]->(c:Comment)
        DETACH DELETE a, c
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, title=title)


db = BlogWebDB(URI, USER, PASSWORD, DATABASE)


@app.route("/")
def index():
    try:
        articulos = db.obtener_articulos()
    except Exception as e:
        articulos = []
        flash(f"Error de conexión con Neo4j: {e}", "danger")
    return render_template("index.html", articulos=articulos)


@app.route("/usuario", methods=["POST"])
def registrar_usuario():
    db.crear_usuario(request.form["name"].strip(), request.form["email"].strip())
    flash("Usuario registrado exitosamente.", "success")
    return redirect(url_for("index"))


@app.route("/articulo", methods=["POST"])
def publicar_articulo():
    ok = db.crear_articulo(
        request.form["email"].strip(),
        request.form["title"].strip(),
        request.form["date"].strip(),
        request.form["text"].strip(),
        request.form["category"].strip(),
        request.form["tag"].strip()
    )
    if ok:
        flash("Artículo publicado correctamente.", "success")
    else:
        flash("Error: No existe un usuario registrado con ese correo.", "danger")
    return redirect(url_for("index"))


@app.route("/comentar", methods=["POST"])
def comentar():
    ok = db.agregar_comentario(
        request.form["email"].strip(),
        request.form["title"].strip(),
        request.form["comment"].strip(),
        request.form["url"].strip()
    )
    if ok:
        flash("Comentario agregado al artículo.", "success")
    else:
        flash("Error: Verifica que el correo exista.", "danger")
    return redirect(url_for("index"))


@app.route("/editar", methods=["POST"])
def editar():
    ok = db.actualizar_articulo(
        request.form["title"].strip(),
        request.form["nuevo_texto"].strip()
    )
    if ok:
        flash("Artículo actualizado.", "info")
    else:
        flash("No se encontró el artículo.", "danger")
    return redirect(url_for("index"))


@app.route("/eliminar", methods=["POST"])
def eliminar():
    db.eliminar_articulo(request.form["title"].strip())
    flash("Artículo eliminado del grafo.", "warning")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)