# QS-Gen3.0 Initial Development Report

**Version**: 0.4.0  
**Date**: 2025-12-12  
**Status**: Planning Phase - All Major Decisions Complete

---

## 1. Executive Summary

QS-Gen3.0은 개인 투자자(Retail Quant)를 위한 차세대 자동화 거래 시스템입니다.

| 핵심 결정 | 선택 |
|----------|------|
| **Core Framework** | Nautilus Trader |
| **GUI Framework** | PySide6-Fluent-Widgets |
| **차트 라이브러리** | PyQtGraph |
| **디자인 시스템** | Windows 11 Fluent Design (Mica + Acrylic) |

> 📚 **관련 토론 문서**
> - [Framework Debate](../argue/framework_debate.md) - Nautilus Trader 채택
> - [GUI Implementation Debate](../argue/gui_implementation_debate.md) - GUI 구현 범위
> - [Glassmorphism Debate](../argue/glassmorphism_framework_debate.md) - Fluent Widgets 채택

---

## 2. Project Vision

### 2.1 Mission Statement
> "개인 투자자도 기관 수준의 퀀트 전략을 실행할 수 있는 접근 가능하고 신뢰할 수 있는 자동화 거래 플랫폼 구축"

### 2.2 Core Values
- **Reliability** (신뢰성): 24/7 무중단 운영
- **Transparency** (투명성): 거래 결정 추적 가능
- **Adaptability** (적응성): 시장 변화 대응
- **Simplicity** (단순성): 사용 편의성 극대화

---

## 3. Technology Stack (Confirmed)

### 3.1 Core Layer
| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Trading Engine** | Nautilus Trader | Production-grade, IBKR 통합 |
| **Broker** | Interactive Brokers | 멀티 에셋, 안정적 API |

### 3.2 GUI Layer
| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Framework** | PySide6-Fluent-Widgets | Windows 11 Native UI |
| **Charts** | PyQtGraph | 고성능 실시간 차트 |
| **Design** | Fluent Design (Mica/Acrylic) | Glassmorphism 효과 |

### 3.3 Support Layer
| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Research** | Vectorbt + Jupyter | 알파 연구 |
| **Database** | SQLite / PostgreSQL | 로컬 캐시 |
| **Packaging** | PyInstaller / Nuitka | 실행 파일 배포 |

---

## 4. GUI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    QS-Gen3.0 Desktop                         │
│              PySide6-Fluent-Widgets + PyQtGraph              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Fluent Design Shell                     │    │
│  │  • Mica 배경 효과 (Windows 11 Native)                │    │
│  │  • Acrylic 사이드바/팝업                             │    │
│  │  • NavigationBar + 시스템 테마 연동                  │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Content Panels                          │    │
│  │  • Live Chart (PyQtGraph in CardWidget)              │    │
│  │  • Position Panel / Order Table                      │    │
│  │  • Log Viewer / Strategy Monitor                     │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    Nautilus Bridge Layer                     │
│              (QAsync Event Loop Integration)                 │
├─────────────────────────────────────────────────────────────┤
│                    Nautilus Trader Core                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. GUI Scope

### 5.1 구현 범위 (In Scope)

| Priority | Component | Description |
|----------|-----------|-------------|
| **P0** | Connection Status | IBKR 연결 상태 표시 |
| **P0** | Live Chart | 실시간 캔들/볼륨 차트 |
| **P0** | Position Panel | 포지션 및 P&L |
| **P0** | Order Table | 주문 현황 |
| **P1** | Manual Order | 수동 주문 입력 |
| **P1** | Strategy Monitor | 전략 상태 on/off |
| **P2** | Backtest Viewer | Tearsheet 통합 |
| **P2** | Log Viewer | 실시간 로그 |

### 5.2 제외 범위 (Out of Scope)

| 기능 | 사유 | 대안 |
|------|------|------|
| 전략 코드 에디터 | IDE가 더 우수 | VSCode |
| 파라미터 최적화 | CLI가 효율적 | Vectorbt + Jupyter |
| 비주얼 전략 빌더 | 과도한 복잡성 | Python 코드 |

---

## 6. Development Roadmap

### Phase 0: Foundation (Week 1-2) 🎯 **시작점**
- [ ] PySide6-Fluent-Widgets 환경 설정
- [ ] Fluent 기반 메인 윈도우 레이아웃
- [ ] 다크 테마 + Mica 효과 적용
- [ ] 기본 네비게이션 구조

### Phase 1: Core Monitoring (Week 3-5)
- [ ] Connection Status Widget
- [ ] PyQtGraph 실시간 차트
- [ ] Position Panel (CardWidget)
- [ ] Order Table (TableWidget)

### Phase 2: Nautilus Integration (Week 6-8)
- [ ] Nautilus Trader 환경 설정
- [ ] QAsync 이벤트 브릿지
- [ ] IBKR Paper Trading 연결
- [ ] 실시간 데이터 스트리밍

### Phase 3: Control Interface (Week 9-10)
- [ ] Manual Order Entry Dialog
- [ ] Strategy Start/Stop Controls
- [ ] System Tray Notifications

### Phase 4: Analytics & Polish (Week 11-12)
- [ ] Backtest Result Viewer
- [ ] Log Viewer with Filtering
- [ ] Settings Persistence (YAML)

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| GUI 응답 시간 | < 16ms (60 FPS) |
| 차트 업데이트 | < 50ms |
| 메모리 사용량 | < 500MB |
| 연결 복구 시간 | < 30초 |

---

## 8. Next Steps

1. **[즉시]** `pip install PySide6-Fluent-Widgets` 환경 구성
2. **[Week 1]** Fluent 메인 윈도우 PoC
3. **[Week 2]** PyQtGraph 차트 통합 테스트
4. **[Week 3]** Nautilus Trader 연동 시작

---

## Appendix

### A. Document History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-12-12 | Initial draft |
| 0.2.0 | 2025-12-12 | Framework decision (Nautilus) |
| 0.3.0 | 2025-12-12 | Changed to desktop GUI (PySide6) |
| 0.4.0 | 2025-12-12 | **Fluent Widgets 채택 (Glassmorphism)** |

### B. Key Dependencies

```
nautilus_trader>=1.200.0
PySide6>=6.6.0
PySide6-Fluent-Widgets>=1.5.0
pyqtgraph>=0.13.0
```

### C. References
- [Nautilus Trader](https://nautilustrader.io/)
- [PyQt-Fluent-Widgets](https://qfluentwidgets.com)
- [PyQtGraph](https://pyqtgraph.readthedocs.io/)
