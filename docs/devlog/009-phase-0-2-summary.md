# QS-Gen3.0 개발 진행 보고서

**Date**: 2025-12-12  
**Author**: AI Assistant  
**Status**: Phase 2 완료

---

## 프로젝트 개요

QS-Gen3.0은 PySide6 기반 리테일 퀀트 트레이딩 시스템입니다.

### 기술 스택

| 영역 | 기술 |
|------|------|
| GUI Framework | PySide6 + QFluentWidgets |
| IBKR API | 공식 ibapi 9.81.1 |
| Chart | PyQtGraph |
| Window | qframelesswindow |

---

## 완료된 Phase

### Phase 0: Foundation ✅

- 프로젝트 구조 초기화
- 가상환경 및 의존성 설정
- GUI 프로토타입 (Fluent Design)
- Glassmorphism 이슈 해결 (Windows 24H2 호환성 문제)

### Phase 1: IBKR Core Integration ✅

**문제 해결 과정:**

1. **TWS 연결 TimeoutError** - 초기 연결 실패
   - 원인: TWS 재시작 필요
   - 해결: TWS 재시작 후 연결 성공

2. **ibapi 라이브러리 선택**
   - 테스트: nautilus-ibapi, ib_async, 공식 ibapi
   - 결론: 공식 ibapi 9.81.1 가장 안정적

3. **Qt 크로스 스레드 크래시**
   - 원인: 백그라운드 스레드에서 Qt Signal 직접 emit
   - 해결: Qt.QueuedConnection으로 내부 Signal 연결

**산출물:**

| 파일 | 기능 |
|------|------|
| `src/core/ibkr_bridge.py` | IBKR 연결 Qt Bridge |
| `src/gui/widgets/connection_widget.py` | 연결 상태 LED + Reconnect |

### Phase 2: Live Monitoring ✅

**산출물:**

| 파일 | 기능 |
|------|------|
| `src/gui/widgets/live_chart.py` | Candlestick 차트 (PyQtGraph) |
| `src/gui/widgets/position_panel.py` | 포지션 P&L 테이블 |
| `src/gui/widgets/order_table.py` | 주문 상태 테이블 |

---

## 현재 프로젝트 구조

```
src/
├── core/
│   ├── ibkr_bridge.py      # IBKR Qt Bridge
│   ├── nautilus_bridge.py  # (미사용)
│   └── trading_node.py     # (미사용)
├── gui/
│   ├── mainwindow.py       # 메인 윈도우
│   └── widgets/
│       ├── connection_widget.py
│       ├── live_chart.py
│       ├── position_panel.py
│       └── order_table.py
└── main.py                 # 진입점
```

---

## 다음 단계 (Phase 3)

- Order Entry Dialog
- Order Cancel/Modify
- Strategy Control (start/stop)

---

## 주요 학습 사항

1. **TWS API**: 연결 문제 시 TWS 재시작이 가장 효과적
2. **Qt 스레드**: 백그라운드에서 Signal emit 시 QueuedConnection 필수
3. **ibapi 버전**: 공식 버전이 가장 안정적 (ib_async보다 권장)
