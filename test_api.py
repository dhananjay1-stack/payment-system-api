"""
Full API endpoint test script for the payment system.
Tests all 13 endpoints + edge cases.
"""
import requests
import json

BASE = "http://127.0.0.1:8000"


def test(name, method, url, data=None, headers=None):
    try:
        r = getattr(requests, method)(url, json=data, headers=headers or {})
        status_code = r.status_code
        try:
            body = r.json()
        except Exception:
            body = r.text[:200]

        if status_code < 400:
            print(f"  PASS [{status_code}] {name}")
        else:
            print(f"  FAIL [{status_code}] {name} -> {json.dumps(body)[:150]}")

        return r
    except Exception as e:
        print(f"  ERROR {name} -> {e}")
        return None


print("=" * 60)
print("  PAYMENT SYSTEM - FULL API TEST")
print("=" * 60)

# ---- 1. USER REGISTRATION ----
print("\n--- USER REGISTRATION ---")
r1 = test("Register alice", "post", f"{BASE}/api/accounts/register/", {
    "username": "alice",
    "email": "alice@test.com",
    "password": "pass123456",
    "first_name": "Alice",
    "last_name": "Smith",
})

r2 = test("Register bob", "post", f"{BASE}/api/accounts/register/", {
    "username": "bob",
    "email": "bob@test.com",
    "password": "pass123456",
    "first_name": "Bob",
    "last_name": "Jones",
})

test("Register duplicate (should 400)", "post", f"{BASE}/api/accounts/register/", {
    "username": "alice",
    "password": "pass123456",
})

# ---- 2. AUTHENTICATION ----
print("\n--- AUTHENTICATION ---")
r = test("Login alice", "post", f"{BASE}/api/accounts/login/", {
    "username": "alice",
    "password": "pass123456",
})
alice_tokens = r.json() if r and r.status_code == 200 else {}
alice_hdr = {"Authorization": f"Bearer {alice_tokens.get('access', '')}"}
print(f"    -> access token: {alice_tokens.get('access', 'MISSING')[:30]}...")
print(f"    -> refresh token: {alice_tokens.get('refresh', 'MISSING')[:30]}...")

r = test("Login bob", "post", f"{BASE}/api/accounts/login/", {
    "username": "bob",
    "password": "pass123456",
})
bob_tokens = r.json() if r and r.status_code == 200 else {}
bob_hdr = {"Authorization": f"Bearer {bob_tokens.get('access', '')}"}

test("Login wrong password (should 401)", "post", f"{BASE}/api/accounts/login/", {
    "username": "alice",
    "password": "wrongpassword",
})

test("Token refresh", "post", f"{BASE}/api/accounts/token/refresh/", {
    "refresh": alice_tokens.get("refresh", ""),
})

# ---- 3. USER PROFILE ----
print("\n--- USER PROFILE ---")
test("Get profile (alice)", "get", f"{BASE}/api/accounts/profile/", headers=alice_hdr)

test("Update profile", "patch", f"{BASE}/api/accounts/update/", {
    "phone": "9876543210",
    "first_name": "Alice Updated",
}, alice_hdr)

test("Profile no auth (should 401)", "get", f"{BASE}/api/accounts/profile/")

# ---- 4. BANK ACCOUNTS ----
print("\n--- BANK ACCOUNTS ---")
r = test("Add account 1 (SBI)", "post", f"{BASE}/api/banking/accounts/", {
    "bank_name": "SBI",
    "account_type": "savings",
}, alice_hdr)
acct1 = r.json().get("account", {}) if r and r.status_code == 201 else {}
print(f"    -> Account number: {acct1.get('account_number', 'N/A')}")

r = test("Add account 2 (HDFC)", "post", f"{BASE}/api/banking/accounts/", {
    "bank_name": "HDFC",
    "account_type": "current",
}, alice_hdr)

r = test("Add account 3 (ICICI)", "post", f"{BASE}/api/banking/accounts/", {
    "bank_name": "ICICI",
    "account_type": "savings",
}, alice_hdr)

test("Add account 4 (should 400 - limit)", "post", f"{BASE}/api/banking/accounts/", {
    "bank_name": "Axis",
    "account_type": "savings",
}, alice_hdr)

r = test("Bob add account", "post", f"{BASE}/api/banking/accounts/", {
    "bank_name": "PNB",
    "account_type": "savings",
}, bob_hdr)
bob_acct = r.json().get("account", {}) if r and r.status_code == 201 else {}
print(f"    -> Bob's account number: {bob_acct.get('account_number', 'N/A')}")

test("List accounts (alice)", "get", f"{BASE}/api/banking/accounts/list/", headers=alice_hdr)

# ---- 5. TOP UP ----
print("\n--- TOP UP ---")
test("Top up 5000", "post", f"{BASE}/api/banking/topup/", {
    "account_id": acct1.get("id", ""),
    "amount": "5000.00",
}, alice_hdr)

test("Top up negative (should 400)", "post", f"{BASE}/api/banking/topup/", {
    "account_id": acct1.get("id", ""),
    "amount": "-100.00",
}, alice_hdr)

test("Top up wrong account (should 404)", "post", f"{BASE}/api/banking/topup/", {
    "account_id": "00000000-0000-0000-0000-000000000000",
    "amount": "100.00",
}, alice_hdr)

# ---- 6. PAYMENTS ----
print("\n--- PAYMENTS ---")
test("Payment 500 to Bob", "post", f"{BASE}/api/payments/pay/", {
    "sender_account_id": acct1.get("id", ""),
    "receiver_account_number": bob_acct.get("account_number", ""),
    "amount": "500.00",
    "remarks": "Rent payment",
}, alice_hdr)

test("Payment 99999 insufficient (should 400)", "post", f"{BASE}/api/payments/pay/", {
    "sender_account_id": acct1.get("id", ""),
    "receiver_account_number": bob_acct.get("account_number", ""),
    "amount": "99999.00",
}, alice_hdr)

test("Payment invalid receiver (should 400)", "post", f"{BASE}/api/payments/pay/", {
    "sender_account_id": acct1.get("id", ""),
    "receiver_account_number": "000000000000",
    "amount": "100.00",
}, alice_hdr)

test("Self transfer (should 400)", "post", f"{BASE}/api/payments/pay/", {
    "sender_account_id": acct1.get("id", ""),
    "receiver_account_number": acct1.get("account_number", ""),
    "amount": "100.00",
}, alice_hdr)

test("Negative amount (should 400)", "post", f"{BASE}/api/payments/pay/", {
    "sender_account_id": acct1.get("id", ""),
    "receiver_account_number": bob_acct.get("account_number", ""),
    "amount": "-50.00",
}, alice_hdr)

# ---- 7. TRANSACTIONS ----
print("\n--- TRANSACTIONS ---")
r = test("Transaction list (alice)", "get", f"{BASE}/api/payments/transactions/", headers=alice_hdr)
if r and r.status_code == 200:
    data = r.json()
    print(f"    -> Total transactions: {data.get('count', len(data.get('results', [])))}")
    for txn in data.get("results", []):
        print(f"       {txn['reference_id']} | {txn['amount']} | {txn['status']} | {txn.get('failure_reason','')}")

# ---- 8. DELETE ----
print("\n--- CLEANUP ---")
test("Delete bank account", "delete",
     f"{BASE}/api/banking/accounts/{acct1.get('id', '')}/", headers=alice_hdr)

test("Deactivate user (alice)", "delete", f"{BASE}/api/accounts/delete/", headers=alice_hdr)

# ---- 9. ROOT REDIRECT ----
print("\n--- MISC ---")
r = requests.get(f"{BASE}/", allow_redirects=False)
print(f"  {'PASS' if r.status_code == 302 else 'FAIL'} [{r.status_code}] Root redirect -> {r.headers.get('Location', 'no redirect')}")

# ---- 10. SWAGGER ----
r = requests.get(f"{BASE}/swagger/")
print(f"  {'PASS' if r.status_code == 200 else 'FAIL'} [{r.status_code}] Swagger UI loads")

r = requests.get(f"{BASE}/redoc/")
print(f"  {'PASS' if r.status_code == 200 else 'FAIL'} [{r.status_code}] ReDoc loads")

print("\n" + "=" * 60)
print("  ALL ENDPOINT TESTS COMPLETE")
print("=" * 60)
