#!/bin/bash
# MCP Server 중지 스크립트

pkill -f "gunicorn server.main:app" && echo "서버 중지됨" || echo "실행 중인 서버 없음"
