# Step 5.1: 실시간 시세 구독 구현

**Date**: 2025-12-12  
**Status**: ✅ 완료

---

## 목표

IBKR TWS로부터 실시간(지연) 시세 데이터를 수신하여 Qt Signal로 전달

---

## 구현 과정

### 1. 첫 번째 시도: 기본 reqMktData

**코드:**
```python
self._client.reqMktData(req_id, contract, "", False, False, [])
```

**결과:**
```
[IBKR] Error 10089: Requested market data requires additional subscription
```

**분석:**
- Paper Trading 계정은 실시간 시세 구독이 없음
- Error 10089 = 유료 시장 데이터 구독 필요

---

### 2. 해결책: Delayed Data 요청

**수정 코드:**
```python
# 지연 데이터 요청 (type 3)
self._client.reqMarketDataType(3)  # 1=Live, 2=Frozen, 3=Delayed, 4=Delayed Frozen
self._client.reqMktData(req_id, contract, "", False, False, [])
```

**결과:**
```
[IBKR] tickPrice: reqId=1001, type=68, price=688.48
[IBKR] tickPrice: reqId=1001, type=66, price=688.42
[IBKR] tickPrice: reqId=1001, type=67, price=688.50
```

**성공!** 지연 데이터가 수신됨

---

### 3. Tick Type 분석

| Type | Real-time | Delayed | 의미 |
|------|-----------|---------|------|
| 1 | ✅ | - | Bid |
| 2 | ✅ | - | Ask |
| 4 | ✅ | - | Last |
| 66 | - | ✅ | Delayed Bid |
| 67 | - | ✅ | Delayed Ask |
| 68 | - | ✅ | Delayed Last |
| 72 | - | ✅ | Delayed High |
| 73 | - | ✅ | Delayed Low |
| 75 | - | ✅ | Delayed Close |
| 76 | - | ✅ | Delayed Open |

---

### 4. 최종 tickPrice 콜백

```python
def tickPrice(self, reqId, tickType, price, attrib):
    # Real-time: 1=bid, 2=ask, 4=last
    # Delayed: 66=bid, 67=ask, 68=last
    if tickType in [4, 68]:  # Last price
        print(f"[IBKR] Last Price {reqId}: ${price:.2f}")
        self._bridge._emit_price(reqId, price)
    elif tickType in [1, 66]:  # Bid
        self._bridge._emit_bid(reqId, price)
    elif tickType in [2, 67]:  # Ask
        self._bridge._emit_ask(reqId, price)
```

---

## 추가된 코드

### IBKRClient (EWrapper)

| 메서드 | 설명 |
|--------|------|
| `tickPrice()` | 가격 틱 수신 콜백 |
| `tickSize()` | 거래량 틱 수신 (미사용) |
| `tickGeneric()` | 기타 틱 수신 (미사용) |

### IBKRBridge (QObject)

| Signal | 타입 | 설명 |
|--------|------|------|
| `price_received` | `Signal(int, float)` | Last 가격 수신 |
| `bid_received` | `Signal(int, float)` | Bid 가격 수신 |
| `ask_received` | `Signal(int, float)` | Ask 가격 수신 |

| 메서드 | 설명 |
|--------|------|
| `subscribe_market_data(symbol, req_id)` | 시세 구독 시작 |
| `unsubscribe_market_data(req_id)` | 시세 구독 해제 |

---

## 테스트 스크립트

**파일**: `scripts/test_market_data.py`

```python
bridge = IBKRBridge()

def on_price(req_id, price):
    print(f"[TEST] Got price: reqId={req_id}, price=${price:.2f}")

bridge.connected.connect(lambda: bridge.subscribe_market_data("SPY", 1001))
bridge.price_received.connect(on_price)
bridge.connect_to_tws()
```

---

## 테스트 결과

```
Connecting to TWS...
[IBKR] Connected! Order ID: 1

=== Connected! Subscribing to SPY ===

[IBKR] Last Price 1001: $688.48
[IBKR] Price 1001: $688.48
[TEST] Got price: reqId=1001, price=$688.48
```

---

## 핵심 학습

1. **Paper Trading = Delayed Data Only**
   - 실시간 시세는 유료 구독 필요
   - `reqMarketDataType(3)`으로 지연 데이터 요청

2. **Tick Type 차이**
   - 실시간: 1, 2, 4
   - 지연: 66, 67, 68 (실시간 + 65)

3. **스레드 안전성**
   - ibapi 콜백은 백그라운드 스레드에서 호출
   - Qt Signal은 `QueuedConnection`으로 메인 스레드 전달

---

## 다음 단계

- Step 5.2: Live Chart에 가격 연동
