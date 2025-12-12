# Glassmorphism Implementation Deep Research

**Date**: 2025-12-12  
**Status**: Research Complete - Root Cause Identified

---

## 1. Executive Summary

PySide6-Fluent-Widgets에서 Mica 효과가 작동하지 않는 **근본 원인**을 발견했습니다.

> **Root Cause**: `PySide6-Frameless-Window` 패키지 미설치

---

## 2. 문제 분석

### 2.1 현재 증상
- `setMicaEffectEnabled(True)` 호출됨
- `win32mica.ApplyMica()` 호출됨
- 결과: **검은 불투명 배경** (Mica 효과 없음)

### 2.2 시스템 환경 확인

| 항목 | 값 | 요구사항 | 상태 |
|------|-----|---------|------|
| Windows Build | **26100** | ≥ 22000 | ✅ 충족 |
| PySide6 | 설치됨 | 필수 | ✅ |
| PySide6-Fluent-Widgets | 설치됨 | 필수 | ✅ |
| **PySide6-Frameless-Window** | **미설치** | 필수 | ❌ **문제** |
| qframelesswindow | **미설치** | 필수 | ❌ **문제** |

### 2.3 FluentWindow 내부 구현 분석

FluentWindow 소스 코드 분석 결과:

```python
# FluentWindowBase에서 Mica 적용 방식
def setMicaEffectEnabled(self, isEnabled: bool):
    if sys.platform != 'win32' or sys.getwindowsversion().build < 22000:
        return
    
    self._isMicaEnabled = isEnabled
    if isEnabled:
        # 핵심: windowEffect 객체가 Mica를 적용
        self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
```

**`self.windowEffect`는 `qframelesswindow` 패키지의 `WindowEffect` 클래스입니다.**

이 패키지가 없으면:
- `windowEffect` 객체가 생성되지 않거나 기본 구현만 있음
- `setMicaEffect()` 호출이 실제로 아무 것도 하지 않음

---

## 3. 해결책

### Option A: PySide6-Frameless-Window 설치 (권장)

```bash
pip install PySide6-Frameless-Window
```

**장점**:
- FluentWindow의 `setMicaEffectEnabled(True)`가 자동으로 작동
- 추가 코드 수정 불필요
- 프레임리스 윈도우, 그림자, 모서리 둥글기 등 추가 기능

### Option B: ctypes로 DWM API 직접 호출

```python
import ctypes
from ctypes import wintypes

dwmapi = ctypes.windll.dwmapi

DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMSBT_MAINWINDOW = 2  # Mica

def apply_mica(hwnd):
    value = ctypes.c_int(DWMSBT_MAINWINDOW)
    dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_SYSTEMBACKDROP_TYPE,
        ctypes.byref(value),
        ctypes.sizeof(value)
    )
```

**단점**:
- FluentWindow의 내부 배경이 여전히 Mica를 가릴 수 있음
- 추가적인 배경 투명화 작업 필요

### Option C: QFluentWidgets 공식 예제 그대로 따라하기

공식 문서에 따르면 FluentWindow는 기본적으로 Mica가 활성화되어 있음.  
하지만 **`qframelesswindow` 의존성이 반드시 설치되어야 함**.

---

## 4. 추가 확인 사항

### Windows 설정 확인
설정 → 개인 설정 → 색 → **투명 효과** 가 **켜짐**인지 확인

### 패키지 충돌 확인
다음 패키지들이 동시에 설치되면 충돌 가능:
- PyQt-Fluent-Widgets
- PyQt6-Fluent-Widgets
- PySide2-Fluent-Widgets
- PySide6-Fluent-Widgets

→ **하나만 설치**되어 있어야 함

---

## 5. 실행 계획

1. **즉시**: `pip install PySide6-Frameless-Window` 실행
2. **설치 후**: 기존 코드 그대로 GUI 재실행
3. **검증**: Mica 효과 확인
4. **실패 시**: Option B (ctypes DWM API) 시도

---

## 6. 참고 자료

| 자료 | URL |
|------|-----|
| PyQt-Frameless-Window GitHub | https://github.com/zhiyiYo/PyQt-Frameless-Window |
| FluentWindow 소스 코드 | qfluentwidgets/window/fluent_window.py |
| DWM API 문서 | https://learn.microsoft.com/windows/win32/api/dwmapi |
| DWMWA_SYSTEMBACKDROP_TYPE | Windows 11 22H2+ 필요 |
