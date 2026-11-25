// 1. Limpiar la base de datos antes de inicializar
MATCH (n) DETACH DELETE n;

// 2. Restricciones de unicidad (Constraints)
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;

// 3. Creación de Nodos (Usuarios, Artículos, Etiquetas, Categorías y Comentarios)
CREATE (u1:User {name: "Ana Gómez", email: "ana@mail.com"}),
       (u2:User {name: "Carlos Ruiz", email: "carlos@mail.com"}),
       (a1:Article {
           title: "Introducción a Neo4j",
           date: "2026-11-24",
           text: "Las bases de datos de grafos permiten modelar relaciones complejas de forma natural."
       }),
       (t1:Tag {name: "Python", url: "/tags/python"}),
       (t2:Tag {name: "Grafos", url: "/tags/grafos"}),
       (cat1:Category {name: "Tecnología", url: "/cat/tecnologia"}),
       (com1:Comment {name: "Excelente post", url: "/comments/1"}),

// 4. Creación de Relaciones según el modelo (1-to-N y N-to-N)
       (u1)-[:WROTE]->(a1),
       (a1)-[:TAGGED_WITH]->(t1),
       (a1)-[:TAGGED_WITH]->(t2),
       (a1)-[:IN_CATEGORY]->(cat1),
       (u2)-[:COMMENTED]->(com1),
       (a1)-[:HAS_COMMENT]->(com1);

// 5. Consulta de verificación para visualizar el grafo completo
MATCH (n)-[r]->(m)
RETURN n, r, m;