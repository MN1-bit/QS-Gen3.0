# TWS 연결 문제 해결 보고서

**Date**: 2025-12-12  
**Status**: ✅ 해결됨

---

## 문제

Python에서 TWS API 연결 시 `TimeoutError` 발생.

## 테스트 결과 요약

| 테스트 | 결과 |
|--------|------|
| 포트 7497 열림 | ✅ |
| TWS LISTENING | ✅ (PID 35612) |
| 소켓 연결 | ✅ Connected |
| API handshake | ❌ timeout |

## 원인

**TWS 재시작 필요** - API 설정 변경 또는 내부 상태 문제.

## 해결

```
TWS 완전 종료 → 재시작
```

재시작 후 연결 성공:
```
✅ Account: DUM425288
✅ Market data farm: OK
✅ HMDS data farm: OK
```

## 교훈

1. TWS API 문제 발생 시 **TWS 재시작** 먼저 시도
2. `netstat -ano | FINDSTR "7497"` 로 listening 확인
3. 소켓 연결 성공 + API timeout = handshake 문제

---

## 테스트 도구

| 스크립트 | 용도 |
|----------|------|
| `scripts/test_ibapi_v2.py` | raw socket + ibapi 테스트 |
| `scripts/test_official_ibapi.py` | IB 공식 패턴 테스트 |
| `scripts/diagnose_tws.py` | 환경 진단 |
