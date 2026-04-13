# Chat App

A real-time chat backend built with Django, Django Channels, and Django REST Framework. Supports direct and group conversations, WebSocket-based live messaging, JWT authentication, and Google OAuth2 sign-in.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Local Development](#local-development)
  - [Running with Docker](#running-with-docker)
- [API Reference](#api-reference)
  - [Authentication](#authentication)
  - [Chat](#chat)
  - [WebSocket](#websocket)
- [Data Models](#data-models)
- [Code Quality](#code-quality)
- [Configuration](#configuration)

---

## Features

- **User Registration & Login** — Standard email/password registration with JWT-based authentication
- **Google OAuth2** — Sign in with a Google ID token; accounts are automatically created on first login
- **JWT Token Refresh** — Stateless authentication with access and refresh token support
- **Real-Time Messaging** — WebSocket connections powered by Django Channels and a Redis channel layer
- **Direct & Group Conversations** — Conversations are typed (`direct` or `group`) with optional titles for group chats
- **Message Persistence** — All messages are saved to the database with sender and timestamp metadata
- **Swagger / Redoc API Docs** — Interactive API documentation available out of the box
- **Environment-Aware Database** — SQLite for local development, PostgreSQL for production
- **Dockerized** — Full Docker and Docker Compose support for easy deployment

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Web Framework | Django 5.2 |
| REST API | Django REST Framework 3.16 |
| Real-Time | Django Channels 4.3 + Daphne (ASGI) |
| Channel Layer | Redis (via `channels-redis`) |
| Auth | SimpleJWT + Google OAuth2 |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL 18 |
| API Docs | drf-yasg (Swagger UI + Redoc) |
| Code Formatting | Black |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
chat_app/
├── authentication/         # User model, registration, JWT login, Google OAuth
│   ├── models.py           # CustomUser with UUID primary key
│   ├── views.py            # RegisterView
│   ├── google_auth.py      # GoogleAuthView
│   ├── serializers.py
│   └── urls.py
├── chat/                   # Core chat functionality
│   ├── models.py           # Conversation, ConversationMember, Message
│   ├── consumers.py        # ChatConsumer (WebSocket handler)
│   ├── router.py           # WebSocket URL routing
│   ├── views.py            # REST API views
│   └── urls.py
├── common/                 # Shared utilities
│   ├── models.py           # UUIDTimeStampedModelMixin (base model)
│   ├── choices.py          # Conversation type choices
│   └── utils.py
├── chat_app/               # Django project config
│   ├── settings.py         # Main settings entry point
│   ├── settings_config/
│   │   ├── base.py         # Installed apps, middleware, DRF, Channels config
│   │   ├── database.py     # Environment-aware DB config
│   │   └── swagger.py      # Swagger schema config
│   ├── asgi.py             # ASGI entry point (HTTP + WebSocket routing)
│   └── urls.py             # Root URL configuration
├── Dockerfile
├── app.yaml                # Docker Compose config
├── requirements.txt
├── manage.py
└── .pre-commit-config.yaml
```

---

## Getting Started

### Prerequisites

- Python 3.13
- Redis (running on `localhost:6379` for local development)
- Docker & Docker Compose (for containerized setup)

### Environment Variables

Copy the `.env` file and fill in your values. The following variables are required:

```env
SECRET_KEY=your-django-secret-key
DEBUG=TRUE                        # Set to FALSE for production

# PostgreSQL (only used when DEBUG=FALSE)
DB_NAME=chat_app
DB_USER=admin
DB_PASSWORD=your-db-password
DB_HOST=postgres
DB_PORT=5432

# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

> **Note:** When `DEBUG=TRUE`, the app uses SQLite and no database configuration is needed. When `DEBUG=FALSE`, it connects to PostgreSQL using the variables above.

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd chat_app
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up pre-commit hooks**

   ```bash
   pre-commit install
   ```

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Start Redis** (required for WebSocket channel layer)

   ```bash
   redis-server
   ```

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   The server will be available at `http://localhost:8000`.

   On Windows, you can also use the provided batch script:

   ```bash
   start_chat_app.bat
   ```

### Running with Docker

The `app.yaml` Docker Compose file starts both the Django app and a PostgreSQL instance. Make sure your `.env` has `DEBUG=FALSE` to use PostgreSQL.

1. **Build the Docker image**

   ```bash
   docker build -t chat_app .
   ```

2. **Start all services**

   ```bash
   docker compose -f app.yaml up
   ```

   This spins up:
   - `postgres` — PostgreSQL 18, exposed on port `5434`
   - `chat_app` — Django app, exposed on port `8000`

3. **Run migrations inside the container**

   ```bash
   docker compose -f app.yaml exec chat_app python manage.py migrate
   ```

---

## API Reference

Interactive documentation is available once the server is running:

- **Swagger UI:** `http://localhost:8000/swagger/`
- **Redoc:** `http://localhost:8000/redoc/`

All protected endpoints require a `Bearer` token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register/` | Register a new user | No |
| `POST` | `/auth/login/` | Obtain JWT access & refresh tokens | No |
| `POST` | `/auth/token/refresh/` | Refresh an access token | No |
| `POST` | `/auth/google/` | Sign in with Google ID token | No |

**Register** — `POST /auth/register/`

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Login** — `POST /auth/login/`

```json
{
  "username": "johndoe",
  "password": "securepassword"
}
```

Response:
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

**Google Sign-In** — `POST /auth/google/`

```json
{
  "id_token": "<google-id-token-from-client>"
}
```

A new user account is automatically created if one does not exist for the given Google email. Returns access and refresh JWT tokens.

**Token Refresh** — `POST /auth/token/refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

### Chat

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/index/` | Health check / protected index | Yes |

### WebSocket

Connect to a conversation's real-time channel:

```
ws://localhost:8000/ws/chat/<conversation_id>/
```

- `<conversation_id>` is the UUID of a `Conversation` object.
- The connection is wrapped in Django's `AuthMiddlewareStack`, so session-based authentication is used for the WebSocket handshake.

**Send a message:**

```json
{
  "message": "Hello!"
}
```

**Receive a broadcast:**

```json
{
  "type": "chat_message",
  "message": "Hello!",
  "sender": "johndoe",
  "timestamp": "2026-04-13T10:00:00.000Z"
}
```

All messages sent through the WebSocket are persisted to the database immediately.

---

## Data Models

### `CustomUser`

Extends Django's `AbstractUser` with a UUID primary key.

### `Conversation`

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `type` | String | `direct` or `group` |
| `title` | String (optional) | Display name, used for group chats |
| `created_at` | DateTime | Auto-set on creation |
| `updated_at` | DateTime | Auto-updated on save |

### `ConversationMember`

Links a user to a conversation. The `(conversation, user)` pair is unique — a user can only appear once per conversation.

### `Message`

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `conversation` | FK → Conversation | The conversation this message belongs to |
| `sender` | FK → CustomUser | The user who sent the message |
| `content` | Text | The message body |
| `created_at` | DateTime | Auto-set on creation |

All models inherit from `UUIDTimeStampedModelMixin`, which provides a UUID primary key and `created_at` / `updated_at` timestamp fields.

---

## Code Quality

This project uses [Black](https://black.readthedocs.io/) for automatic code formatting, enforced via a pre-commit hook.

```bash
# Install hooks (run once after cloning)
pre-commit install

# Run manually across all files
pre-commit run --all-files
```

Black is configured for Python 3.13 and runs automatically on every `git commit`.

---

## Configuration

The settings are split across `chat_app/settings_config/` for clarity:

- **`base.py`** — Installed apps, middleware, DRF authentication classes, Channels layer config, CORS origins, Swagger security definitions
- **`database.py`** — Switches between SQLite (`DEBUG=TRUE`) and PostgreSQL (`DEBUG=FALSE`) based on the environment
- **`swagger.py`** — Swagger/Redoc schema generation settings

CORS is currently configured to allow requests from `http://localhost:3000` (typical for a local frontend). Update `CORS_ALLOWED_ORIGINS` in `base.py` for other environments.
