# 📚 BookVerse API

A RESTful API built with Flask, PostgreSQL, and JWT-based authentication. The application is containerized using Docker and ready for production deployment with Gunicorn.

---

## 🚀 Tech Stack

- **Flask** – lightweight Python web framework
- **SQLAlchemy** – ORM for database interactions
- **PostgreSQL** – relational database
- **Flask-Migrate (Alembic)** – database migrations
- **JWT (Flask-JWT-Extended)** – access & refresh token-based authentication
- **Gunicorn** – WSGI server for production
- **Docker + Docker Compose** – containerized deployment

---

## ⚙️ Setup Instructions

### Clone the repository

Run the following commands in your terminal:

```bash
https://github.com/aykhanko/FLASK-API-BookVerseAPI-DB-PostgreSQL.git
cd FLASK-API-BookVerseAPI-DB-PostgreSQL
```
### Your .env file

Your .env file in the project root and fill in the following values:

```bash
FLASK_APP=main
FLASK_DEBUG=False

JWT_SECRET_KEY = YOUR_SECRET_KEY

DATABASE_URL = postgresql://YOUR_NAME:YOUR_PASSWORD@db:5432/YOUR_DB_NAME
```
Your docker-compose.yml defines two services:

```bash
services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - db    

  db:
    image: postgres:17
    environment:
      POSTGRES_USER: YOUR_NAME
      POSTGRES_PASSWORD: YOUR_PASSWORD
      POSTGRES_DB: YOUR_DB_NAME
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:

```

### Build and start the application

Make sure Docker and Docker Compose are installed, then run:
```bash
docker-compose up --build
```
This will:

Build the Flask application image from the Dockerfile

Start both the Flask API and PostgreSQL database services

Automatically run database migrations on container startup

## 📬 API Endpoints

The following endpoints are available at:  
🔗 **Base URL**: [http://localhost:5000](http://localhost:5000)  

---

### 📚 Books

| Method | Endpoint          | Description             |
|--------|-------------------|-------------------------|
| GET    | `/books/`         | Get list of all books   |
| POST   | `/books/`         | Create a new book       |
| GET    | `/books/<id>`     | Get a single book       |
| PUT    | `/books/<id>`     | Update a book           |
| DELETE | `/books/<id>`     | Delete a book           |

---

### 💬 Comments

| Method | Endpoint            | Description               |
|--------|---------------------|---------------------------|
| GET    | `/comments/`        | Get all comments          |
| POST   | `/comments/`        | Create a comment          |
| GET    | `/comment/<id>`     | Get a single comment      |
| PUT    | `/comment/<id>`     | Update a comment          |
| DELETE | `/comment/<id>`     | Delete a comment          |

---

### 🔐 Authentication

| Method | Endpoint         | Description                  |
|--------|------------------|------------------------------|
| POST   | `/registration/` | Register a new user          |
| POST   | `/login/`        | Log in and receive tokens    |
| POST   | `/refresh/`      | Refresh access token         |
| POST   | `/logout/`       | Revoke user's tokens         |

---

### 👤 User Profile

| Method | Endpoint                            | Description                      |
|--------|-------------------------------------|----------------------------------|
| GET    | `/profile/<username>`              | Get user profile                 |
| PUT    | `/profile/<username>`              | Update user profile              |
| PUT    | `/profile/<username>/changepassword` | Change user password             |
| DELETE | `/profile/<username>`              | Delete user account              |

📖 Swagger UI is enabled by default.  
You can access it at: [http://localhost:5000/swagger-ui](http://localhost:5000/swagger-ui)
### 🐘 Docker Compose Overview

### 🛡️ Environment Variables Summary

| Variable         | Description                                              |
| ---------------- | -------------------------------------------------------- |
| FLASK\_APP       | Entry point of the Flask app                             |
| FLASK\_DEBUG     | Enables/disables debug mode                              |
| JWT\_SECRET\_KEY | Secret key for JWT signing                               |
| DATABASE\_URL    | SQLAlchemy DB URI (connects to Postgres in `db` service) |
