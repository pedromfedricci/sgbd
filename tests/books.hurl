# ============================================
# Books API Tests
# ============================================

# --------------------------------------------
# Create book - success
# --------------------------------------------
POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Dom Casmurro",
  "author": "Machado de Assis"
}
HTTP 201
[Captures]
book_id_1: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isInteger
jsonpath "$.title" == "Dom Casmurro"
jsonpath "$.author" == "Machado de Assis"


# --------------------------------------------
# Create book - another book
# --------------------------------------------
POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Memórias Póstumas de Brás Cubas",
  "author": "Machado de Assis"
}
HTTP 201
[Captures]
book_id_2: jsonpath "$.id"
[Asserts]
jsonpath "$.title" == "Memórias Póstumas de Brás Cubas"


# --------------------------------------------
# Create book - same title different author (allowed)
# --------------------------------------------
POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Dom Casmurro",
  "author": "Outro Autor"
}
HTTP 201


# --------------------------------------------
# Create book - missing title
# --------------------------------------------
POST http://localhost:8000/books
Content-Type: application/json
{
  "author": "Autor Sem Titulo"
}
HTTP 422


# --------------------------------------------
# Create book - missing author
# --------------------------------------------
POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Livro Sem Autor"
}
HTTP 422


# --------------------------------------------
# Create book - empty body
# --------------------------------------------
POST http://localhost:8000/books
Content-Type: application/json
{}
HTTP 422


# --------------------------------------------
# Get first book by ID - success
# --------------------------------------------
GET http://localhost:8000/books/{{book_id_1}}
HTTP 200
[Asserts]
jsonpath "$.id" == {{book_id_1}}
jsonpath "$.title" == "Dom Casmurro"
jsonpath "$.author" == "Machado de Assis"

# --------------------------------------------
# Get second book by ID - success
# --------------------------------------------
GET http://localhost:8000/books/{{book_id_2}}
HTTP 200
[Asserts]
jsonpath "$.id" == {{book_id_2}}
jsonpath "$.title" == "Memórias Póstumas de Brás Cubas"
jsonpath "$.author" == "Machado de Assis"

# --------------------------------------------
# Get book by ID - not found
# --------------------------------------------
GET http://localhost:8000/books/99999
HTTP 404
[Asserts]
jsonpath "$.code" == "book_not_found"
jsonpath "$.context.book_id" == 99999


# --------------------------------------------
# List books - default pagination
# --------------------------------------------
GET http://localhost:8000/books
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count >= 1


# --------------------------------------------
# List books - with pagination
# --------------------------------------------
GET http://localhost:8000/books?offset=0&limit=2
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count <= 2


# --------------------------------------------
# List books - offset beyond results
# --------------------------------------------
GET http://localhost:8000/books?offset=10000&limit=10
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count == 0
