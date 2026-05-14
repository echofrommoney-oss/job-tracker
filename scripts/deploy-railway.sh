#!/usr/bin/env bash
# Deploy this project to Railway with one command.
#
# Prereqs:
#   - Railway CLI installed:  brew install railway
#                          or curl -fsSL https://railway.app/install.sh | sh
#   - You are logged in:      railway login
#
# What it does:
#   1. Creates (or links) a Railway project
#   2. Adds Postgres + Redis plugins
#   3. Sets environment variables (with asyncpg-flavored DATABASE_URL)
#   4. Deploys
#   5. Generates a public domain

set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-job-tracker}"
POSTGRES_SERVICE="${POSTGRES_SERVICE:-Postgres}"
REDIS_SERVICE="${REDIS_SERVICE:-Redis}"

bold()  { printf "\033[1m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
red()   { printf "\033[31m%s\033[0m\n" "$*" >&2; }

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    red "Missing required command: $1"
    exit 1
  fi
}

require railway

bold "==> Checking Railway auth"
if ! railway whoami >/dev/null 2>&1; then
  red "Not logged in. Run: railway login"
  exit 1
fi
green "Authed as: $(railway whoami)"

bold "==> Linking or creating project '$PROJECT_NAME'"
if [ ! -f ".railway/config.json" ] && [ ! -f "railway.json" ]; then
  railway init --name "$PROJECT_NAME" || true
else
  echo "Project already linked."
fi

bold "==> Adding PostgreSQL plugin"
if ! railway status 2>/dev/null | grep -qi "$POSTGRES_SERVICE"; then
  railway add --database postgres
else
  echo "Postgres plugin already present."
fi

bold "==> Adding Redis plugin"
if ! railway status 2>/dev/null | grep -qi "$REDIS_SERVICE"; then
  railway add --database redis
else
  echo "Redis plugin already present."
fi

bold "==> Setting environment variables"
SECRET_KEY=$(openssl rand -hex 32)

railway variables \
  --set "DATABASE_URL=postgresql+asyncpg://\${{${POSTGRES_SERVICE}.PGUSER}}:\${{${POSTGRES_SERVICE}.PGPASSWORD}}@\${{${POSTGRES_SERVICE}.PGHOST}}:\${{${POSTGRES_SERVICE}.PGPORT}}/\${{${POSTGRES_SERVICE}.PGDATABASE}}" \
  --set "REDIS_URL=\${{${REDIS_SERVICE}.REDIS_URL}}" \
  --set "SECRET_KEY=$SECRET_KEY" \
  --set "ENVIRONMENT=production"

green "Environment variables set."

bold "==> Deploying"
railway up --detach

bold "==> Generating public domain"
railway domain || echo "Domain may already exist — check 'railway status'."

bold "==> Done"
railway status
green "Next: tail the deploy log with 'railway logs', and hit '/health' on the generated domain."
