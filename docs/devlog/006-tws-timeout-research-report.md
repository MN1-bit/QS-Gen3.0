# TWS 연결 TimeoutError 연구 보고서

**Date**: 2025-12-12  
**Status**: 연구 완료

---

## 연구 질문

> Python 3.13 호환성이 TimeoutError의 원인인가?

---

## 연구 결과

### ❌ Python 3.13은 원인이 아님

| 근거 | 출처 |
|------|------|
| ib_async는 Python 3.13 **공식 지원** | PyPI: `Python >=3.10`, `Python :: 3.13` 명시 |
| Python 3.14도 지원 예정 | ib_async 공식 문서 |

---

## 실제 원인 분석

### 1. ib_async/ib_insync TimeoutError 공통 원인

| 원인 | 가능성 | 설명 |
|------|--------|------|
| **거래 시간 중 연결 문제** | ⭐⭐⭐⭐⭐ | 정규 거래 시간에만 TimeoutError 발생 보고 다수 |
| **TWS API 버전 불일치** | ⭐⭐⭐⭐ | IB측에서 "outdated API" 경고 |
| **Download open orders** 미체크 | ⭐⭐⭐ | TWS API 설정에서 필요 |
| **Java 메모리 부족** | ⭐⭐⭐ | TWS 4096MB 권장 |
| **TWS 자동 업데이트** | ⭐⭐ | 호환성 깨짐 가능 |

---

### 2. Nautilus Trader IBKR 어댑터 이슈

| 항목 | 정보 |
|------|------|
| **connection_timeout** | 기본 300초 (5분) |
| **환경변수** | `IB_MAX_CONNECTION_ATTEMPTS` 조정 가능 |
| **권장 방식** | Dockerized IB Gateway 사용 |

---

## 핵심 발견

> **IB 지원팀 공식 답변 (2025.11):**  
> "ib_async가 **구식 TWS API 버전**을 사용하고 있을 수 있음. ib_async를 제거하고 **공식 TWS API를 직접 사용**하라고 권고"

---

## 권장 해결 순서

### 1순위: TWS API 설정 재확인

```
☐ "Download open orders on connection" 체크
☐ Java Memory: 4096MB 이상
☐ TWS 버전: 최신 Stable (오프라인 설치)
```

### 2순위: 공식 TWS API 직접 사용 테스트

```python
# ibapi (공식 TWS API) 직접 사용
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
```

### 3순위: Dockerized IB Gateway

```python
# Nautilus 권장 방식
from nautilus_trader.adapters.interactive_brokers.gateway import DockerizedIBGateway
```

---

## 결론

| 접근 | 적합성 |
|------|--------|
| Python 3.13 다운그레이드 | ❌ 불필요 (3.13 공식 지원됨) |
| 공식 TWS API 직접 테스트 | ✅ **권장** |
| Dockerized IB Gateway | ✅ **권장 (장기)** |
| TWS 설정 재점검 | ✅ 필수 |

---

## 다음 단계

1. **공식 ibapi로 연결 테스트** (ib_async 우회)
2. 성공 시: Nautilus 어댑터 설정 조정
3. 실패 시: Dockerized IB Gateway 고려
