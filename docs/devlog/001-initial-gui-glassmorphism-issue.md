# Devlog 001: Initial GUI Setup & Glassmorphism Issue

**Date**: 2025-12-12  
**Status**: 🔴 **Blocked** - Windows 11 24H2 Known Issue

---

## Summary

PySide6-Fluent-Widgets 기반 GUI PoC 구현 완료. 그러나 **Windows 11 Mica 효과가 작동하지 않음**.

**Root Cause 발견**: Windows 11 24H2 (Build 26100)에서 Mica 효과가 작동하지 않는 것이 알려진 OS 수준 버그.

---

## Timeline

| 시간 | 작업 | 결과 |
|------|------|------|
| 09:10 | 프로젝트 구조 생성 | ✅ |
| 09:28 | Phase 0 Plan 승인 | ✅ |
| 09:29 | 패키지 설치 (글로벌) | ⚠️ qframelesswindow 누락 |
| 09:42 | Mica 미적용 발견 | ❌ |
| 09:46 | win32mica 시도 | ❌ |
| 09:50 | setAutoFillBackground 시도 | ❌ |
| 09:57 | 심층 연구 시작 | - |
| 09:59 | .venv 환경 구축 | ✅ |
| 10:01 | PyQt-Frameless-Window 설치 | ✅ |
| 10:05 | GUI 재실행 | ❌ 여전히 검은 배경 |
| 10:10 | **Windows 24H2 문제 발견** | 🔴 OS 버그 |

---

## Key Discovery

> **Windows 11 24H2 (Build 26100)에서 Mica 효과가 작동하지 않는 것이 알려진 버그입니다.**

- GitHub 이슈: MicaForEveryone, PyQt-Frameless-Window 등에서 보고됨
- Microsoft에서 수정 대기 중

---

## Current Environment

| Component | Version | Status |
|-----------|---------|--------|
| Windows Build | 26100 (24H2) | 🔴 Known Issue |
| Python | 3.x | ✅ |
| PySide6 | 6.10.1 | ✅ |
| PySide6-Fluent-Widgets | Latest | ✅ |
| PyQt-Frameless-Window | 0.0.85 | ✅ |
| qframelesswindow | ✅ Import OK | ✅ |

---

## Next Steps

1. **확인**: Windows 설정에서 투명 효과 켜짐 확인
2. **확인**: 파일 탐색기에서 Mica 보이는지 확인
3. **시도**: ctypes로 DWM API 직접 호출
4. **시도**: Acrylic 효과 대안
5. **Fallback**: Mica 없이 Fluent 테마 유지

---

## Related Documents

- [002-glassmorphism-deep-research.md](./002-glassmorphism-deep-research.md)
- [implementation_plan.md](file:///C:/Users/USER/.gemini/antigravity/brain/907b3052-3b6f-42b9-ad82-8e054ce53eb6/implementation_plan.md)

