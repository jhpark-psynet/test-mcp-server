# 배포 가이드

이 문서는 Test MCP Server를 Linux 서버에 직접 배포하는 방법을 설명합니다.

## 목차

- [사전 요구사항](#사전-요구사항)
- [설치](#설치)
- [실행](#실행)
- [프로세스 관리](#프로세스-관리)
- [환경 변수](#환경-변수)
- [Health Check](#health-check)
- [로그 관리](#로그-관리)
- [문제 해결](#문제-해결)

---

## 사전 요구사항

### 시스템 요구사항
- Linux (Ubuntu 20.04+, Debian 11+, 또는 호환 배포판)
- Python 3.11 이상
- Node.js 18 이상 (프론트엔드 빌드용)
- 최소 1GB RAM
- 최소 2GB 디스크 공간

### 필수 패키지 설치

```bash
# Ubuntu/Debian
apt update
apt install -y python3 python3-venv python3-pip nodejs npm curl

# Python 버전 확인
python3 --version  # 3.11 이상 필요

# Node.js 버전 확인
node --version  # 18 이상 필요
```

---

## 설치

### 1. 프로젝트 복사

```bash
# 프로젝트를 원하는 위치에 복사
# 예: git clone 또는 scp 등으로 복사
cd /opt/test-mcp-server  # 또는 원하는 경로
```

### 2. Python 가상환경 설정

```bash
# 가상환경 생성
python3 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r server/requirements.txt
```

### 3. 프론트엔드 빌드

```bash
# components 디렉토리로 이동
cd components

# npm 패키지 설치
npm install

# 프로덕션 빌드
npm run build

# 원래 디렉토리로 복귀
cd ..
```

### 4. 로그 디렉토리 생성

```bash
mkdir -p logs
```

### 5. 환경 변수 설정

```bash
# .env.production 파일 수정 (또는 새로 생성)
cat > .env.production << 'EOF'
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
LOG_LEVEL=INFO
SPORTS_API_BASE_URL=https://data.psynet.co.kr
SPORTS_API_KEY=your-api-key-here
USE_MOCK_SPORTS_DATA=false
EOF

# 파일 권한 설정 (API 키 보호)
chmod 600 .env.production
```

---

## 실행

### 개발 모드 실행

```bash
source .venv/bin/activate
ENV=development .venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

### 프로덕션 모드 실행

```bash
source .venv/bin/activate
ENV=production .venv/bin/gunicorn server.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 백그라운드 실행

```bash
# nohup 사용
source .venv/bin/activate
nohup env ENV=production .venv/bin/gunicorn server.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  > logs/gunicorn.log 2>&1 &

# PID 확인
echo $! > logs/gunicorn.pid
cat logs/gunicorn.pid
```

### 서버 중지

```bash
# PID 파일로 중지
kill $(cat logs/gunicorn.pid)

# 또는 프로세스 찾아서 중지
pkill -f "gunicorn server.main:app"
```

---

## 프로세스 관리

### systemd 서비스 등록 (권장)

시스템 재시작 시 자동 실행되도록 systemd 서비스를 등록합니다.

```bash
# 서비스 파일 생성
sudo cat > /etc/systemd/system/mcp-server.service << 'EOF'
[Unit]
Description=Test MCP Server
After=network.target

[Service]
Type=exec
User=root
WorkingDirectory=/opt/test-mcp-server
Environment="ENV=production"
ExecStart=/opt/test-mcp-server/.venv/bin/gunicorn server.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile /opt/test-mcp-server/logs/access.log \
  --error-logfile /opt/test-mcp-server/logs/error.log
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

> **참고**: `WorkingDirectory`와 `ExecStart` 경로를 실제 설치 경로에 맞게 수정하세요.

```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start mcp-server

# 부팅 시 자동 시작 활성화
sudo systemctl enable mcp-server

# 상태 확인
sudo systemctl status mcp-server
```

### systemd 서비스 관리 명령어

```bash
# 시작
sudo systemctl start mcp-server

# 중지
sudo systemctl stop mcp-server

# 재시작
sudo systemctl restart mcp-server

# 상태 확인
sudo systemctl status mcp-server

# 로그 확인
sudo journalctl -u mcp-server -f
```

---

## 환경 변수

### 필수 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `ENV` | 실행 환경 (`production`, `development`) | `development` |

### 선택 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `HTTP_HOST` | 바인딩할 호스트 | `0.0.0.0` |
| `HTTP_PORT` | 서버 포트 | `8000` |
| `LOG_LEVEL` | 로그 레벨 (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `SPORTS_API_BASE_URL` | Sports API 기본 URL | `https://data.psynet.co.kr` |
| `SPORTS_API_KEY` | Sports API 인증 키 | - |
| `USE_MOCK_SPORTS_DATA` | Mock 데이터 사용 여부 | `false` |

---

## Health Check

서버 상태를 확인하는 엔드포인트가 제공됩니다.

### 엔드포인트

```
GET /health
```

### 응답 예시

```json
{
  "status": "healthy",
  "service": "test-mcp-server",
  "environment": "production"
}
```

### 상태 확인 방법

```bash
curl http://localhost:8000/health
```

### 간단한 모니터링 스크립트

```bash
#!/bin/bash
# health_check.sh

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$RESPONSE" = "200" ]; then
  echo "$(date): Server is healthy"
else
  echo "$(date): Server is DOWN (HTTP $RESPONSE)"
  # 필요시 알림 발송 또는 재시작 로직 추가
fi
```

---

## 로그 관리

### 로그 위치

| 파일 | 설명 |
|------|------|
| `logs/server.log` | 애플리케이션 로그 |
| `logs/access.log` | HTTP 접근 로그 (Gunicorn) |
| `logs/error.log` | 에러 로그 (Gunicorn) |

### 로그 로테이션

애플리케이션 로그는 자동으로 로테이션됩니다:
- 파일 크기: 10MB
- 보관 개수: 5개

Gunicorn 로그는 logrotate로 관리할 수 있습니다:

```bash
# /etc/logrotate.d/mcp-server
cat > /etc/logrotate.d/mcp-server << 'EOF'
/opt/test-mcp-server/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload mcp-server > /dev/null 2>&1 || true
    endscript
}
EOF
```

### 실시간 로그 확인

```bash
# 애플리케이션 로그
tail -f logs/server.log

# 접근 로그
tail -f logs/access.log

# systemd 로그
sudo journalctl -u mcp-server -f
```

---

## 문제 해결

### 서버가 시작되지 않는 경우

```bash
# 가상환경 활성화 확인
source .venv/bin/activate
which python  # .venv/bin/python 이어야 함

# 의존성 확인
pip list | grep -E "fastmcp|uvicorn|gunicorn"

# 수동 실행으로 에러 확인
ENV=production python -c "from server.main import app; print('OK')"
```

### 포트 충돌

```bash
# 8000 포트 사용 중인 프로세스 확인
lsof -i :8000
# 또는
netstat -tlnp | grep 8000

# 해당 프로세스 종료
kill -9 <PID>
```

### Health Check 실패

```bash
# 서버 프로세스 확인
ps aux | grep gunicorn

# 로컬에서 직접 테스트
curl -v http://localhost:8000/health

# 포트 리스닝 확인
ss -tlnp | grep 8000
```

### 외부 API 연결 실패

```bash
# DNS 확인
nslookup data.psynet.co.kr

# API 연결 테스트
curl -I https://data.psynet.co.kr

# Mock 데이터로 전환 (임시 해결)
# .env.production 에서 USE_MOCK_SPORTS_DATA=true 설정
```

### 메모리 부족

```bash
# 메모리 사용량 확인
free -h

# 프로세스별 메모리 확인
ps aux --sort=-%mem | head -10

# 워커 수 줄이기 (--workers 2)
```

---

## 프로덕션 체크리스트

배포 전 확인 사항:

- [ ] Python 3.11+ 설치 확인
- [ ] Node.js 18+ 설치 확인
- [ ] 가상환경 생성 및 의존성 설치
- [ ] 프론트엔드 빌드 완료 (`components/assets/` 존재)
- [ ] `.env.production` 설정 완료
- [ ] API 키 설정 및 파일 권한 (chmod 600)
- [ ] 로그 디렉토리 생성
- [ ] Health check 응답 확인
- [ ] systemd 서비스 등록 (선택)
- [ ] 방화벽에서 포트 개방

---

## 빠른 시작 요약

```bash
# 1. 의존성 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt

# 2. 프론트엔드 빌드
cd components && npm install && npm run build && cd ..

# 3. 환경 설정
mkdir -p logs
# .env.production 파일에 API 키 설정

# 4. 실행
ENV=production .venv/bin/gunicorn server.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000

# 5. 확인
curl http://localhost:8000/health
```

---

## 문의

문제가 발생하면 GitHub Issues에 등록해 주세요.
