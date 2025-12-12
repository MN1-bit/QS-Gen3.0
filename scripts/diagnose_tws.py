# scripts/diagnose_tws.py
import sys
import asyncio

print("=" * 50)
print("TWS Connection Diagnostic")
print("=" * 50)

print(f"\n[1] Python: {sys.version}")
print(f"[2] Event loop: {asyncio.get_event_loop()}")

try:
    import nest_asyncio
    nest_asyncio.apply()
    print("[3] nest_asyncio: OK (applied)")
except ImportError:
    print("[3] nest_asyncio: NOT INSTALLED")

try:
    from ib_async import IB
    print(f"[4] ib_async: OK")
except Exception as e:
    print(f"[4] ib_async: ERROR - {e}")

print("\n" + "=" * 50)
print("Connection Test (timeout=60, clientId=10)")
print("=" * 50)

# 연결 테스트
ib = IB()
try:
    ib.connect('127.0.0.1', 7497, clientId=10, timeout=60)
    print(f"\n✅ Connected!")
    print(f"   Accounts: {ib.managedAccounts()}")
    ib.disconnect()
    print("   Disconnected.")
except Exception as e:
    print(f"\n❌ Connection failed: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
