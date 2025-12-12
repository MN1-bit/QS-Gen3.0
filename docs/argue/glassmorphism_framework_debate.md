# GUI Framework Debate: Windows 11 Glassmorphism 구현

**Date**: 2025-12-12  
**Subject**: PySide6로 완벽한 Windows 11 Native Glassmorphism GUI 구현이 가능한가?  
**Conclusion**: ⚠️ PySide6 단독으로는 부족, **PyQt-Fluent-Widgets** 또는 **PySide6-Fluent-Widgets** 필수

---

## 1. 핵심 질문

> **"Glassmorphism이 완벽 적용된 Windows 11 Native GUI를 PySide6로 구현할 수 있는가?"**

---

## 2. Windows 11 시각 효과 정의

### 2.1 Glassmorphism vs Fluent Design

| 효과 | 설명 | Windows 11 구현 |
|------|------|----------------|
| **Glassmorphism** | 반투명 유리 효과, 블러, 그라데이션 테두리 | CSS 기반 웹 디자인 용어 |
| **Mica** | 바탕화면 통합 반투명 효과 (앱 배경용) | Windows 11 전용 |
| **Acrylic** | 젖빛 유리 효과 (플라이아웃, 메뉴용) | Windows 10/11 |
| **Fluent Design** | Microsoft 디자인 시스템 (Mica + Acrylic + 애니메이션) | 시스템 전체 |

> **Windows 11 Native = Fluent Design = Mica + Acrylic**

---

## 3. PySide6 단독 평가

### 3.1 기본 PySide6의 한계

```python
# PySide6 기본으로는 Windows 11 효과 불가
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication([])
app.setStyle('windows11')  # ❌ 네이티브 Mica/Acrylic 미적용
```

| 기능 | PySide6 기본 지원 |
|------|------------------|
| Mica 효과 | ❌ 미지원 |
| Acrylic 블러 | ❌ 미지원 |
| Fluent 위젯 | ❌ 미지원 |
| 다크/라이트 테마 | ⚠️ 수동 QSS 필요 |
| 애니메이션 | ⚠️ 수동 구현 필요 |

### 3.2 보조 라이브러리 필요

| 라이브러리 | 기능 | PySide6 호환 |
|-----------|------|-------------|
| `win32mica` | Mica 효과만 | ✅ |
| `PySide6-Frameless-Window` | Mica + Acrylic + 프레임리스 | ✅ |
| `QGraphicsBlurEffect` | 일반 블러 (네이티브 아님) | ✅ |

**결론**: PySide6 단독으로는 **Windows 11 Glassmorphism 불가능**

---

## 4. 대안 비교

### 4.1 Option A: PySide6 + Fluent Widgets

> **PySide6-Fluent-Widgets** (PyQt-Fluent-Widgets의 PySide6 버전)

```
┌─────────────────────────────────────────────────────────────┐
│                    PySide6-Fluent-Widgets                    │
├─────────────────────────────────────────────────────────────┤
│  ✅ Mica / Acrylic 배경 효과                                 │
│  ✅ Fluent Design 위젯 세트 (버튼, 카드, 네비게이션 등)      │
│  ✅ 다크/라이트 테마 자동 전환                               │
│  ✅ 시스템 액센트 색상 연동                                  │
│  ✅ Qt Designer 플러그인                                    │
│  ✅ PySide6 공식 지원                                       │
├─────────────────────────────────────────────────────────────┤
│  ⚠️ 라이선스: GPLv3 (상용은 유료)                           │
│  ⚠️ 의존성 추가                                             │
└─────────────────────────────────────────────────────────────┘
```

**설치**:
```bash
pip install PySide6-Fluent-Widgets
```

**예제**:
```python
from qfluentwidgets import FluentWindow, setTheme, Theme
from qfluentwidgets import PrimaryPushButton, LineEdit, CardWidget

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        # Mica 효과 자동 적용
        self.setMicaEffectEnabled(True)
        
        # Fluent 위젯 사용
        self.button = PrimaryPushButton("Connect", self)
        self.input = LineEdit(self)
```

### 4.2 Option B: PySide6 + 직접 Win32 API

```python
# win32mica 사용
import win32mica
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def showEvent(self, event):
        hwnd = int(self.winId())
        win32mica.ApplyMica(hwnd, win32mica.MicaTheme.AUTO)
```

**한계**:
- Mica 배경만 적용됨
- Fluent 위젯은 여전히 수동 구현 필요
- 애니메이션, 테마 전환 등 모두 직접 개발

### 4.3 Option C: Flet (Flutter 기반)

```python
import flet as ft
from flet_blur import WindowEffect

def main(page: ft.Page):
    page.window_effect = WindowEffect.MICA
    page.theme_mode = ft.ThemeMode.DARK
    
ft.app(target=main)
```

**장점**:
- Flutter Material 3 위젯
- 핫 리로드
- 크로스 플랫폼

**단점**:
- Nautilus Trader와 통합 복잡 (별도 프로세스)
- Python 네이티브 아님 (Flutter 런타임)
- 고성능 차트 라이브러리 부족

### 4.4 비교 매트릭스

| 기준 | PySide6 단독 | PySide6 + Fluent | Flet |
|------|-------------|-----------------|------|
| **Mica 효과** | ❌ | ✅ 완벽 | ✅ |
| **Acrylic 효과** | ❌ | ✅ 완벽 | ✅ |
| **Fluent 위젯** | ❌ | ✅ 완벽 | ⚠️ Material |
| **Windows 11 네이티브** | ❌ | ✅ 완벽 | ⚠️ 유사 |
| **Nautilus 통합** | ✅ 쉬움 | ✅ 쉬움 | ❌ 어려움 |
| **PyQtGraph 차트** | ✅ | ✅ | ❌ |
| **라이선스** | LGPL | GPL/상용 | Apache 2.0 |
| **학습 곡선** | 중 | 중 | 낮음 |
| **커뮤니티** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 5. 심판 판결

### 최종 권고

> **PySide6-Fluent-Widgets**를 사용하십시오.

```
✅ 채택: PySide6 + PySide6-Fluent-Widgets
❌ 기각: PySide6 단독 (Glassmorphism 불가)
❌ 기각: Flet (Nautilus 통합 어려움)
```

### 권고 사유

| 요구사항 | PySide6-Fluent-Widgets 충족 |
|----------|---------------------------|
| Windows 11 Native | ✅ Mica + Acrylic 완벽 지원 |
| Glassmorphism | ✅ Fluent Design = Glassmorphism |
| 고성능 차트 | ✅ PyQtGraph 통합 가능 |
| Nautilus 통합 | ✅ Qt 이벤트 루프 공유 |
| 다크 테마 | ✅ 시스템 연동 자동 |

### 라이선스 고려

| 사용 목적 | 라이선스 |
|----------|---------|
| 개인/비상용 | GPLv3 (무료) |
| 상용 배포 | 상용 라이선스 필요 ($499~) |

> 개인 프로젝트(QS-Gen3.0)에서는 **GPLv3로 무료 사용 가능**

---

## 6. 수정된 기술 스택

### Before (순수 PySide6)

```
PySide6 + PyQtGraph + QSS 스타일시트
↓
❌ Windows 11 Native 효과 불가
```

### After (Fluent Widgets 추가)

```
┌─────────────────────────────────────────────────────────────┐
│                    QS-Gen3.0 Desktop                         │
│              PySide6-Fluent-Widgets + PyQtGraph              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Fluent Design Shell                     │    │
│  │  - Mica 배경 효과                                    │    │
│  │  - Acrylic 사이드바/팝업                             │    │
│  │  - Fluent NavigationBar                              │    │
│  │  - 시스템 테마 연동                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Content Area                            │    │
│  │  - PyQtGraph 차트 (Fluent 스타일 커스텀)             │    │
│  │  - Fluent CardWidget 기반 패널                       │    │
│  │  - Fluent TableWidget                                │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    Nautilus Bridge Layer                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 구현 예시

### Fluent 메인 윈도우

```python
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, 
    setTheme, Theme, FluentIcon
)
from qfluentwidgets import SubtitleLabel, CardWidget

class TradingDashboard(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QS-Gen3.0")
        self.resize(1400, 900)
        
        # Mica 효과 활성화
        self.setMicaEffectEnabled(True)
        
        # 네비게이션 설정
        self.addSubInterface(
            self.chart_page, 
            FluentIcon.MARKET, 
            "Chart"
        )
        self.addSubInterface(
            self.position_page, 
            FluentIcon.DOCUMENT, 
            "Positions"
        )
        
    def create_chart_page(self):
        # PyQtGraph 차트를 Fluent Card 안에 배치
        card = CardWidget(self)
        # ... PyQtGraph 위젯 추가
        return card

if __name__ == "__main__":
    app = QApplication([])
    setTheme(Theme.AUTO)  # 시스템 테마 연동
    window = TradingDashboard()
    window.show()
    app.exec()
```

---

## 8. Next Steps

1. **[즉시]** PySide6-Fluent-Widgets 설치 및 PoC
2. **[Week 1]** Fluent 기반 메인 레이아웃 구현
3. **[Week 2]** PyQtGraph 차트를 Fluent Card에 통합
4. **[Week 3]** Nautilus 연동 테스트

---

## Appendix: 참고 자료

| 자료 | 링크 |
|------|------|
| PyQt-Fluent-Widgets GitHub | https://github.com/zhiyiYo/PyQt-Fluent-Widgets |
| PySide6-Fluent-Widgets PyPI | https://pypi.org/project/PySide6-Fluent-Widgets/ |
| qfluentwidgets 문서 | https://qfluentwidgets.com |
| win32mica PyPI | https://pypi.org/project/win32mica/ |

---

**Document Status**: Concluded  
**Decision**: PySide6 단독 기각, **PySide6-Fluent-Widgets** 채택  
**Rationale**: Windows 11 Native Glassmorphism (Mica/Acrylic) 완벽 지원
