# ============================================
# Users API Tests
# ============================================

# --------------------------------------------
# Create user - success
# --------------------------------------------
POST http://localhost:8000/users
Content-Type: application/json
{
  "name": "Maria Santos",
  "email": "maria.santos@email.com"
}
HTTP 201
[Captures]
user_id: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isInteger
jsonpath "$.name" == "Maria Santos"
jsonpath "$.email" == "maria.santos@email.com"


# --------------------------------------------
# Create user - duplicate email
# --------------------------------------------
POST http://localhost:8000/users
Content-Type: application/json
{
  "name": "Maria Duplicada",
  "email": "maria.santos@email.com"
}
HTTP 409
[Asserts]
jsonpath "$.code" == "email_already_registered"
jsonpath "$.context.email" == "maria.santos@email.com"


# --------------------------------------------
# Create user - invalid email format
# --------------------------------------------
POST http://localhost:8000/users
Content-Type: application/json
{
  "name": "Invalid Email",
  "email": "not-an-email"
}
HTTP 422


# --------------------------------------------
# Create user - missing name
# --------------------------------------------
POST http://localhost:8000/users
Content-Type: application/json
{
  "email": "missing.name@email.com"
}
HTTP 422


# --------------------------------------------
# Create user - missing email
# --------------------------------------------
POST http://localhost:8000/users
Content-Type: application/json
{
  "name": "Missing Email"
}
HTTP 422


# --------------------------------------------
# Create user - empty body
# --------------------------------------------
POST http://localhost:8000/users
Content-Type: application/json
{}
HTTP 422


# --------------------------------------------
# Get user by ID - success
# --------------------------------------------
GET http://localhost:8000/users/{{user_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == {{user_id}}
jsonpath "$.name" == "Maria Santos"
jsonpath "$.email" == "maria.santos@email.com"


# --------------------------------------------
# Get user by ID - not found
# --------------------------------------------
GET http://localhost:8000/users/99999
HTTP 404
[Asserts]
jsonpath "$.code" == "user_not_found"
jsonpath "$.context.user_id" == 99999


# --------------------------------------------
# List users - default pagination
# --------------------------------------------
GET http://localhost:8000/users
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count >= 1


# --------------------------------------------
# List users - with pagination
# --------------------------------------------
GET http://localhost:8000/users?offset=0&limit=5
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count <= 5


# --------------------------------------------
# List users - offset beyond results
# --------------------------------------------
GET http://localhost:8000/users?offset=10000&limit=10
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count == 0


# --------------------------------------------
# Get user loans - empty (new user)
# --------------------------------------------
GET http://localhost:8000/users/{{user_id}}/loans
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$" count == 0


# --------------------------------------------
# Get user loans - user not found
# --------------------------------------------
GET http://localhost:8000/users/99999/loans
HTTP 404
[Asserts]
jsonpath "$.code" == "user_not_found"
