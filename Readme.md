# 🚀 FastAPI Auth Boilerplate

> 🔐 A production-ready **FastAPI starter** with PostgreSQL, JWT Authentication, Google Sign-In, and Alembic migrations — built for speed and simplicity.

![FastAPI](https://img.shields.io/badge/FastAPI-⚡-brightgreen?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-🗃️-blue?style=flat-square&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## 🔧 Tech Stack

- ⚡ FastAPI
- 🐘 PostgreSQL
- 🔐 JWT (Access & Refresh Tokens)
- 🔑 Google OAuth2 Sign-In
- 📧 FastAPI-Mail (Email OTP for Signup, Login, Forgot Password)
- 🔄 Alembic (Database Migrations)
- 🐍 Python venv environment

---

## 📦 Project Setup

### ✅ Clone the Repository

```bash
git clone https://github.com/jami-raza/fastapi_auth_boilerplate.git
cd fastapi_auth_boilerplate

# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Start App
uvicorn app.main:app --reload

# For Migration 
alembic revision --autogenerate -m "your message here"
alembic upgrade head

