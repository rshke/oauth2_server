# OAuth2 Server

This project is a custom OAuth2 server implementation composed of a FastAPI backend and a SvelteKit frontend. It demonstrates a complete OAuth2 flow including client registration, user authentication, and token management.

## Project Structure

- **backend/**: Python-based OAuth2 provider using FastAPI.
- **frontend/**: SvelteKit application for the user interface (Login, Consent, Registration).
- **client/**: A simple client application to demonstrate the OAuth2 flow.

## Tech Stack

### Backend
- **Language**: Python 3.12
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **OAuth2 Library**: [aioauth](https://github.com/alisaifee/aioauth)
- **Database**: SQLite with [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

### Frontend
- **Framework**: [SvelteKit](https://kit.svelte.dev/)
- **Styling**: [TailwindCSS](https://tailwindcss.com/)
- **UI Components**: [shadcn-svelte](https://www.shadcn-svelte.com/)
- **Language**: TypeScript

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js (Latest LTS recommended)
- [uv](https://github.com/astral-sh/uv) (for Python package management)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```

4. Start the server:
   ```bash
   uv run uvicorn main:app --reload
   ```
   The backend API will be available at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend application will be running at `http://localhost:5173`.

## Features

- **OAuth2 Flows**: Supports Authorization Code flow.
- **User Authentication**: Login and Consent pages.
- **Modern UI**: Clean and responsive interface built with SvelteKit and shadcn-ui.
- **Type Safety**: Full Pydantic validation on the backend and TypeScript on the frontend.
