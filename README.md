# Expense Tracker API

A production-oriented REST API for managing personal expenses, built with **FastAPI, PostgreSQL, raw SQL, psycopg, JWT authentication, pytest, Alembic, Docker, and Docker Compose**.

The project was deliberately built without an ORM. Database interaction uses SQL directly through `psycopg`, making the project useful not only as an expense tracker but also as a practical exploration of backend engineering fundamentals: relational database design, SQL, transactions, authentication, authorization, connection pooling, migrations, testing, configuration, containerization, and deployment.

---

## Table of Contents

- [Overview](#overview)
- [What This Project Demonstrates](#what-this-project-demonstrates)
- [Architecture](#architecture)
- [Request Flow](#request-flow)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [Database Relationships](#database-relationships)
- [Authentication and Authorization](#authentication-and-authorization)
- [API Endpoints](#api-endpoints)
- [Validation and Error Handling](#validation-and-error-handling)
- [Service and Repository Layers](#service-and-repository-layers)
- [Transactions](#transactions)
- [PostgreSQL Connection Pooling](#postgresql-connection-pooling)
- [Configuration and Environment Variables](#configuration-and-environment-variables)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Docker](#docker)
- [Docker Compose](#docker-compose)
- [Health and Readiness Checks](#health-and-readiness-checks)
- [Deployment Flow](#deployment-flow)
- [Running Locally](#running-locally)
- [Running with Docker Compose](#running-with-docker-compose)
- [Running Tests](#running-tests)
- [Useful Commands](#useful-commands)
- [Engineering Decisions](#engineering-decisions)
- [Future Improvements](#future-improvements)

---

## Overview

Expense Tracker is a REST API that allows authenticated users to:

- Create an account
- Log in
- Create expense categories
- Record expenses
- View their expenses
- View an individual expense
- Edit expenses
- Delete expenses
- Filter expenses by category
- Calculate total spending
- Enforce ownership of user data

The API also includes role-based authorization, with `USER` and `ADMIN` roles.

The project evolved from a simple CRUD API into a more structured backend system.

The final architecture follows:

```text
HTTP Request
     │
     ▼
┌─────────────┐
│   Router    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Service   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Repository  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │
└─────────────┘
```

The goal is not merely to make endpoints work, but to separate HTTP concerns, business logic, data access, and persistence.

---

# What This Project Demonstrates

This project covers a broad set of backend engineering concepts.

### API development

- FastAPI
- RESTful endpoints
- Request validation
- Response schemas
- HTTP status codes
- Dependency injection
- API versioning

### Database engineering

- PostgreSQL
- Raw SQL
- Foreign keys
- Constraints
- Unique indexes
- `ON DELETE CASCADE`
- `ON DELETE RESTRICT`
- Transactions
- UUID primary keys
- `NUMERIC`
- `DATE`
- `TIMESTAMPTZ`
- Connection pooling

### Application architecture

- Router layer
- Service layer
- Repository layer
- Dependency layer
- Schema layer
- Configuration layer

### Security

- Password hashing
- JWT authentication
- Role-based authorization
- Resource ownership
- Environment-based secrets
- CORS configuration
- Safe handling of unexpected errors

### Testing

- pytest
- FastAPI `TestClient`
- Isolated PostgreSQL test database
- Dependency overrides
- Authentication fixtures
- Ownership tests
- Admin authorization tests

### Production concerns

- Environment configuration
- Database migrations
- Structured logging
- Health checks
- Readiness checks
- PostgreSQL connection pooling
- Docker
- Docker Compose
- Reproducible application builds

---

# Architecture

The application is organized around a layered architecture.

```mermaid
flowchart TD
    Client["Client / Browser / Mobile App"]
    Router["FastAPI Router"]
    Schema["Pydantic Schema"]
    Service["Service Layer"]
    Repository["Repository Layer"]
    Pool["PostgreSQL Connection Pool"]
    DB[("PostgreSQL")]

    Client --> Router
    Router --> Schema
    Router --> Service
    Service --> Repository
    Repository --> Pool
    Pool --> DB
```

Each layer has a specific responsibility.

### Router

The router handles HTTP-specific concerns.

Examples:

- URL paths
- HTTP methods
- request parameters
- authentication dependencies
- response status codes

A router should not contain large amounts of business logic or SQL.

### Schema

Pydantic schemas define the shape and validation rules of API data.

For example:

```text
ExpenseCreate
    name
    description
    amount
    date
    category_id
```

Validation happens before the request reaches the service layer.

### Service

The service layer contains business logic.

Examples:

- checking whether a category exists
- enforcing business rules
- coordinating multiple repository operations
- committing transactions
- translating expected database errors into API errors

### Repository

The repository layer is responsible for database access.

This project intentionally uses raw SQL rather than an ORM.

For example:

```sql
SELECT
    id,
    name,
    description,
    amount,
    date,
    created_at,
    user_id,
    category_id
FROM expenses
WHERE user_id = %s
ORDER BY date DESC;
```

The repository knows SQL.

It does not know about HTTP status codes or FastAPI routes.

### PostgreSQL

PostgreSQL is responsible for persistent relational data, constraints, referential integrity, and transactional consistency.

---

# Request Flow

A typical authenticated request looks like this:

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Router
    participant A as Auth Dependency
    participant S as Service
    participant Repo as Repository
    participant DB as PostgreSQL

    C->>R: GET /api/v1/expenses
    R->>A: Validate JWT
    A->>R: Current user ID
    R->>S: Request expenses
    S->>Repo: Get expenses(user_id)
    Repo->>DB: SELECT ... WHERE user_id = ?
    DB-->>Repo: Rows
    Repo-->>S: Expense records
    S-->>R: Result
    R-->>C: JSON response
```

This separation means that changing how data is stored does not require rewriting the HTTP layer.

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Application language |
| FastAPI | REST API framework |
| Pydantic | Request/response validation |
| pydantic-settings | Environment configuration |
| PostgreSQL 16 | Relational database |
| psycopg 3 | PostgreSQL driver |
| psycopg-pool | Database connection pooling |
| PyJWT | JWT authentication |
| pwdlib + Argon2 | Password hashing |
| Alembic | Database migrations |
| pytest | Automated testing |
| Docker | Application containerization |
| Docker Compose | Container orchestration |
| Uvicorn | ASGI server |

---

# Project Structure

```text
expense-tracker/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── security.py
│   ├── dependencies.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── expenses.py
│   │   └── categories.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── expenses.py
│   │   ├── categories.py
│   │   └── auth.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── expenses.py
│   │   ├── categories.py
│   │   └── auth.py
│   │
│   └── repositories/
│       ├── __init__.py
│       ├── users.py
│       ├── expenses.py
│       ├── categories.py
│       └── auth.py
│
├── migrations/
│   ├── env.py
│   └── versions/
│       └── c2543da804ac_create_initial_database_schema.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_categories.py
│   └── test_expenses.py
│
├── Dockerfile
├── .dockerignore
├── compose.yaml
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# Database Design

The database contains three primary tables:

```mermaid
erDiagram
    USERS ||--o{ EXPENSES : creates
    USERS ||--o{ CATEGORIES : creates
    CATEGORIES ||--o{ EXPENSES : classifies

    USERS {
        UUID id PK
        TEXT email UK
        TEXT password_hash
        TEXT role
        TIMESTAMPTZ created_at
    }

    CATEGORIES {
        UUID id PK
        TEXT name
        UUID creator FK
        TIMESTAMPTZ created_at
    }

    EXPENSES {
        UUID id PK
        TEXT name
        TEXT description
        NUMERIC amount
        DATE date
        TIMESTAMPTZ created_at
        UUID user_id FK
        UUID category_id FK
    }
```

## Users

```text
users
```

Stores authentication and account information.

Important constraints:

```sql
id UUID PRIMARY KEY
email TEXT NOT NULL UNIQUE
password_hash TEXT NOT NULL
role TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

The role is restricted to:

```text
USER
ADMIN
```

Passwords are never stored as plaintext.

Only password hashes are persisted.

---

## Categories

```text
categories
```

Categories are shared across the application but have a creator.

```sql
creator UUID NOT NULL REFERENCES users(id)
```

Category names are protected by a case-insensitive, whitespace-normalized unique index:

```sql
CREATE UNIQUE INDEX categories_name_unique
ON categories (LOWER(TRIM(name)));
```

This prevents situations such as:

```text
Food
food
  Food
FOOD
```

being treated as different categories.

---

## Expenses

```text
expenses
```

Each expense belongs to both a user and a category.

```sql
user_id UUID NOT NULL
    REFERENCES users(id)
    ON DELETE CASCADE

category_id UUID NOT NULL
    REFERENCES categories(id)
    ON DELETE RESTRICT
```

This creates two different deletion behaviours.

### User deletion

Deleting a user deletes that user's expenses:

```text
User
 └── Expenses
       ↓
    CASCADE
```

### Category deletion

A category cannot be deleted while expenses still reference it:

```text
Category
   ↑
Expenses
   │
   └── RESTRICT
```

This prevents orphaned expense records.

---

# Database Relationships

The relationships can be summarized as:

```text
USER
 │
 ├─────────────── creates ───────────────► CATEGORY
 │
 └─────────────── owns ──────────────────► EXPENSE
                                             │
                                             │ belongs to
                                             ▼
                                          CATEGORY
```

An expense therefore has two important ownership/classification relationships:

```text
Expense
 ├── belongs to User
 └── belongs to Category
```

The API also enforces user ownership at the query level.

For example, retrieving an expense does not simply query:

```sql
WHERE id = %s
```

It also considers the authenticated user:

```sql
WHERE id = %s
AND user_id = %s
```

This prevents one authenticated user from accessing another user's expense simply by knowing its UUID.

---

# Authentication and Authorization

Authentication answers:

> Who are you?

Authorization answers:

> What are you allowed to do?

The application uses JWT-based authentication.

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant DB as PostgreSQL

    U->>API: POST /api/v1/auth/login
    API->>DB: Find user by email
    DB-->>API: User + password hash
    API->>API: Verify password
    API->>API: Create JWT
    API-->>U: Access token

    U->>API: Authenticated request + Bearer token
    API->>API: Decode JWT
    API->>API: Extract user ID / role
    API-->>U: Protected resource
```

JWTs contain authentication information such as the user's identity and expiration.

The configured token lifetime is:

```text
30 minutes
```

Passwords are hashed using `pwdlib` with Argon2.

The application never stores or compares plaintext passwords.

---

# Role-Based Authorization

The application currently supports:

```text
USER
ADMIN
```

A normal user cannot access admin-only functionality.

For example:

```text
GET /api/v1/users
```

requires the `ADMIN` role.

The authorization flow is:

```text
JWT
 │
 ▼
Current User
 │
 ▼
Role Check
 │
 ├── USER  ──► 403 Forbidden
 │
 └── ADMIN ──► Continue
```

---

# API Endpoints

All versioned endpoints are under:

```text
/api/v1
```

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Authenticate a user and receive a JWT |

## Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/users` | Create an account |
| GET | `/api/v1/users` | List users; admin only |

## Categories

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/categories` | Create a category |
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/categories/{id}` | Get a category |
| PUT | `/api/v1/categories/{id}` | Update a category |
| DELETE | `/api/v1/categories/{id}` | Delete a category |

## Expenses

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/expenses` | Create an expense |
| GET | `/api/v1/expenses` | List expenses |
| GET | `/api/v1/expenses/{id}` | Get one expense |
| PUT | `/api/v1/expenses/{id}` | Update an expense |
| DELETE | `/api/v1/expenses/{id}` | Delete an expense |
| GET | `/api/v1/expenses/total` | Calculate total spending |

The expense listing supports category filtering.

For example:

```text
GET /api/v1/expenses?category_id=<UUID>
```

---

# Health Endpoints

Two operational endpoints are intentionally outside `/api/v1`.

```text
GET /health
GET /ready
```

### `/health`

Checks whether the application process is alive.

```json
{
  "status": "ok"
}
```

### `/ready`

Checks whether the application can communicate with PostgreSQL.

```json
{
  "status": "ready"
}
```

This distinction matters in production.

A server can be alive while its database connection is unavailable.

```text
/health
   │
   └── Is the application alive?

/ready
   │
   └── Is the application capable of serving requests?
          │
          └── Can it reach PostgreSQL?
```

---

# Validation and Error Handling

Input validation is handled using Pydantic schemas.

Examples include:

### Email

Must be a valid email address.

### Password

Minimum length:

```text
8 characters
```

### Expense name

```text
1–100 characters
```

### Description

Maximum:

```text
500 characters
```

### Amount

Must be greater than zero.

The database also independently enforces:

```sql
CHECK (amount > 0)
```

This is deliberate.

Application validation provides useful API feedback, while database constraints protect the data even if another application or SQL client writes to the database.

---

# Error Handling

Expected errors are translated into appropriate HTTP responses.

Examples:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
```

Unexpected exceptions are handled globally.

Instead of exposing internal details to clients, the API returns:

```json
{
  "detail": "Internal server error"
}
```

while logging the actual exception internally.

This creates a separation between:

```text
Client
  ↓
Safe API error

Server logs
  ↓
Detailed diagnostic information
```

---

# Service and Repository Layers

One of the major architectural decisions in this project was separating business logic from database access.

Without separation, an endpoint can quickly become:

```text
Route
 ├── validate request
 ├── authenticate user
 ├── write SQL
 ├── handle database errors
 ├── apply business rules
 ├── commit transaction
 └── construct response
```

That becomes difficult to maintain.

Instead:

```text
Router
   │
   ▼
Service
   │
   ▼
Repository
```

### Router

Handles HTTP.

### Service

Handles business rules and transaction boundaries.

### Repository

Handles SQL.

For example:

```text
POST /expenses
      │
      ▼
expenses router
      │
      ▼
expense service
      │
      ▼
expense repository
      │
      ▼
INSERT INTO expenses ...
```

The repository does not commit the transaction.

The service controls the transaction.

This keeps transaction boundaries at the business-operation level.

---

# Transactions

Database operations that belong together are handled transactionally.

The general pattern is:

```text
BEGIN
   │
   ├── database operation
   │
   ├── database operation
   │
   └── ...
   │
   ├── success → COMMIT
   │
   └── failure → ROLLBACK
```

Repositories therefore focus on data access rather than deciding when a transaction should be committed.

---

# PostgreSQL Connection Pooling

The application uses `psycopg_pool.ConnectionPool`.

Instead of opening a new PostgreSQL connection for every request, the application maintains a pool of reusable connections.

Current configuration:

```text
Minimum connections: 2
Maximum connections: 10
```

Conceptually:

```text
                 ┌───────────────┐
Request ────────►│               │
Request ────────►│ Connection    │
Request ────────►│ Pool          │
Request ────────►│               │
                 └───────┬───────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Conn 1     Conn 2     Conn 3 ...
              │          │          │
              └──────────┼──────────┘
                         ▼
                     PostgreSQL
```

The pool is created during FastAPI application startup and closed during shutdown.

This avoids repeatedly establishing PostgreSQL connections under normal request traffic.

---

# Configuration and Environment Variables

Configuration is handled through `pydantic-settings`.

The application reads environment variables rather than hardcoding secrets or database credentials.

Example:

```env
DATABASE_URL=postgresql://expense_app:YOUR_PASSWORD@localhost:5432/expense_tracker
TEST_DATABASE_URL=postgresql://expense_app:YOUR_PASSWORD@localhost:5432/expense_tracker_test
JWT_SECRET_KEY=replace_with_a_secure_random_secret
ALLOWED_ORIGINS=http://localhost:3000
```

A template is provided in:

```text
.env.example
```

Actual environment files are excluded from Git.

For the Docker/Compose setup, the local `.env.docker` file contains the Docker-specific database hostname:

```text
host.docker.internal
```

It is intentionally not committed.

---

# CORS

Allowed origins are configured through:

```env
ALLOWED_ORIGINS
```

Multiple origins can be supplied as a comma-separated list.

For example:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

The application converts this environment value into a list before configuring FastAPI's CORS middleware.

This avoids hardcoding development or production frontend URLs into application code.

---

# Database Migrations

Database schema changes are managed with **Alembic**.

The project uses raw SQL for application database access, but Alembic is still useful as a migration/versioning system.

The distinction is:

```text
Application
    │
    └── psycopg + raw SQL
            │
            ▼
       PostgreSQL

Schema changes
    │
    └── Alembic migrations
            │
            ▼
       PostgreSQL
```

There is currently an initial migration:

```text
initial_schema
```

It creates:

```text
users
categories
expenses
```

along with their constraints and indexes.

The current database is at:

```text
initial_schema (head)
```

---

## Why migrations matter

Without migrations, a database schema can exist only as a collection of manual commands someone happened to run.

With migrations, schema evolution becomes versioned:

```text
Migration 001
     │
     ▼
Initial schema
     │
     ▼
Migration 002
     │
     ▼
Future schema
     │
     ▼
Migration 003
     │
     ▼
...
```

This makes schema changes reproducible across environments.

---

# Testing

The project uses `pytest`.

Tests run against a dedicated PostgreSQL database:

```text
expense_tracker_test
```

The application database and test database are intentionally separate.

```text
Development
    │
    ▼
expense_tracker

Tests
    │
    ▼
expense_tracker_test
```

Before tests run, the test database is cleaned using:

```sql
TRUNCATE TABLE expenses, categories, users
RESTART IDENTITY
CASCADE;
```

This prevents test data from leaking between tests.

---

# Test Structure

```text
tests/
├── conftest.py
├── test_health.py
├── test_auth.py
├── test_categories.py
└── test_expenses.py
```

`conftest.py` provides shared fixtures such as:

- test client
- authenticated user
- authentication headers
- category
- expense
- second authenticated user

These fixtures reduce repetitive setup and make individual tests easier to read.

---

# What Is Tested?

The test suite covers:

- Health endpoint
- Readiness endpoint
- User creation
- Authentication
- JWT-protected routes
- Invalid credentials
- Role-based authorization
- Admin-only endpoints
- Category creation
- Category validation
- Expense creation
- Expense retrieval
- Expense updates
- Expense deletion
- Category filtering
- Expense totals
- User ownership
- Cross-user access restrictions
- Error cases

The current test suite contains:

```text
41 tests
```

with the full suite passing.

```text
41 passed
```

---

# Docker

The application is containerized using Docker.

The Docker image is based on:

```text
python:3.13-slim
```

The Dockerfile:

1. Creates `/app`
2. Copies runtime requirements
3. Installs dependencies
4. Copies application code
5. Copies Alembic migrations
6. Copies `alembic.ini`
7. Exposes port `8000`
8. Starts Uvicorn

The resulting flow is:

```text
Source Code
     │
     ▼
 Dockerfile
     │
     ▼
Docker Image
     │
     ▼
Container
     │
     ▼
FastAPI
```

---

# Docker Image vs Container

A useful mental model:

```text
Docker Image
     │
     │ docker run
     ▼
Docker Container
```

The image is the packaged application.

The container is a running instance of that image.

This project produces:

```text
expense-tracker-api:latest
```

---

# Docker Compose

Docker Compose is used to describe how the API container should run.

The current Compose setup contains the API service:

```text
compose.yaml
```

Conceptually:

```mermaid
flowchart LR
    Host["Ubuntu Host"]
    Compose["Docker Compose"]
    API["Expense Tracker API"]
    PG[("PostgreSQL 16")]

    Host --> Compose
    Compose --> API
    API -->|"host.docker.internal:5432"| PG
```

PostgreSQL remains installed directly on the host for this development/deployment setup.

It is deliberately not duplicated as another container.

This gives the current environment:

```text
Ubuntu
│
├── PostgreSQL
│   └── :5432
│
└── Docker
    └── expense-tracker-api
        └── :8000
```

---

# Docker Networking

Containers have their own network namespace, so:

```text
localhost
```

inside the container does **not** mean the Ubuntu host.

Inside the API container:

```text
localhost:5432
```

would mean:

```text
the API container itself
```

To reach PostgreSQL running on the host, the Compose configuration uses:

```text
host.docker.internal
```

which resolves to the Docker host gateway.

The final connection path is:

```text
FastAPI container
       │
       ▼
host.docker.internal
       │
       ▼
172.17.0.1:5432
       │
       ▼
PostgreSQL
```

PostgreSQL is configured to accept the Docker network through `pg_hba.conf`.

---

# Health and Readiness Checks

The application exposes two operational checks:

```text
/health
/ready
```

These serve different purposes.

```mermaid
flowchart TD
    Request["Health / Readiness Request"]

    Request --> Health{"Which check?"}

    Health -->|/health| Alive["Application process alive"]
    Health -->|/ready| DB["Can acquire PostgreSQL connection?"]

    Alive --> Healthy["200 OK"]
    DB -->|Yes| Ready["200 OK"]
    DB -->|No| Unready["503 Service Unavailable"]
```

This makes it possible for an external system to distinguish:

```text
Application is running
```

from:

```text
Application is actually ready to serve requests
```

---

# Deployment Flow

The intended deployment sequence is:

```mermaid
flowchart TD
    Code["Application Code"]
    Build["Build Docker Image"]
    Migration["Run Alembic Migrations"]
    Start["Start API Container"]
    Health["Health Check"]
    Ready["Readiness Check"]
    Running["Application Ready"]

    Code --> Build
    Build --> Migration
    Migration --> Start
    Start --> Health
    Health --> Ready
    Ready --> Running
```

The migration step is intentionally separate from application startup.

The API does **not** automatically execute:

```bash
alembic upgrade head
```

every time the application starts.

Instead, migrations are an explicit deployment operation.

For example:

```bash
docker compose run --rm api alembic upgrade head
```

followed by:

```bash
docker compose up -d
```

This keeps database schema changes separate from simply starting the web server.

---

# Running Locally

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd expense-tracker
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

## 3. Install dependencies

Runtime dependencies:

```bash
pip install -r requirements.txt
```

Development dependencies:

```bash
pip install -r requirements-dev.txt
```

## 4. Configure environment variables

Copy:

```bash
cp .env.example .env
```

Then edit `.env` with your local PostgreSQL credentials and JWT secret.

Example:

```env
DATABASE_URL=postgresql://expense_app:YOUR_PASSWORD@localhost:5432/expense_tracker
TEST_DATABASE_URL=postgresql://expense_app:YOUR_PASSWORD@localhost:5432/expense_tracker_test
JWT_SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000
```

## 5. Run migrations

```bash
alembic upgrade head
```

## 6. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive Swagger documentation:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

# Running with Docker Compose

Create the Docker-specific environment file:

```bash
cp .env .env.docker
```

Change the database host in `.env.docker` to:

```text
host.docker.internal
```

Then build and start the API:

```bash
docker compose up --build
```

Run migrations separately:

```bash
docker compose run --rm api alembic upgrade head
```

For background execution:

```bash
docker compose up -d
```

Check the running service:

```bash
docker compose ps
```

Check readiness:

```bash
curl http://localhost:8000/ready
```

Expected response:

```json
{
  "status": "ready"
}
```

---

# Running Tests

Make sure the test database exists and the test environment is configured.

Then run:

```bash
pytest
```

For more verbose output:

```bash
pytest -v
```

The expected current result is:

```text
41 passed
```

---

# Useful Commands

### Start development server

```bash
uvicorn app.main:app --reload
```

### Run tests

```bash
pytest
```

### Check migration version

```bash
alembic current
```

### Show migration head

```bash
alembic heads
```

### Apply migrations

```bash
alembic upgrade head
```

### Build Docker image

```bash
docker build -t expense-tracker-api .
```

### Start Compose

```bash
docker compose up
```

### Start Compose in background

```bash
docker compose up -d
```

### Rebuild Compose

```bash
docker compose up --build
```

### View containers

```bash
docker compose ps
```

### View logs

```bash
docker compose logs
```

### Follow logs

```bash
docker compose logs -f
```

### Stop Compose

```bash
docker compose down
```

### Run a one-off migration container

```bash
docker compose run --rm api alembic upgrade head
```

---

# Engineering Decisions

## Why PostgreSQL?

The application has relational data and meaningful relationships:

```text
User → Expenses
User → Categories
Category → Expenses
```

PostgreSQL provides:

- Foreign keys
- Transactions
- Constraints
- Indexes
- Strong data types
- Reliable persistence
- Mature SQL support

This makes it a natural fit for the application.

---

## Why raw SQL instead of an ORM?

This was a deliberate choice.

The goal was to understand what the database is actually doing rather than hiding SQL behind an abstraction.

For example, instead of relying on:

```python
Expense.objects.filter(user_id=user_id)
```

or an ORM equivalent, the application explicitly executes SQL.

That makes concepts such as:

- joins
- indexes
- foreign keys
- constraints
- transactions
- query performance
- parameterized queries

much more visible.

An ORM could certainly be introduced later, but the underlying database concepts should remain understandable.

---

## Why separate repositories?

The repository layer isolates database access.

Instead of scattering SQL throughout the application:

```text
Router
 ├── SQL
 ├── SQL
 ├── SQL
 └── SQL
```

SQL is concentrated in repositories:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
SQL
```

This makes the application easier to reason about and test.

---

## Why separate services?

Services provide a place for business rules and transaction boundaries.

This prevents routers from becoming large collections of unrelated responsibilities.

---

## Why use both application validation and database constraints?

Because they solve different problems.

Application validation:

```text
Client
  ↓
Pydantic
  ↓
Useful API error
```

Database constraints:

```text
Any database client
  ↓
PostgreSQL
  ↓
Data integrity
```

The database should not assume that FastAPI is the only thing that will ever interact with it.

---

## Why use connection pooling?

Opening a new database connection for every request is unnecessary overhead.

A connection pool allows the application to reuse existing database connections.

This becomes increasingly important as request volume increases.

---

## Why use migrations?

Because the database schema is part of the application.

The code and schema need to evolve together.

Alembic provides a versioned history of those schema changes.

---

## Why Docker?

Docker makes the application environment reproducible.

Instead of requiring another developer or deployment machine to manually reproduce:

```text
Python version
Python packages
Application files
Migration files
Server command
```

the Docker image packages the application environment into a repeatable artifact.

---

# Future Improvements

Possible future work includes:

- Pagination for expense listings
- More granular API filtering
- Expense summaries by date range
- Monthly spending reports
- Budget functionality
- Refresh tokens
- Password reset flow
- Email verification
- More comprehensive audit logging
- Rate limiting
- Structured JSON logging
- Automated CI/CD
- Docker image publishing
- Production database hosting
- HTTPS/reverse proxy configuration
- Database backup strategy
- Monitoring and metrics
- API integration tests at greater scale
- Performance testing
- Additional database indexes based on query patterns

These are deliberately not part of the current implementation. The existing system focuses on establishing a solid backend foundation before adding more infrastructure or features.

---

# Project Status

The core API functionality is implemented and tested.

Current engineering capabilities include:

```text
                    Expense Tracker API
                           │
          ┌────────────────┼────────────────┐
          │                │                │
       API Layer       Data Layer        Security
          │                │                │
       FastAPI          PostgreSQL       JWT
       Routers          Raw SQL          Argon2
       Pydantic         psycopg          RBAC
          │                │                │
          └────────────────┼────────────────┘
                           │
                    Production Concerns
                           │
              ┌────────────┼────────────┐
              │            │            │
          Migrations    Logging      Health
              │            │            │
              └────────────┼────────────┘
                           │
                       Deployment
                           │
                    Docker + Compose
```

The project is intentionally small enough to understand end-to-end while containing the major pieces found in substantially larger backend systems.

---

# License

Add the project's license here if/when one is selected.

---

# Author

**Dexter Mtetwa**

Software Engineering graduate focused on Python backend development, databases, and practical AI/ML systems.
