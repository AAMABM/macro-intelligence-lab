# Macro Intelligence Lab 🌐

**Live Demo:** [macro-intelligence-lab.vercel.app](https://macro-intelligence-lab.vercel.app)
**API Endpoint:** [macro-intelligence-lab-api.onrender.com](https://macro-intelligence-lab-api.onrender.com)

Macro Intelligence Lab is a full-stack Economic Intelligence Platform. It automates the collection of global economic and market data, serves it via a high-performance API, and provides a premium Bloomberg-style Research Terminal for analysts.

## ✨ Features
*   **Automated ETL Pipelines:** Nightly GitHub Actions connect to the Federal Reserve (FRED) and Yahoo Finance to ingest real-world macroeconomic (CPI, GDP, Unemployment) and market (S&P 500, Gold, FX) data.
*   **Interactive Visualizations:** Beautiful, responsive Plotly time-series charts with dark-theme optimization.
*   **Secure Research Terminal:** JWT-authenticated dashboard with protected routes, sidebar navigation, and customized layout.
*   **Modern Architecture:** Fully containerized (Docker), deployed on cloud infrastructure (Vercel, Render, Neon), and backed by a CI/CD pipeline.

## 🛠️ Tech Stack
*   **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Plotly.js, React Query, Zustand.
*   **Backend:** Python 3.12, FastAPI, SQLAlchemy (Async), Alembic, Pydantic.
*   **Database:** PostgreSQL (Neon Serverless Cloud).
*   **DevOps:** Docker, GitHub Actions (CI/CD & Cron Jobs), Vercel, Render.

## 🏗️ Architecture
```text
[ Client (Vercel) ]  ──>  [ API (Render) ]  ──>  [ DB (Neon) ]
       │                        │
   React UI               FastAPI/Python
       │                        │
[ GitHub Actions ] ─────────────┘
 (Nightly ETL Cron)