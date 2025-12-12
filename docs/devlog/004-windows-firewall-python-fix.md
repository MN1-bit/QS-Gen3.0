# Windows 방화벽 Python 차단 해결 가이드

**Date**: 2025-12-12  
**Issue**: TWS 연결 TimeoutError

---

## 증상

```
API connection failed: TimeoutError()
```

TWS API 설정이 올바르지만 Python에서 연결 불가.

---

## 진단

### 1. 포트 연결 테스트

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 7497
```

**TcpTestSucceeded: False** → 포트가 열려있지 않음

---

## 해결 방법

### 방법 1: Windows 방화벽 규칙 추가

1. **Windows 검색** → "Windows Defender 방화벽" 입력
2. **고급 설정** 클릭
3. **인바운드 규칙** → **새 규칙**
4. 설정:
   - 규칙 유형: **프로그램**
   - 프로그램 경로: `C:\Program Files\Python313\python.exe`
   - 작업: **연결 허용**
   - 이름: "Python IBKR"
5. **마침**

### 방법 2: PowerShell로 규칙 추가 (관리자)

```powershell
# Python 인바운드 규칙
New-NetFirewallRule -DisplayName "Python IBKR" -Direction Inbound -Program "C:\Program Files\Python313\python.exe" -Action Allow

# Python 아웃바운드 규칙
New-NetFirewallRule -DisplayName "Python IBKR Out" -Direction Outbound -Program "C:\Program Files\Python313\python.exe" -Action Allow
```

### 방법 3: 일시적 방화벽 비활성화 (테스트용)

```powershell
# 관리자 권한 필요
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# 테스트 후 다시 활성화
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

---

## 검증

```powershell
# 포트 다시 테스트
Test-NetConnection -ComputerName 127.0.0.1 -Port 7497

# Python 연결 테스트
python -c "from ib_async import IB; ib = IB(); ib.connect('127.0.0.1', 7497, clientId=99); print('Success!'); ib.disconnect()"
```

---

## 다른 원인

| 원인 | 해결 |
|------|------|
| TWS API 비활성화 | Edit → Global Configuration → API → Enable |
| 잘못된 포트 | Paper: 7497, Live: 7496 확인 |
| TWS 미실행 | TWS/Gateway 실행 확인 |
| 다른 프로그램 사용 중 | Client ID 변경 (1-32) |
