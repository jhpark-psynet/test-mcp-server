## Test MCP Server 개선 제안

### 핵심 진단
- 해시된 번들 파일명이 `package.json` 버전에만 의존해 콘텐츠가 바뀌어도 캐시가 무효화되지 않는 기능적 결함이 존재함. 클라이언트가 구버전 JS/CSS를 재사용할 수 있음.
- `server/main.py`가 구성, 도메인 모델, 비즈니스 로직, FastMCP 핸들러, ASGI 앱 생성까지 단일 파일에서 처리(약 900줄)하며 결합도가 높아 유지보수성과 테스트 용이성이 크게 저하됨.
- 계산기 툴이 사용자 입력을 `eval`로 실행하는 구조여서 고의적 악의 입력에 취약하며, 보안 정책 관점에서 명확한 제약이 부족함.
- FastMCP 내부 비공개 속성(`_mcp_server`)에 직접 접근해 핸들러를 등록하고 있어 라이브러리 변경 시 쉽게 깨질 수 있는 구조. 인터페이스 안정성이 확보되지 않음.
- 테스트가 `ExternalApiClient` 단위 테스트 한 종류에 치중되어 있고, 서버 핵심 로직은 수동 스크립트로만 검증됨. 자동화된 회귀 테스트와 위젯 응답 검증이 부재함.

### 개선 제안 상세

#### 1. 콘텐츠 기반 캐시 버스팅

```ts
// build.ts
const result = await build({ ...config, build: { manifest: true } });
const manifest = JSON.parse(fs.readFileSync(`${outDir}/.vite/manifest.json`, "utf8"));

for (const entry of Object.values(manifest)) {
  const filePath = path.join(outDir, entry.file);
  const hash = crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex").slice(0, 8);
  const hashedName = filePath.replace(/\.js$/, `.${hash}.js`);
  fs.renameSync(filePath, hashedName);

  generatedHtml.push(renderHtml({
    script: `${baseUrl}/${path.basename(hashedName)}`,
    css: entry.css?.map((cssPath) => rewriteCss(cssPath, hash)) ?? [],
  }));
}
```

#### 2. `server/main.py` 모듈화 및 책임 분리

```python
# http/app_factory.py
def create_app(cfg: Config, tool_registry: ToolRegistry, widget_repo: WidgetRepository) -> FastMCP:
    mcp = FastMCP(name=cfg.app_name, stateless_http=True)
    register_list_handlers(mcp, tool_registry, widget_repo, cfg)
    register_call_handler(mcp, tool_registry, widget_repo, cfg, ExternalApiClientFactory(cfg))
    return mcp.streamable_http_app()
```

#### 3. 안전한 계산기 구현

```python
import ast
import operator

SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def safe_eval(expr: str) -> float:
    node = ast.parse(expr, mode="eval").body

    def _eval(n):
        if isinstance(n, ast.BinOp) and type(n.op) in SAFE_OPS:
            return SAFE_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in SAFE_OPS:
            return SAFE_OPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.Num):
            return n.n
        if isinstance(n, ast.Constant):
            return n.value
        raise ValueError("허용되지 않은 연산입니다.")

    return _eval(node)
```

#### 4. FastMCP 핸들러 등록 안정화

```python
class SafeFastMCP(FastMCP):
    def register_list_tools(self, handler):
        try:
            return super()._mcp_server.list_tools()(handler)
        except AttributeError as exc:
            raise RuntimeError("FastMCP 내부 구조가 변경되었습니다.") from exc

def create_mcp_server(cfg, registry):
    mcp = SafeFastMCP(name=cfg.app_name, stateless_http=True)
    mcp.register_list_tools(lambda: build_tool_payload(registry, cfg))
    ...
```

#### 5. 자동화 테스트 확장

```python
# tests/test_tools.py
import pytest
import mcp.types as types
from server.main import create_mcp_server, CONFIG

@pytest.mark.asyncio
async def test_list_tools_returns_widget_meta(mock_assets):
    mcp = create_mcp_server(CONFIG)
    handler = mcp._mcp_server.request_handlers[types.ListToolsRequest]
    result = await handler(types.ListToolsRequest())
    tool = next(t for t in result.tools if t.name == "example-widget")
    assert tool._meta["openai/widgetAccessible"] is True
```

#### 6. 위젯 자원 테스트 및 모니터링

```python
def verify_assets(cfg: Config):
    missing = []
    for widget in REQUIRED_WIDGETS:
        try:
            load_widget_html(widget, cfg.assets_dir)
        except FileNotFoundError:
            missing.append(widget)
    if missing:
        raise RuntimeError(f"다음 위젯 애셋이 없습니다: {', '.join(missing)}")
```

### 요약
- 캐시 버스팅과 보안 취약점을 우선 해결하고, 구조 분리 및 테스트 확장을 통해 유지보수성과 안정성을 확보해야 함.
- 제안된 개선은 단계적으로 적용 가능하며, 우선 순위는 보안/캐시 → 구조 → 테스트 순으로 진행하는 것을 권장함.

---

## ✅ 개선 완료 상태 (Phase 1 - 2025-11-04)

### 완료된 개선사항

#### 2. server/main.py 모듈화 및 책임 분리 ✅ **완료**
- **성과**: 933줄 → 32줄 (96.6% 감소)
- **구조**:
  - `config.py`: 설정 관리
  - `logging_config.py`: 로깅 설정
  - `models/`: 도메인 모델 (Widget, Tool, Schemas)
  - `services/`: 비즈니스 로직 (6개 모듈)
  - `handlers/`: 툴 핸들러
  - `factory/`: MCP 서버 팩토리
- **결과**: 레이어드 아키텍처로 유지보수성 대폭 향상

#### 3. 안전한 계산기 구현 ✅ **완료**
- **구현**: `server/handlers/calculator.py`에 AST 기반 `safe_eval()` 구현
- **보안**: eval() 제거, 허용된 연산만 실행
- **테스트**: 악의적 입력 차단 확인 (`"malicious"` → `Error: Unsupported expression`)
- **결과**: 보안 취약점 해결

### 향후 개선 (선택사항)

#### 1. 콘텐츠 기반 캐시 버스팅 ⏳ **계획됨** (Phase 4)
- REFACTORING_PLAN.md Phase 4 참조
- 각 파일의 내용으로 고유한 해시 생성

#### 4. FastMCP 핸들러 등록 안정화 ⏳ **계획됨** (Phase 2)
- SafeFastMCPWrapper 구현 예정
- REFACTORING_PLAN.md Phase 2 참조

#### 5. 자동화 테스트 확장 ⏳ **진행 중**
- 통합 테스트: 7/9 통과 (외부 API 2개 제외)
- 추가 테스트 확장 가능

#### 6. 빌드 자원 검증 ⏳ **계획됨** (Phase 5)
- verify-build.ts 구현 예정
- REFACTORING_PLAN.md Phase 5 참조

### 참조
- [REFACTORING_PLAN.md](./REFACTORING_PLAN.md) - 전체 리팩토링 계획 및 Phase 1 완료 보고서
- [README.md](./README.md) - 업데이트된 프로젝트 문서
- [claude.md](./claude.md) - 업데이트된 아키텍처 문서

