# ============================================
# Loans API Tests
# ============================================

# --------------------------------------------
# Setup: Create user for loan tests
# --------------------------------------------
POST http://localhost:8000/users
Content-Type: application/json
{
  "name": "Loan Test User",
  "email": "loan.test@email.com"
}
HTTP 201
[Captures]
user_id: jsonpath "$.id"


# --------------------------------------------
# Setup: Create books for loan tests
# --------------------------------------------
POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Livro para Empréstimo 1",
  "author": "Autor Teste"
}
HTTP 201
[Captures]
book_id_1: jsonpath "$.id"

POST http://localhost:8000/books/{{book_id_1}}/copies
HTTP 201
[Captures]
copy_id_1: jsonpath "$.id"


POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Livro para Empréstimo 2",
  "author": "Autor Teste"
}
HTTP 201
[Captures]
book_id_2: jsonpath "$.id"

POST http://localhost:8000/books/{{book_id_2}}/copies
HTTP 201
[Captures]
copy_id_2: jsonpath "$.id"


POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Livro para Empréstimo 3",
  "author": "Autor Teste"
}
HTTP 201
[Captures]
book_id_3: jsonpath "$.id"

POST http://localhost:8000/books/{{book_id_3}}/copies
HTTP 201
[Captures]
copy_id_3: jsonpath "$.id"


POST http://localhost:8000/books
Content-Type: application/json
{
  "title": "Livro para Empréstimo 4",
  "author": "Autor Teste"
}
HTTP 201
[Captures]
book_id_4: jsonpath "$.id"

POST http://localhost:8000/books/{{book_id_4}}/copies
HTTP 201
[Captures]
copy_id_4: jsonpath "$.id"


# --------------------------------------------
# Create loan - success
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}},
  "book_id": {{book_id_1}}
}
HTTP 201
[Captures]
loan_id_1: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isInteger
jsonpath "$.user_id" == {{user_id}}
jsonpath "$.copy_id" == {{copy_id_1}}
jsonpath "$.returned_at" == null
jsonpath "$.fine_cents" == 0
jsonpath "$.due_to" isString


# --------------------------------------------
# Create loan - no copies available (book already loaned)
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}},
  "book_id": {{book_id_1}}
}
HTTP 409
[Asserts]
jsonpath "$.code" == "no_copies_available"
jsonpath "$.context.book_id" == {{book_id_1}}


# --------------------------------------------
# Create loan - second loan (same user)
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}},
  "book_id": {{book_id_2}}
}
HTTP 201
[Captures]
loan_id_2: jsonpath "$.id"


# --------------------------------------------
# Create loan - third loan (same user)
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}},
  "book_id": {{book_id_3}}
}
HTTP 201
[Captures]
loan_id_3: jsonpath "$.id"


# --------------------------------------------
# Create loan - fourth loan (exceeds max)
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}},
  "book_id": {{book_id_4}}
}
HTTP 409
[Asserts]
jsonpath "$.code" == "max_active_loans_exceeded"
jsonpath "$.context.user_id" == {{user_id}}
jsonpath "$.context.active" == 3


# --------------------------------------------
# Create loan - user not found
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": 99999,
  "book_id": {{book_id_4}}
}
HTTP 404
[Asserts]
jsonpath "$.code" == "user_not_found"


# --------------------------------------------
# Create loan - book not found
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}},
  "book_id": 99999
}
HTTP 404
[Asserts]
jsonpath "$.code" == "book_not_found"


# --------------------------------------------
# Create loan - missing user_id
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "book_id": {{book_id_4}}
}
HTTP 422


# --------------------------------------------
# Create loan - missing book_id
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}}
}
HTTP 422


# --------------------------------------------
# List active loans
# --------------------------------------------
GET http://localhost:8000/loans/active
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count >= 3


# --------------------------------------------
# List active loans - with pagination
# --------------------------------------------
GET http://localhost:8000/loans/active?offset=0&limit=2
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count <= 2


# --------------------------------------------
# List overdue loans (may be empty)
# --------------------------------------------
GET http://localhost:8000/loans/overdue
HTTP 200
[Asserts]
jsonpath "$" isCollection


# --------------------------------------------
# List user loans
# --------------------------------------------
GET http://localhost:8000/users/{{user_id}}/loans
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count == 3


# --------------------------------------------
# Return loan - success
# --------------------------------------------
POST http://localhost:8000/loans/{{loan_id_1}}/return
HTTP 200
[Asserts]
jsonpath "$.id" == {{loan_id_1}}
jsonpath "$.returned_at" isString
jsonpath "$.fine_cents" isInteger


# --------------------------------------------
# Return loan - already returned
# --------------------------------------------
POST http://localhost:8000/loans/{{loan_id_1}}/return
HTTP 409
[Asserts]
jsonpath "$.code" == "loan_already_returned"
jsonpath "$.context.loan_id" == {{loan_id_1}}


# --------------------------------------------
# Return loan - not found
# --------------------------------------------
POST http://localhost:8000/loans/99999/return
HTTP 404
[Asserts]
jsonpath "$.code" == "loan_not_found"


# --------------------------------------------
# After return: can loan same book again
# --------------------------------------------
POST http://localhost:8000/loans
Content-Type: application/json
{
  "user_id": {{user_id}},
  "book_id": {{book_id_1}}
}
HTTP 201
[Asserts]
jsonpath "$.copy_id" == {{copy_id_1}}


# --------------------------------------------
# List user loans - includes returned
# --------------------------------------------
GET http://localhost:8000/users/{{user_id}}/loans
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count == 4
