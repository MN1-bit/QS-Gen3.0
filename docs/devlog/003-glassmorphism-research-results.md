# Glassmorphism Research Results

**Date**: 2025-12-12  
**Status**: 🔴 Blocked - Windows 24H2 OS-Level Bug

---

## Summary

Windows 11 24H2 (Build 26100)에서 Mica/Acrylic Glassmorphism 효과가 **title bar에만 적용**되고 **내부 컨텐츠 영역에는 적용되지 않음**.

---

## Test Results

| 테스트 | Title Bar | Content Area | 결론 |
|--------|-----------|--------------|------|
| FluentWindow + setMicaEffectEnabled | ❌ 검은색 | ❌ 검은색 | 실패 |
| ctypes DWM Mica (DWMSBT_MAINWINDOW) | ✅ 효과 있음 | ❌ 검은색 | 부분 성공 |
| ctypes DWM Acrylic (DWMSBT_TRANSIENTWINDOW) | ✅ 효과 있음 | ❌ 검은색 | 부분 성공 |
| QMainWindow + WA_TranslucentBackground | ✅ 효과 있음 | ❌ 검은색 | 부분 성공 |
| FramelessWindow + setAcrylicEffect | ❌ 검은색 | ❌ 검은색 | 실패 |

---

## Key Findings

1. **DWM API 호출은 성공** (result: 0)
2. **Title bar에는 Acrylic 효과가 보임**
3. **내부 컨텐츠는 Qt 위젯이 DWM 효과를 덮어씀**
4. **Windows 24H2 알려진 버그**: GitHub Issues에서 동일 문제 보고됨

---

## Environment

- Windows Build: **26100 (24H2)**
- PySide6: 6.10.1
- PyQt-Frameless-Window: 0.0.85
- EnableTransparency: **1 (활성화됨)**

---

## Conclusion

> **Windows 24H2에서 DWM Glassmorphism 효과는 title bar에만 작동하고 client area(내부)에는 적용되지 않음.**

이는 OS 수준 버그로, Microsoft 업데이트 대기 필요.

---

## Fallback Strategy

1. **현재**: Fluent Design 유지 (Mica 없이)
2. **향후**: Windows 업데이트 후 Mica 재시도
3. **테스트 스크립트**: `scripts/` 폴더에 보관
