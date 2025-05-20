## Library Management System API

A Django REST Framework-based API that supports book borrowing, returning, inventory tracking, and late return penalties.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/library-api.git
cd library-api
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

---

## API Authentication

Use token-based authentication. Get a token using the `/api/token/` endpoint (if implemented), or use session login via Django admin.

---

## Key Features

### Borrowing Logic (`POST /api/borrow/`)

* A user can borrow a book by providing `book_id`.
* The system:

  * Ensures the user has **less than 3 active borrows**.
  * Ensures the book has **available copies**.
  * Reduces the book’s `available_copies` by 1.
  * Creates a `Borrow` record with:

    * `borrow_date` = today
    * `due_date` = 14 days from today
* All operations are **atomic** to prevent race conditions.

### Returning Logic (`POST /api/return/`)

* A user returns a book by providing `borrow_id`.
* The system:

  * Sets `return_date` to today.
  * Increments `available_copies` by 1.
  * Checks if the return is **late**:

    * If so, calculates how many days late.
    * Adds **1 penalty point per late day** to the user's profile.

### Penalty Check (`GET /api/users/{id}/penalties/`)

* Shows total accumulated penalty points for a user.
* Only viewable by the user themself or an admin.

---

## Penalty Points Calculation

```python
late_days = (return_date - due_date).days
penalty_points += late_days  # 1 point per late day
```

Only applied when a book is returned **after** its due date.

---

## Assumptions & Known Limitations

* Timezone handling is simplified using Django defaults (UTC).
* Borrow and return operations are **atomic**, avoiding race conditions with inventory.
* **Borrowing back-dates cannot be changed via API**.
* **No automatic overdue scanning** — penalties are applied only at the time of return.

---

## Testing

* You can test endpoints using Postman or the Django admin panel.
* Sample data can be added via Django admin or fixtures.
* For testing overdue penalties, modify `borrow_date` and `due_date` using:

  * Admin panel (if allowed)
  * Custom API in test mode
  * Management script (`python manage.py shell`)


