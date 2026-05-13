You are an expert Django backend engineer helping me build a complete mini payment system project. The final output should look like a genuine student-built project: clean, practical, well-structured, and easy for me to explain in viva/interview. Keep the implementation original, simple enough to understand, but advanced enough to look professional.

Project Goal:
Build a secure payment system using Django and Django REST Framework that demonstrates API design, authentication, database relationships, validation, transaction handling, and business logic.

Core Requirements:
1. User APIs
- Create User
- Update User
- Delete User
- Get User Profile
- Get Users List

2. Authentication APIs
- Login user and return access token + refresh token
- Refresh token to generate a new access token
- Access token expiry: 5 minutes
- Refresh token expiry: 1 day

3. Bank Account APIs
- Add user bank account
- Get user bank accounts list
- Delete user bank account
- Top up user bank account balance
- Each user can have a maximum of 3 bank accounts

4. Payment APIs
- Do payment
- Get transactions list by user

Payment Rules:
- If payment is successful, deduct amount from sender account, add amount to receiver account, and create a transaction record with status SUCCESS.
- If payment fails due to insufficient balance, invalid account, invalid user, missing data, or any business rule violation, create a transaction record with status FAILED.
- Payment operations must be atomic and safe from partial updates.

Implementation Stack:
- Django
- Django REST Framework
- PostgreSQL or SQLite for development
- Simple JWT for authentication
- Django admin for managing data
- drf-yasg or Swagger/OpenAPI for API docs if possible
- pytest or Django test framework for tests

What I want you to build:
- A complete Django project structure with apps separated logically, such as:
  - accounts
  - banking
  - payments
  - core/common utilities if needed
- Custom user model from the start
- Serializer-based validation
- JWT authentication setup
- Permissions and access control
- Database models for:
  - User
  - BankAccount
  - Transaction
- Strong business logic in services or helper functions
- Clean API views using DRF ViewSets or APIViews where appropriate
- Proper URL routing
- Error responses with meaningful messages
- Code that is organized like a real project, not a single-file demo

Data Model Expectations:
- User model should store basic profile information
- BankAccount should belong to a user
- Enforce maximum 3 bank accounts per user
- Transaction should store sender account, receiver account, amount, timestamp, and status
- Add useful fields such as reference ID, balance snapshots, or remarks if needed
- Use model constraints, indexes, and validation where helpful

Business Logic Expectations:
- Login returns access and refresh tokens
- Refresh endpoint issues a new access token
- Add bank account should fail gracefully if user already has 3 accounts
- Top-up should increase balance only for the authenticated user's account
- Payment should:
  - verify sender owns the account
  - verify receiver account exists
  - verify sufficient balance
  - update both balances inside a database transaction
  - create a transaction record every time
  - never allow inconsistent balance updates
- Handle edge cases carefully

Security and Quality Expectations:
- Use JWT authentication properly
- Protect user-specific endpoints
- Do not expose sensitive data unnecessarily
- Add permission checks
- Use Django transactions.atomic() for money transfer logic
- Avoid race conditions where possible
- Validate all input data carefully
- Return proper HTTP status codes

Deliverables I want from you:
1. Full project architecture
2. Django app structure
3. Models with fields and relations
4. Serializers
5. Views
6. URLs
7. Authentication setup
8. Business logic/services
9. Admin configuration
10. Sample request and response JSON for each API
11. Test cases for main flows
12. README-style setup steps
13. Optional Swagger documentation setup

Style Requirements:
- Keep code readable, modular, and realistic
- Use clear variable names
- Add only useful comments
- Make it look like I wrote it myself for a college project
- Do not make it look overly generic or obviously AI-generated
- Avoid unnecessary complexity
- Prefer practical code over fancy patterns
- Keep explanations short but complete

Important Constraints:
- Use Django REST Framework properly
- Use a custom user model
- Ensure all money transfer logic is transactional
- Enforce the 3 bank account limit
- Make the project easy to run locally


