# Phase 5.5: Desktop Notifications + Clean Exit

**Date**: 2025-12-12 14:06  
**Status**: ✅ 완료

---

## Desktop Notifications

### 구현된 알림

| 이벤트 | 메시지 | 타입 |
|--------|--------|------|
| TWS 연결 | "Successfully connected to TWS" | Info |
| TWS 연결 해제 | "Connection to TWS lost" | Warning |
| 주문 체결 | "Order {id} filled" | Info |
| 주문 취소 | "Order {id} cancelled" | Info |

---

## Clean Exit Process

### 문제

- 기존: X 버튼 → 트레이 최소화만, 완전 종료 없음
- 좀비 프로세스: ibapi 스레드가 남아 client ID 점유

### 해결책

1. **Dashboard Exit 버튼** 추가 (빨간색)
2. **Tray Exit** → clean_exit() 연결
3. **clean_exit()** 프로세스:

```python
def clean_exit(self):
    # 1. Tray icon 숨김
    self._tray_icon.hide()
    
    # 2. TWS 연결 해제
    if self._bridge.is_connected:
        self._bridge.disconnect_from_tws()
    
    # 3. 500ms 대기 후 강제 종료
    QTimer.singleShot(500, self._force_exit)

def _force_exit(self):
    QApplication.quit()
    os._exit(0)  # 강제 종료
```

### 테스트 결과

```
종료 전: Python 프로세스 없음
GUI 실행 → Exit 클릭
종료 후: Python 프로세스 없음 ✅
```

**좀비 프로세스 없음 확인!**

---

## 변경 파일

- `src/gui/mainwindow.py`: Exit 버튼, clean_exit(), 알림

---

## 다음 단계

- Phase 6: Nautilus Trader Integration
