# TWS 연결 문제 최종 분석 보고서

**Date**: 2025-12-12  
**Status**: 🔴 미해결 (Python 측 원인 미확인)

---

## 테스트 결과 요약

| 테스트 | 결과 |
|--------|------|
| 포트 7497 열림 | ✅ TcpTestSucceeded: True |
| Raw Socket 연결 | ✅ Connected |
| Raw Socket 데이터 수신 | ❌ No data (timeout) |
| nautilus-ibapi 10.30.1 | ❌ TimeoutError |
| ib_async 2.1.0 | ❌ TimeoutError |
| 공식 ibapi 9.81.1 | ❌ 응답 없음 |

---

## 핵심 발견

> **소켓은 연결되지만 TWS가 아무 데이터도 보내지 않음**

이것은 Python 라이브러리 버전과 **무관**합니다.

---

## 분석

### 가능한 원인 (Python 측만 가정)

| 원인 | 확률 | 설명 |
|------|------|------|
| **Python asyncio/socket 버그** | 낮음 | 표준 라이브러리 문제 |
| **handshake 프로토콜** | 중간 | 클라이언트가 첫 메시지를 보내야 할 수 있음 |
| **Windows 소켓 설정** | 중간 | TCP 버퍼, 타임아웃 설정 |
| **ibapi 초기화 순서** | 중간 | connect() 후 run() 필요 |

---

## 검증된 사항

- [x] Python 3.13 호환성 → 문제 없음
- [x] 방화벽 차단 → 없음 (포트 열림)
- [x] ibapi 버전 → 공식 9.81.1도 동일
- [x] 스레드 동기화 → 정상
- [x] nest_asyncio → 적용됨

---

## 권장 다음 단계

1. **IB 공식 Python 샘플 코드** 실행
   - [IB API Download](https://interactivebrokers.github.io) 에서 다운로드
   - `TestApp.py` 예제 실행

2. **TWS 로그 분석** (API 측에서 거부 여부)

3. **다른 PC/환경에서 테스트**

---

## 현재 프로젝트 상태

| 항목 | 상태 |
|------|------|
| GUI 기본 구조 | ✅ 완료 |
| Nautilus 설치 | ✅ 완료 |
| NautilusBridge | ✅ 구현됨 |
| ConnectionWidget | ✅ 구현됨 |
| **IBKR 실제 연결** | ❌ 블로킹 |
