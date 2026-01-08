#!/bin/bash
# MCP Server 시작 스크립트

# 스크립트 위치 기준으로 프로젝트 루트 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# 가상환경 활성화
source .venv/bin/activate

# 프로덕션 모드로 실행
ENV=production .venv/bin/gunicorn server.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
