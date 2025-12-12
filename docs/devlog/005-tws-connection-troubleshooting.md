# TWS 연결 실패 - Python/라이브러리 측 원인 분석

**Date**: 2025-12-12  
**Status**: 🔴 디버깅 중  
**가정**: TWS 설정은 정상 (API 활성화, 포트 7497, Paper 계정)

---

## 현재 상황

```
포트 7497: ✅ 열림
TWS 설정: ✅ 정상 (사용자 확인)
Python 연결: ❌ TimeoutError
```

---

## Python/라이브러리 측 가능한 원인

### 1. asyncio 이벤트 루프 문제

| 원인 | 설명 | 해결 |
|------|------|------|
| **중첩 이벤트 루프** | Jupyter/IPython에서 이미 루프 실행 중 | `nest_asyncio.apply()` 호출 |
| **이벤트 루프 미실행** | `asyncio.run()` 없이 await 호출 | 동기 메서드 사용 또는 `asyncio.run()` |
| **루프 종료 안 됨** | 이전 연결의 루프가 살아있음 | Python 프로세스 재시작 |

**테스트 코드**:
```python
import nest_asyncio
nest_asyncio.apply()  # 중첩 루프 허용

from ib_async import IB
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=10)
```

---

### 2. Python 버전 호환성

| 원인 | 설명 | 해결 |
|------|------|------|
| **Python 3.13 호환성** | 일부 C 확장이 3.13 미지원 | Python 3.11/3.12 사용 |
| **asyncio 변경** | 3.12+ asyncio API 변경 | `ib_async` 최신 버전 확인 |

**현재 버전 확인**:
```powershell
python --version  # 3.13.x면 호환성 문제 가능
```

---

### 3. ib_async/nautilus_trader 버전 문제

| 원인 | 설명 | 해결 |
|------|------|------|
| **ibapi 버전 불일치** | TWS API 버전과 불일치 | `pip install nautilus-ibapi==10.30.1.0` |
| **ib_async 버그** | 최신 버전 버그 | 이전 버전 시도: `pip install ib_async==1.0.0` |

---

### 4. 동기/비동기 혼합 문제

| 원인 | 설명 | 해결 |
|------|------|------|
| **sync에서 async 호출** | 동기 컨텍스트에서 비동기 호출 | `ib.connect()` 동기 버전 사용 |
| **await 누락** | 비동기 함수에서 await 없음 | await 추가 |

**동기 연결 테스트**:
```python
from ib_async import IB
ib = IB()
# 동기 버전은 내부적으로 루프 처리
ib.connect('127.0.0.1', 7497, clientId=10, timeout=60)
```

---

### 5. timeout 값 문제

| 원인 | 설명 | 해결 |
|------|------|------|
| **기본 timeout 너무 짧음** | 기본 4초, 네트워크 지연 시 부족 | `timeout=60` 설정 |
| **TWS 초기화 지연** | 첫 연결 시 지연 | 더 긴 timeout |

---

### 6. Client ID 관련

| 원인 | 설명 | 해결 |
|------|------|------|
| **Client ID 0 사용** | TWS 내부용 예약 | 1-32 사용 |
| **동일 ID 재사용** | 이전 연결 미종료 | 다른 ID 사용 (10, 20, 30) |

---

### 7. 가상환경 문제

| 원인 | 설명 | 해결 |
|------|------|------|
| **잘못된 Python** | 시스템 Python 사용 중 | `.venv` 활성화 확인 |
| **패키지 미설치** | 가상환경에 패키지 없음 | `pip list` 확인 |
| **손상된 venv** | 가상환경 문제 | venv 재생성 |

---

## 추천 진단 코드

```python
# scripts/diagnose_tws.py
import sys
import asyncio

print(f"Python: {sys.version}")
print(f"Event loop: {asyncio.get_event_loop()}")

try:
    import nest_asyncio
    nest_asyncio.apply()
    print("nest_asyncio: OK")
except ImportError:
    print("nest_asyncio: NOT INSTALLED")

try:
    from ib_async import IB, __version__
    print(f"ib_async: {__version__}")
except Exception as e:
    print(f"ib_async: ERROR - {e}")

# 연결 테스트
ib = IB()
try:
    ib.connect('127.0.0.1', 7497, clientId=10, timeout=60)
    print(f"Connected! Accounts: {ib.managedAccounts()}")
    ib.disconnect()
except Exception as e:
    print(f"Connection failed: {type(e).__name__}: {e}")
```

---

## 다음 시도 순서

1. `nest_asyncio` 적용 후 재시도
2. `timeout=60` 증가
3. `clientId=10` 변경
4. Python 3.11/3.12로 테스트 (3.13 호환성 문제 시)
