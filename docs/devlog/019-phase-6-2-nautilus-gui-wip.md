# Phase 6.2: NautilusBridge GUI 통합 (WIP)

**Date**: 2025-12-12 14:44  
**Status**: 🚧 진행 중

---

## 진행 사항

### nautilus_ibapi 설치

```bash
pip install git+https://github.com/nautechsystems/ibapi.git
# nautilus_ibapi 10.37.2 설치됨
```

### 환경변수 기반 Bridge 선택

```python
use_nautilus = os.environ.get("USE_NAUTILUS", "0") == "1"

if use_nautilus:
    self._bridge = NautilusBridge(self)
else:
    self._bridge = IBKRBridge(self)
```

### 테스트 결과

| 항목 | 상태 |
|------|------|
| GUI 표시 | ✅ |
| NautilusBridge 사용 | ✅ |
| TradingNode 초기화 | ✅ (624ms) |
| Docker IB Gateway | ✅ (로그인됨) |
| GUI 연결 상태 | ❌ Disconnect |

---

## 남은 과제

- [ ] Nautilus 연결 이벤트 → Qt Signal 연결
- [ ] 시세 데이터 → GUI 차트 연동
- [ ] Position/Order 동기화

---

## 사용 방법

```powershell
# Nautilus 모드
$env:USE_NAUTILUS = "1"
python src/main.py

# 기존 IBKRBridge 모드 (기본값)
python src/main.py
```
