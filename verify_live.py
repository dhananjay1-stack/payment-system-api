"""Verify live deployment on Render - full test."""
import requests
import json
import sys

BASE = "https://payment-system-api-69iz.onrender.com"

def test(name, method, url, data=None, headers=None):
    try:
        r = getattr(requests, method)(url, json=data, headers=headers or {}, timeout=30)
        code = r.status_code
        try:
            body = r.json()
        except Exception:
            body = r.text[:300]
        
        if code < 400:
            print("  PASS [{}] {}".format(code, name))
        else:
            detail = json.dumps(body)[:120] if isinstance(body, dict) else str(body)[:120]
            print("  FAIL [{}] {} -> {}".format(code, name, detail))
        return r, code
    except Exception as e:
        print("  ERROR {} -> {}".format(name, e))
        return None, 0

print("=" * 58)
print("  LIVE DEPLOYMENT TEST")
print("  " + BASE)
print("=" * 58)

# --- Basic pages ---
print("\n--- PAGES ---")
r = requests.get(BASE + "/", allow_redirects=False, timeout=30)
print("  {} [{}] Root redirect -> {}".format(
    "PASS" if r.status_code == 302 else "FAIL", r.status_code,
    r.headers.get("Location", "none")))

r = requests.get(BASE + "/swagger/", timeout=30)
print("  {} [{}] Swagger UI".format("PASS" if r.status_code == 200 else "FAIL", r.status_code))

r = requests.get(BASE + "/redoc/", timeout=30)
print("  {} [{}] ReDoc".format("PASS" if r.status_code == 200 else "FAIL", r.status_code))

r = requests.get(BASE + "/admin/login/", timeout=30)
print("  {} [{}] Admin page".format("PASS" if r.status_code == 200 else "FAIL", r.status_code))

# --- Registration ---
print("\n--- USER REGISTRATION ---")
r, c = test("Register user1", "post", BASE + "/api/accounts/register/", {
    "username": "liveuser1", "email": "live1@test.com",
    "password": "livepass123", "first_name": "Live", "last_name": "User"
})

if c == 500:
    print("\n  *** DATABASE NOT CONFIGURED ***")
    print("  The Register endpoint returned 500.")
    print("  You need to add DATABASE_URL env var in Render.")
    print("  See instructions above.")
    sys.exit(1)

r2, _ = test("Register user2", "post", BASE + "/api/accounts/register/", {
    "username": "liveuser2", "email": "live2@test.com",
    "password": "livepass123", "first_name": "Live2", "last_name": "User2"
})

test("Duplicate user (400)", "post", BASE + "/api/accounts/register/", {
    "username": "liveuser1", "password": "livepass123"
})

# --- Auth ---
print("\n--- AUTHENTICATION ---")
r, _ = test("Login user1", "post", BASE + "/api/accounts/login/", {
    "username": "liveuser1", "password": "livepass123"
})
tokens1 = r.json() if r and r.status_code == 200 else {}
hdr1 = {"Authorization": "Bearer " + tokens1.get("access", "")}

r, _ = test("Login user2", "post", BASE + "/api/accounts/login/", {
    "username": "liveuser2", "password": "livepass123"
})
tokens2 = r.json() if r and r.status_code == 200 else {}
hdr2 = {"Authorization": "Bearer " + tokens2.get("access", "")}

test("Wrong password (401)", "post", BASE + "/api/accounts/login/", {
    "username": "liveuser1", "password": "wrong"
})

test("Token refresh", "post", BASE + "/api/accounts/token/refresh/", {
    "refresh": tokens1.get("refresh", "")
})

# --- Profile ---
print("\n--- PROFILE ---")
test("Get profile", "get", BASE + "/api/accounts/profile/", headers=hdr1)
test("Update profile", "patch", BASE + "/api/accounts/update/",
     {"phone": "9876543210"}, hdr1)
test("No auth (401)", "get", BASE + "/api/accounts/profile/")

# --- Bank Accounts ---
print("\n--- BANK ACCOUNTS ---")
r, _ = test("Add account 1 (SBI)", "post", BASE + "/api/banking/accounts/",
     {"bank_name": "SBI", "account_type": "savings"}, hdr1)
acct1 = r.json().get("account", {}) if r and r.status_code == 201 else {}

test("Add account 2 (HDFC)", "post", BASE + "/api/banking/accounts/",
     {"bank_name": "HDFC", "account_type": "current"}, hdr1)

test("Add account 3 (ICICI)", "post", BASE + "/api/banking/accounts/",
     {"bank_name": "ICICI", "account_type": "savings"}, hdr1)

test("4th account (400 limit)", "post", BASE + "/api/banking/accounts/",
     {"bank_name": "Axis", "account_type": "savings"}, hdr1)

r, _ = test("User2 add account", "post", BASE + "/api/banking/accounts/",
     {"bank_name": "PNB", "account_type": "savings"}, hdr2)
acct2 = r.json().get("account", {}) if r and r.status_code == 201 else {}

test("List accounts", "get", BASE + "/api/banking/accounts/list/", headers=hdr1)

# --- Top Up ---
print("\n--- TOP UP ---")
if acct1.get("id"):
    test("Top up 5000", "post", BASE + "/api/banking/topup/",
         {"account_id": acct1["id"], "amount": "5000.00"}, hdr1)
    test("Negative topup (400)", "post", BASE + "/api/banking/topup/",
         {"account_id": acct1["id"], "amount": "-100"}, hdr1)

# --- Payments ---
print("\n--- PAYMENTS ---")
if acct1.get("id") and acct2.get("account_number"):
    test("Payment 500", "post", BASE + "/api/payments/pay/", {
        "sender_account_id": acct1["id"],
        "receiver_account_number": acct2["account_number"],
        "amount": "500.00", "remarks": "Live test"
    }, hdr1)

    test("Insufficient (400)", "post", BASE + "/api/payments/pay/", {
        "sender_account_id": acct1["id"],
        "receiver_account_number": acct2["account_number"],
        "amount": "99999.00"
    }, hdr1)

    test("Invalid receiver (400)", "post", BASE + "/api/payments/pay/", {
        "sender_account_id": acct1["id"],
        "receiver_account_number": "000000000000",
        "amount": "100.00"
    }, hdr1)

    test("Self transfer (400)", "post", BASE + "/api/payments/pay/", {
        "sender_account_id": acct1["id"],
        "receiver_account_number": acct1.get("account_number", ""),
        "amount": "100.00"
    }, hdr1)

# --- Transactions ---
print("\n--- TRANSACTIONS ---")
r, _ = test("Transaction list", "get", BASE + "/api/payments/transactions/", headers=hdr1)
if r and r.status_code == 200:
    data = r.json()
    count = data.get("count", len(data.get("results", [])))
    print("         Total: {} transactions".format(count))
    for txn in data.get("results", []):
        print("         {} | {} | {} | {}".format(
            txn["reference_id"], txn["amount"], txn["status"],
            txn.get("failure_reason", "")))

# --- Cleanup ---
print("\n--- CLEANUP ---")
if acct1.get("id"):
    test("Delete account", "delete",
         BASE + "/api/banking/accounts/{}/".format(acct1["id"]), headers=hdr1)
test("Deactivate user", "delete", BASE + "/api/accounts/delete/", headers=hdr1)

# --- Summary ---
print("\n" + "=" * 58)
print("  DEPLOYMENT VERIFICATION COMPLETE")
print("=" * 58)
print()
print("  Live URL:  " + BASE)
print("  Swagger:   " + BASE + "/swagger/")
print("  ReDoc:     " + BASE + "/redoc/")
print("  Admin:     " + BASE + "/admin/")
print("  GitHub:    https://github.com/dhananjay1-stack/payment-system-api")
