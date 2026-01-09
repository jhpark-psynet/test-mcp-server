# 배포 가이드

이 문서는 Test MCP Server를 Linux 서버에 직접 배포하는 방법을 설명합니다.

## 목차

- [사전 요구사항](#사전-요구사항)
- [설치](#설치)
- [실행](#실행)
- [프로세스 관리](#프로세스-관리)
- [환경 변수](#환경-변수)
- [보안 설정](#보안-설정)
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
cd ~/apps/test-mcp-server  # 홈 디렉토리 아래에 설치
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
User=username
WorkingDirectory=/home/username/apps/test-mcp-server
Environment="ENV=production"
ExecStart=/home/username/apps/test-mcp-server/.venv/bin/gunicorn server.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile /home/username/apps/test-mcp-server/logs/access.log \
  --error-logfile /home/username/apps/test-mcp-server/logs/error.log
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

> **참고**: `username`을 실제 사용자명으로 변경하세요. (예: `/home/jhpark/apps/test-mcp-server`)

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
| `CORS_ALLOW_ORIGINS` | 허용할 CORS 도메인 (쉼표 구분) | `*` |
| `RATE_LIMIT_PER_MINUTE` | 분당 최대 요청 수 | `60` |
| `RATE_LIMIT_ENABLED` | Rate Limiting 활성화 | `true` |

---

## 보안 설정

프로덕션 환경에서는 반드시 보안 설정을 적용하세요.

### 1. API 키 보호

API 키는 절대로 Git에 커밋하지 마세요.

```bash
# .env.example을 복사하여 사용
cp .env.example .env.production

# 파일 권한 설정 (본인만 읽기/쓰기 가능)
chmod 600 .env.production

# 또는 환경 변수로 직접 설정
export SPORTS_API_KEY="your-secret-key"
```

### 2. CORS 설정

프로덕션에서는 허용할 도메인만 명시하세요.

```bash
# .env.production
CORS_ALLOW_ORIGINS=https://your-domain.com,https://app.your-domain.com
```

`*`를 사용하면 모든 도메인에서 접근 가능하므로 보안에 취약합니다.

### 3. Rate Limiting

기본적으로 분당 60회 요청 제한이 적용됩니다.

```bash
# .env.production
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_ENABLED=true
```

Rate Limit 초과 시 응답:
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later.",
  "retry_after_seconds": 60
}
```

응답 헤더에서 현재 상태 확인 가능:
- `X-RateLimit-Limit`: 분당 최대 요청 수
- `X-RateLimit-Remaining`: 남은 요청 수

### 4. HTTPS 적용 (권장)

Nginx를 리버스 프록시로 사용하여 HTTPS를 적용합니다.

#### 4.1 Nginx 설치

```bash
sudo apt update && sudo apt install -y nginx
```

#### 4.2 HTTP 기본 설정

```bash
sudo tee /etc/nginx/sites-available/mcp-server << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/mcp-server /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

#### 4.3 SSL 인증서 설정

**방법 A: Let's Encrypt (무료)**

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# 인증서 발급 및 Nginx 자동 설정
sudo certbot --nginx -d your-domain.com

# 자동 갱신 확인
sudo certbot renew --dry-run
```

**방법 B: 공인 인증서 (유료/와일드카드)**

인증서 파일이 이미 있는 경우:
```bash
# 인증서 파일 예시
# /usr/local/ssl/your-domain.crt     (인증서)
# /usr/local/ssl/your-domain.key     (개인키)

sudo tee /etc/nginx/sites-available/mcp-server << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /usr/local/ssl/your-domain.crt;
    ssl_certificate_key /usr/local/ssl/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

#### 4.4 HTTPS 확인

```bash
# 로컬 확인
curl -s https://localhost/health

# 외부 확인
curl -sk https://your-domain.com/health

# 인증서 정보 확인
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 5. 방화벽 설정

필요한 포트만 개방하세요.

```bash
# UFW 사용 시
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (HTTPS 리다이렉트용)
ufw allow 443/tcp   # HTTPS
ufw enable

# 내부 포트 8000은 외부에서 직접 접근 불가
```

### 6. 보안 체크리스트

배포 전 확인 사항:

- [ ] `.env` 파일이 Git에 커밋되지 않았는지 확인
- [ ] `.env.production` 파일 권한이 600인지 확인
- [ ] `CORS_ALLOW_ORIGINS`에 특정 도메인만 설정
- [ ] `RATE_LIMIT_ENABLED=true` 설정
- [ ] HTTPS 적용 (Nginx + Let's Encrypt)
- [ ] 방화벽으로 불필요한 포트 차단
- [ ] 정기적인 보안 업데이트 적용

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
# username을 실제 사용자명으로 변경하세요
cat > /etc/logrotate.d/mcp-server << 'EOF'
/home/username/apps/test-mcp-server/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 username username
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
