# Job Application Tracker

A production-ready REST API for tracking job applications through their lifecycle.
Built with **FastAPI**, **PostgreSQL**, **Redis**, **SQLAlchemy 2.0 (async)**, **Alembic**, and **Docker**, with a minimal HTML dashboard included.

[![tests](https://github.com/echofrommoney-oss/job-tracker/actions/workflows/test.yml/badge.svg)](https://github.com/echofrommoney-oss/job-tracker/actions/workflows/test.yml)
[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://web-production-6efbf.up.railway.app/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)

[🇬🇧 English](#english) · [🇹🇼 繁體中文](#繁體中文)

---

## English

### Overview

A backend service that lets you track every job application from `wishlist` through `applied`, `interview`, `offer`, or `rejected`. Each status change is persisted as a history row, the dashboard aggregates stats in real time, and Redis caches the dashboard response with a 60-second TTL.

This project was built as a demonstration of clean, production-grade Python backend practices:

- Layered architecture (thin routers → services → models)
- Async everywhere (asyncpg, async SQLAlchemy sessions, async tests)
- Type hints on every function, Pydantic v2 schemas
- Schema versioned with Alembic, reversible migrations
- Containerized for local dev and one-click deploy to Railway

### Live Demo

> Replace the placeholder URLs below with your Railway deployment after the first deploy.

| Resource | URL |
|---|---|
| **Dashboard UI** | https://web-production-6efbf.up.railway.app/ |
| **Swagger UI**   | https://web-production-6efbf.up.railway.app/docs |
| **ReDoc**        | https://web-production-6efbf.up.railway.app/redoc |
| **OpenAPI JSON** | https://web-production-6efbf.up.railway.app/openapi.json |
| **Health check** | https://web-production-6efbf.up.railway.app/health |

Quick try:

```bash
curl -X POST https://web-production-6efbf.up.railway.app/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"company":"Acme","position":"Backend Engineer","status":"applied"}'

curl https://web-production-6efbf.up.railway.app/api/v1/dashboard
```

### Screenshots

> Drop PNG/JPG files into `docs/screenshots/` and they will render below.

**Dashboard UI** — status badges colored by lifecycle stage, stats cards on top.

![Dashboard](docs/screenshots/dashboard.png)

**Swagger UI** — auto-generated interactive API documentation.

![Swagger UI](docs/screenshots/swagger.png)

**Status history** — every transition is recorded.

![Status History](docs/screenshots/history.png)

### Tech Stack

| Layer       | Choice                       | Why |
|-------------|------------------------------|-----|
| Framework   | FastAPI 0.115                | Async, auto-generated OpenAPI docs, native type hints |
| Database    | PostgreSQL 15                | Relational integrity, proper schema |
| Cache       | Redis 7                      | Sub-millisecond reads for dashboard aggregations |
| ORM         | SQLAlchemy 2.0 (async)       | Modern typed mappings, async sessions |
| Driver      | asyncpg                      | Fast async Postgres driver |
| Migrations  | Alembic                      | Version-controlled schema changes |
| Validation  | Pydantic v2                  | Request/response schemas, env config |
| Testing     | pytest + httpx.AsyncClient   | Async-native test client |
| Container   | Docker + docker compose      | Reproducible dev environment |
| Deploy      | Railway                      | Free tier, Postgres + Redis add-ons |

### Local Setup

**Prerequisites:** Docker + Docker Compose.

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd job-tracker

# 2. Copy environment template
cp .env.example .env

# 3. Build and start everything (app + Postgres + Redis)
docker compose up --build

# 4. In another terminal, run migrations
docker compose exec app alembic upgrade head
```

Now open:

- **Dashboard:**   http://localhost:8000/
- **Swagger UI:**  http://localhost:8000/docs
- **ReDoc:**       http://localhost:8000/redoc
- **Health:**      http://localhost:8000/health

### API Documentation

FastAPI auto-generates interactive docs from the route signatures and Pydantic schemas:

- **Swagger UI** — http://localhost:8000/docs
- **ReDoc**      — http://localhost:8000/redoc
- **OpenAPI**    — http://localhost:8000/openapi.json

#### Endpoint summary

| Method   | Path                          | Description |
|----------|-------------------------------|-------------|
| `POST`   | `/api/v1/jobs`                | Create a job |
| `GET`    | `/api/v1/jobs`                | List jobs (filter by `status`, search by company/position) |
| `GET`    | `/api/v1/jobs/{id}`           | Get job detail |
| `PATCH`  | `/api/v1/jobs/{id}`           | Update job fields or status |
| `DELETE` | `/api/v1/jobs/{id}`           | Delete a job |
| `GET`    | `/api/v1/jobs/{id}/history`   | Status change history |
| `GET`    | `/api/v1/dashboard`           | Aggregate stats (cached, 60s TTL) |
| `GET`    | `/health`                     | DB + Redis connectivity |
| `GET`    | `/`                           | Minimal HTML dashboard |

### Data Model

**Job** — `id (UUID)`, `company`, `position`, `job_url`, `description`, `status` (`wishlist` / `applied` / `interview` / `offer` / `rejected`), `salary_min`, `salary_max`, `location`, `notes`, `applied_at`, `created_at`, `updated_at`.

**StatusHistory** — every status transition writes a row: `from_status`, `to_status`, `changed_at`. Cascades on job deletion.

### Environment Variables

| Variable        | Default                                                       | Purpose |
|-----------------|---------------------------------------------------------------|---------|
| `DATABASE_URL`  | `postgresql+asyncpg://user:password@db:5432/jobtracker`       | Postgres DSN (asyncpg-flavored) |
| `REDIS_URL`     | `redis://redis:6379`                                          | Redis connection |
| `SECRET_KEY`    | `changeme`                                                    | App secret |
| `ENVIRONMENT`   | `development`                                                 | Env name |

### Testing

Tests run against a separate database (`jobtracker_test`) to avoid touching dev data:

```bash
docker compose exec db createdb -U user jobtracker_test
docker compose exec app pytest -v
```

Override the test database via `TEST_DATABASE_URL`.

### Migrations

```bash
# Create a new migration from model changes
docker compose exec app alembic revision --autogenerate -m "describe change"

# Apply migrations
docker compose exec app alembic upgrade head

# Roll back one
docker compose exec app alembic downgrade -1
```

Every migration includes both `upgrade()` and `downgrade()`.

### Architecture Notes

- **Thin routers** — handlers in `app/routers/` only call `app/services/`. No business logic in HTTP layer.
- **Services** — all logic in `app/services/job_service.py` and `dashboard_service.py`.
- **Dependencies** — `get_db` and `get_redis` injected via `Depends(...)`.
- **Caching** — dashboard stats cached under `dashboard:stats` with 60s TTL, invalidated on every job create/update/delete. Redis failures degrade gracefully.
- **All async** — no synchronous DB calls anywhere in the codebase.

### Project Structure

```
job-tracker/
├── app/
│   ├── main.py                 FastAPI app, routers, exception handler, dashboard route
│   ├── config.py               Settings via pydantic-settings
│   ├── database.py             Async engine + session factory
│   ├── cache.py                Redis client + safe_* helpers
│   ├── dependencies.py         FastAPI DI helpers
│   ├── models/                 SQLAlchemy Job + StatusHistory
│   ├── schemas/                Pydantic request/response schemas
│   ├── routers/                jobs / dashboard / health
│   ├── services/               Business logic (cache, history side-effects)
│   └── static/index.html       Minimal HTML dashboard
├── alembic/                    Migrations
├── tests/                      pytest + httpx async tests
├── docs/screenshots/           Place PNG/JPG screenshots here
├── docker-compose.yml
├── Dockerfile
├── Procfile                    For Render/Heroku-style platforms
├── railway.toml                Railway deploy config
└── requirements.txt
```

### Deployment (Railway)

The repo includes `railway.toml` and `Procfile`. Railway detects both automatically.

1. Push to GitHub.
2. Create a Railway project → **Deploy from GitHub repo**.
3. **Add PostgreSQL plugin.** Railway auto-injects `DATABASE_URL`. The default DSN starts with `postgresql://`; this app needs `postgresql+asyncpg://`. Override the service variable accordingly.
4. **Add Redis plugin** → set `REDIS_URL=${{Redis.REDIS_URL}}`.
5. Set `SECRET_KEY` and `ENVIRONMENT=production`.
6. Deploy. Migrations run automatically via the `release` step in the `Procfile` and the `startCommand` in `railway.toml`.
7. Verify `/health`, `/docs`, and `/`.

**Config files:**

- **`railway.toml`** — builds from the `Dockerfile`, runs `alembic upgrade head` before starting `uvicorn`, polls `/health` for readiness, restarts on failure.
- **`Procfile`** — fallback for Render/Heroku. Declares `release` (migrations) and `web` (uvicorn).

---

## 繁體中文

### 專案簡介

這是一個用來追蹤求職投遞流程的後端服務。每筆職缺可以從 `wishlist`（觀望）→ `applied`（已投遞）→ `interview`（面試中）→ `offer`（拿到 offer）或 `rejected`（拒絕），每一次狀態變更都會寫入 `StatusHistory` 表。Dashboard 即時聚合統計數字，並用 Redis 快取 60 秒。

這個專案的目的，是展示一套乾淨、可上 production 的 Python 後端寫法：

- 分層架構（router 只接 HTTP、邏輯都在 service、資料層用 model）
- 全 async（asyncpg、async SQLAlchemy、async 測試）
- 每個 function 都有型別註解，schema 用 Pydantic v2
- 資料庫 schema 用 Alembic 版控，每個 migration 都可逆
- Docker 化的本地開發環境，可一鍵部署到 Railway

### Live Demo

> 部署完成後請把下方 placeholder URL 換成你自己的 Railway 網址。

| 資源 | URL |
|---|---|
| **Dashboard 頁面**   | https://web-production-6efbf.up.railway.app/ |
| **Swagger UI**       | https://web-production-6efbf.up.railway.app/docs |
| **ReDoc**            | https://web-production-6efbf.up.railway.app/redoc |
| **OpenAPI JSON**     | https://web-production-6efbf.up.railway.app/openapi.json |
| **健康檢查**         | https://web-production-6efbf.up.railway.app/health |

快速試用：

```bash
curl -X POST https://web-production-6efbf.up.railway.app/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"company":"Acme","position":"後端工程師","status":"applied"}'

curl https://web-production-6efbf.up.railway.app/api/v1/dashboard
```

### 截圖

> 把截圖丟到 `docs/screenshots/` 底下，下方就會自動顯示。

**Dashboard 頁面** — 用顏色區分職缺狀態，上方有統計卡片。

![Dashboard](docs/screenshots/dashboard.png)

**Swagger UI** — FastAPI 自動產生的互動式 API 文件。

![Swagger UI](docs/screenshots/swagger.png)

**狀態歷史** — 每次狀態變更都會被記錄。

![Status History](docs/screenshots/history.png)

### 技術選型

| 層級     | 選用                          | 原因 |
|----------|-------------------------------|------|
| Framework | FastAPI 0.115                | Async 原生、自動產生 OpenAPI、型別友善 |
| 資料庫    | PostgreSQL 15                | 關聯式完整、schema 嚴謹 |
| 快取      | Redis 7                      | Dashboard 聚合查詢的低延遲快取 |
| ORM       | SQLAlchemy 2.0（async）      | 現代 typed mapping、async session |
| Driver    | asyncpg                      | 高效能 async Postgres driver |
| Migration | Alembic                      | Schema 版本控管 |
| Validation | Pydantic v2                 | Request/response/env 設定驗證 |
| 測試      | pytest + httpx.AsyncClient   | 原生 async 測試 client |
| 容器化    | Docker + docker compose      | 環境可重現 |
| 部署      | Railway                      | 免費方案、附 Postgres / Redis 外掛 |

### 本地端啟動

**需要先安裝：** Docker 與 Docker Compose。

```bash
# 1. clone repo 並進入資料夾
git clone <your-repo-url>
cd job-tracker

# 2. 複製環境變數範本
cp .env.example .env

# 3. 一次啟動 app + Postgres + Redis
docker compose up --build

# 4. 開另一個 terminal 跑 migration
docker compose exec app alembic upgrade head
```

完成後可以開：

- **Dashboard：**   http://localhost:8000/
- **Swagger UI：**  http://localhost:8000/docs
- **ReDoc：**       http://localhost:8000/redoc
- **健康檢查：**   http://localhost:8000/health

### API 文件

FastAPI 會根據 route signature 和 Pydantic schema 自動產生互動式 API 文件：

- **Swagger UI** — http://localhost:8000/docs
- **ReDoc**      — http://localhost:8000/redoc
- **OpenAPI**    — http://localhost:8000/openapi.json

#### 端點一覽

| Method   | Path                          | 說明 |
|----------|-------------------------------|------|
| `POST`   | `/api/v1/jobs`                | 新增一筆職缺 |
| `GET`    | `/api/v1/jobs`                | 列出職缺（可用 `status` 篩選、用公司/職稱搜尋）|
| `GET`    | `/api/v1/jobs/{id}`           | 取得單筆職缺 |
| `PATCH`  | `/api/v1/jobs/{id}`           | 更新欄位或狀態 |
| `DELETE` | `/api/v1/jobs/{id}`           | 刪除職缺 |
| `GET`    | `/api/v1/jobs/{id}/history`   | 取得狀態變更歷史 |
| `GET`    | `/api/v1/dashboard`           | 聚合統計（Redis 快取，60 秒 TTL）|
| `GET`    | `/health`                     | DB + Redis 健康檢查 |
| `GET`    | `/`                           | 極簡 HTML Dashboard 頁面 |

### 資料模型

**Job** — `id (UUID)`、`company`、`position`、`job_url`、`description`、`status`（`wishlist` / `applied` / `interview` / `offer` / `rejected`）、`salary_min`、`salary_max`、`location`、`notes`、`applied_at`、`created_at`、`updated_at`。

**StatusHistory** — 每次狀態變更都會寫一筆：`from_status`、`to_status`、`changed_at`。職缺被刪除時 cascade 刪除歷史。

### 環境變數

| 變數            | 預設值                                                        | 用途 |
|-----------------|---------------------------------------------------------------|------|
| `DATABASE_URL`  | `postgresql+asyncpg://user:password@db:5432/jobtracker`       | Postgres DSN（asyncpg 格式）|
| `REDIS_URL`     | `redis://redis:6379`                                          | Redis 連線 |
| `SECRET_KEY`    | `changeme`                                                    | 應用 secret |
| `ENVIRONMENT`   | `development`                                                 | 環境名稱 |

### 執行測試

測試會跑在獨立的測試資料庫（`jobtracker_test`），不會碰到 dev 資料：

```bash
docker compose exec db createdb -U user jobtracker_test
docker compose exec app pytest -v
```

需要時可用 `TEST_DATABASE_URL` 覆寫測試資料庫位址。

### Migration

```bash
# 從 model 變更自動產生 migration
docker compose exec app alembic revision --autogenerate -m "describe change"

# 套用最新 migration
docker compose exec app alembic upgrade head

# 回退一個版本
docker compose exec app alembic downgrade -1
```

每個 migration 都必須同時包含 `upgrade()` 與 `downgrade()`。

### 架構說明

- **薄 router** — `app/routers/` 底下的 handler 只負責 HTTP 層，所有邏輯都丟給 service。
- **Service 層** — 邏輯集中在 `app/services/job_service.py` 和 `dashboard_service.py`。
- **依賴注入** — `get_db`、`get_redis` 透過 `Depends(...)` 注入。
- **快取策略** — Dashboard 統計用 `dashboard:stats` 為 key、TTL 60 秒；任何 job 的新增/更新/刪除都會 invalidate。Redis 掛掉時自動降級為直查 DB，不會讓 request 失敗。
- **全 async** — 整個 codebase 沒有任何同步 DB 呼叫。

### 專案結構

```
job-tracker/
├── app/
│   ├── main.py                 FastAPI app、router 註冊、exception handler、dashboard 路由
│   ├── config.py               透過 pydantic-settings 讀環境變數
│   ├── database.py             Async engine + session factory
│   ├── cache.py                Redis client 與 safe_* 包裝
│   ├── dependencies.py         FastAPI DI 共用 helper
│   ├── models/                 SQLAlchemy Job + StatusHistory
│   ├── schemas/                Pydantic request/response schema
│   ├── routers/                jobs / dashboard / health
│   ├── services/               業務邏輯（含快取與歷史紀錄副作用）
│   └── static/index.html       極簡 HTML Dashboard 頁面
├── alembic/                    Migration 檔案
├── tests/                      pytest + httpx async 測試
├── docs/screenshots/           放截圖的位置
├── docker-compose.yml
├── Dockerfile
├── Procfile                    給 Render / Heroku 類平台用
├── railway.toml                Railway 部署設定
└── requirements.txt
```

### 部署到 Railway

repo 裡已經附了 `railway.toml` 和 `Procfile`，Railway 會自動偵測。

1. 推到 GitHub。
2. 在 Railway 建立新專案 → **Deploy from GitHub repo**。
3. **加上 PostgreSQL plugin。** Railway 預設注入的 `DATABASE_URL` 是 `postgresql://...`，但這個專案需要 `postgresql+asyncpg://...`，所以要手動覆寫這個變數。
4. **加上 Redis plugin** → 設 `REDIS_URL=${{Redis.REDIS_URL}}`。
5. 設定 `SECRET_KEY` 與 `ENVIRONMENT=production`。
6. 部署。Migration 會透過 `Procfile` 的 `release` 步驟和 `railway.toml` 的 `startCommand` 自動跑。
7. 驗證 `/health`、`/docs`、`/` 三個端點正常。

**設定檔說明：**

- **`railway.toml`** — 使用 `Dockerfile` build、啟動前先跑 `alembic upgrade head`、用 `/health` 做 readiness check、失敗時自動重啟。
- **`Procfile`** — 給 Render / Heroku 風格的平台用，分成 `release`（migration）與 `web`（uvicorn）兩個 process。
