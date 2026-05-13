# Payment System - Django REST API

A secure mini payment system built with Django and Django REST Framework. Implements JWT authentication, bank account management, and atomic payment transactions.

## Features

- **User Management**: Register, login, profile CRUD with JWT authentication
- **JWT Auth**: Access token (5 min) + Refresh token (1 day)
- **Bank Accounts**: Add up to 3 accounts per user, top-up balance
- **Payments**: Atomic fund transfers with full audit trail
- **Swagger Docs**: Interactive API documentation at `/swagger/`
- **Admin Panel**: Full data management at `/admin/`

## Tech Stack

- Python 3.10+
- Django 4.2+
- Django REST Framework
- SimpleJWT for authentication
- SQLite (development)
- drf-yasg for Swagger/OpenAPI docs

## Project Structure

```
├── accounts/          # User model, auth, profile management
├── banking/           # Bank accounts, top-up, 3-account limit
├── payments/          # Payment processing, transaction history
├── core/              # Shared permissions, pagination
├── payment_system/    # Django project settings & URLs
├── manage.py
├── requirements.txt
└── README.md
```

## Setup & Run

### 1. Clone & Install Dependencies

```bash
git clone <repo-url>
cd LeadMax_Assignment
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (for Admin)

```bash
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

### 5. Access the App

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/swagger/` | Swagger API Docs |
| `http://127.0.0.1:8000/redoc/` | ReDoc API Docs |
| `http://127.0.0.1:8000/admin/` | Admin Panel |

### 6. Run Tests

```bash
python manage.py test accounts banking payments -v 2
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/accounts/register/` | Register a new user | No |
| POST | `/api/accounts/login/` | Login, get tokens | No |
| POST | `/api/accounts/token/refresh/` | Refresh access token | No |

### User Management

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/accounts/profile/` | Get own profile | Yes |
| PUT/PATCH | `/api/accounts/update/` | Update profile | Yes |
| DELETE | `/api/accounts/delete/` | Deactivate account | Yes |
| GET | `/api/accounts/users/` | List all users (admin) | Admin |

### Bank Accounts

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/banking/accounts/` | Add bank account | Yes |
| GET | `/api/banking/accounts/list/` | List my accounts | Yes |
| DELETE | `/api/banking/accounts/<id>/` | Delete account | Yes |
| POST | `/api/banking/topup/` | Top up balance | Yes |

### Payments

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/payments/pay/` | Make a payment | Yes |
| GET | `/api/payments/transactions/` | My transactions | Yes |

---

## Sample API Requests & Responses

### 1. Register User

**Request:**
```json
POST /api/accounts/register/
{
    "username": "dhananjay",
    "email": "dhananjay@example.com",
    "password": "mypassword123",
    "first_name": "Dhananjay",
    "last_name": "Jagtap",
    "phone": "9876543210"
}
```

**Response (201):**
```json
{
    "message": "User registered successfully.",
    "user": {
        "id": "a1b2c3d4-...",
        "username": "dhananjay",
        "email": "dhananjay@example.com",
        "first_name": "Dhananjay",
        "last_name": "Jagtap",
        "phone": "9876543210",
        "date_of_birth": null,
        "date_joined": "2025-01-15T10:30:00Z"
    }
}
```

### 2. Login

**Request:**
```json
POST /api/accounts/login/
{
    "username": "dhananjay",
    "password": "mypassword123"
}
```

**Response (200):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Refresh Token

**Request:**
```json
POST /api/accounts/token/refresh/
{
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 4. Get Profile

**Request:**
```
GET /api/accounts/profile/
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
    "id": "a1b2c3d4-...",
    "username": "dhananjay",
    "email": "john@example.com",
    "first_name": "Dhananjay",
    "last_name": "Jagtap",
    "phone": "9876543210",
    "date_of_birth": null,
    "date_joined": "2025-01-15T10:30:00Z"
}
```

### 5. Update Profile

**Request:**
```json
PATCH /api/accounts/update/
Authorization: Bearer <access_token>
{
    "first_name": "Vishal',
    "phone": "1234567890"
}
```

**Response (200):**
```json
{
    "message": "Profile updated successfully.",
    "user": {
        "id": "a1b2c3d4-...",
        "username": "dhananjay",
        "email": "dhananjay@example.com",
        "first_name": "Vishal"'
        "last_name": "Jagtap",
        "phone": "1234567890",
        "date_of_birth": null,
        "date_joined": "2025-01-15T10:30:00Z"
    }
}
```

### 6. Add Bank Account

**Request:**
```json
POST /api/banking/accounts/
Authorization: Bearer <access_token>
{
    "bank_name": "State Bank",
    "account_type": "savings"
}
```

**Response (201):**
```json
{
    "message": "Bank account created successfully.",
    "account": {
        "id": "e5f6g7h8-...",
        "owner": "dhananjay",
        "account_number": "482937561034",
        "bank_name": "State Bank",
        "account_type": "savings",
        "balance": "0.00",
        "is_active": true,
        "created_at": "2025-01-15T10:35:00Z"
    }
}
```

### 7. Top Up Balance

**Request:**
```json
POST /api/banking/topup/
Authorization: Bearer <access_token>
{
    "account_id": "e5f6g7h8-...",
    "amount": "5000.00"
}
```

**Response (200):**
```json
{
    "message": "Account topped up successfully.",
    "account": {
        "id": "e5f6g7h8-...",
        "owner": "dhananjay",
        "account_number": "482937561034",
        "bank_name": "State Bank",
        "account_type": "savings",
        "balance": "5000.00",
        "is_active": true,
        "created_at": "2025-01-15T10:35:00Z"
    }
}
```

### 8. Make Payment

**Request:**
```json
POST /api/payments/pay/
Authorization: Bearer <access_token>
{
    "sender_account_id": "e5f6g7h8-...",
    "receiver_account_number": "739281456023",
    "amount": "1500.00",
    "remarks": "Rent payment"
}
```

**Response (200) — Success:**
```json
{
    "message": "Payment successful.",
    "transaction": {
        "id": "i9j0k1l2-...",
        "reference_id": "TXN1705312500123ABC",
        "sender_username": "dhananjay",
        "sender_account_number": "482937561034",
        "receiver_account_number": "739281456023",
        "amount": "1500.00",
        "status": "SUCCESS",
        "remarks": "Rent payment",
        "failure_reason": "",
        "sender_balance_before": "5000.00",
        "sender_balance_after": "3500.00",
        "receiver_balance_before": "200.00",
        "receiver_balance_after": "1700.00",
        "created_at": "2025-01-15T10:40:00Z"
    }
}
```

**Response (400) — Failed:**
```json
{
    "message": "Payment failed.",
    "transaction": {
        "id": "m3n4o5p6-...",
        "reference_id": "TXN1705312600456DEF",
        "sender_username": "dhananjay",
        "sender_account_number": "482937561034",
        "receiver_account_number": "000000000000",
        "amount": "1500.00",
        "status": "FAILED",
        "remarks": "",
        "failure_reason": "Receiver account not found or inactive.",
        "sender_balance_before": null,
        "sender_balance_after": null,
        "receiver_balance_before": null,
        "receiver_balance_after": null,
        "created_at": "2025-01-15T10:41:00Z"
    }
}
```

### 9. Get Transaction History

**Request:**
```
GET /api/payments/transactions/
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "i9j0k1l2-...",
            "reference_id": "TXN1705312500123ABC",
            "sender_username": "dhananjay",
            "sender_account_number": "482937561034",
            "receiver_account_number": "739281456023",
            "amount": "1500.00",
            "status": "SUCCESS",
            "remarks": "Rent payment",
            "failure_reason": "",
            "sender_balance_before": "5000.00",
            "sender_balance_after": "3500.00",
            "receiver_balance_before": "200.00",
            "receiver_balance_after": "1700.00",
            "created_at": "2025-01-15T10:40:00Z"
        }
    ]
}
```

---

## Business Rules

1. **3 Account Limit**: Each user can have a maximum of 3 active bank accounts
2. **Atomic Transfers**: All balance updates use `transaction.atomic()` with `select_for_update()` row locking
3. **Audit Trail**: Every payment attempt (success or failure) creates a Transaction record
4. **Balance Snapshots**: Sender/receiver balances are recorded before and after each transaction
5. **Self-Transfer Blocked**: Users cannot transfer money to their own account
6. **JWT Auth**: 5-minute access tokens, 1-day refresh tokens

## Data Models

### User
- UUID primary key
- Extended from AbstractUser
- Extra fields: phone, date_of_birth

### BankAccount
- UUID primary key
- FK to User (max 3 per user)
- Auto-generated 12-digit account number
- Fields: bank_name, account_type, balance, is_active

### Transaction
- UUID primary key
- Auto-generated reference ID (TXN...)
- FK to sender (User), sender_account, receiver_account
- Fields: amount, status, remarks, failure_reason
- Balance snapshots: sender/receiver before/after
