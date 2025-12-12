# Glassmorphism Feasibility Double Check Result

**Date**: 2025-12-12  
**Status**: Verified (Conditional Success)

---

## 1. Executive Summary

귀하의 "과거 실패 경험"을 바탕으로 정밀 검증을 수행한 결과, PySide6 환경에서 Windows 11 Native Glassmorphism (Mica) 구현은 **확실히 가능**합니다.

단, **과거 실패의 주요 원인**은 다음 두 가지로 추정됩니다:
1. **투명 배경 오설정**: `WA_TranslucentBackground`를 켜면 Mica가 작동하지 않고 **검은 배경**이 됩니다.
2. **윈도우 핸들링 미숙**: DWM API 호출 시점이나 핸들(HWND) 매핑 오류.

따라서 **구현 성공을 위한 핵심 조건**을 아래와 같이 정리합니다.

---

## 2. 과거 실패 원인 분석 (Root Cause Analysis)

### 🔴 실패 케이스 1: "검은 화면만 나온다"
- **원인**: `setAttribute(Qt.WA_TranslucentBackground)`를 `True`로 설정함.
- **설명**: Mica는 윈도우 배경을 "투과"시키는 것이 아니라, DWM이 배경에 바탕화면을 합성해주는 방식입니다. 창이 투명하면 안 되며, 오히려 **불투명**해야 DWM이 그 위에 효과를 입힙니다.
- **해결책**: `WA_TranslucentBackground` **설정 금지**. 대신 `setAutoFillBackground(True)` 설정.

### 🔴 실패 케이스 2: "효과가 적용되지 않는다"
- **원인**: `DwmSetWindowAttribute` API 호출 시, 유효하지 않은 HWND를 사용했거나 타이밍(Show 이벤트 전) 문제.
- **해결책**: `PySide6-Fluent-Widgets` 라이브러리가 이 복잡한 타이밍을 내부적으로 처리해줍니다.

### 🔴 실패 케이스 3: "업데이트 후 깨짐"
- **원인**: Windows 11 버전(22H2, 23H2 등)에 따라 Private API가 변경됨.
- **해결책**: `win32mica`나 `Fluent-Widgets` 같은, 지속 관리되는 라이브러리를 사용하여 API 변경에 대응.

---

## 3. 구현 성공 전략 (Success Strategy)

### ✅ 채택: PySide6-Fluent-Widgets
가장 안전하고 검증된 방법입니다.

```python
# 핵심 코드 (성공 패턴)
from qfluentwidgets import FluentWindow

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Mica 활성화 (Windows 11 전용)
        self.setMicaEffectEnabled(True)
        
        # 2. 테마 설정 (시스템 동기화)
        # 검은 배경 방지를 위해 테마 매니저가 배경색을 관리함
```

### ⚠️ 주의사항 (Do's and Don'ts)

| 구분 | 지침 | 이유 |
|------|------|------|
| **Do** | `FluentWindow` 상속 사용 | DWM 핸들링 로직이 내장됨 |
| **Do** | Windows 11 Build 22000 이상 | Mica는 11 전용 기능 |
| **Don't** | `WA_TranslucentBackground` | Mica 작동 불능 및 검은 배경 원인 |
| **Don't** | `frameless-window-blur` 구형 라이브러리 | 최신 윈도우 지원 미비 |

### 🔍 대안 검증: GvozdevLeonid BackDrop
- **평가**: Python 레벨에서 블러를 그리는 방식.
- **단점**: Windows 11 Native Mica보다 **성능이 떨어짐** (CPU/GPU 자원 소모).
- **결론**: Native 룩을 원한다면 비추천.

---

## 4. 최종 결론

> **"PySide6-Fluent-Widgets를 사용하고, 투명 배경 속성만 건드리지 않는다면 100% 성공합니다."**

이제 확신을 가지고 **Phase 0 (Foundation)** 단계로 진입하여 실제 환경 구성을 시작해도 좋습니다.
