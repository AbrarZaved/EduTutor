# Django Project Template with Authentication

A production-ready Django project template featuring a complete JWT-based authentication system with OTP support and asynchronous email handling via Celery. This template is designed to be reusable across multiple client projects with minimal configuration.

## Features

- ✅ **Custom User Model** - Email-based authentication (no username)
- ✅ **JWT Authentication** - Using `djangorestframework-simplejwt`
- ✅ **User Registration** - With email verification
- ✅ **Login / Logout** - Token-based sessions
- ✅ **Password Reset** - OTP-based forgot password flow
- ✅ **Profile Management** - View and update user profile
- ✅ **Password Change** - With OTP verification option
- ✅ **Celery Integration** - Asynchronous email sending with Redis
- ✅ **Background Tasks** - All emails sent as background jobs
- ✅ **Configurable Features** - Enable/disable auth features via settings
- ✅ **Service-Layer Architecture** - Clean separation of concerns
- ✅ **Production-Ready** - Logging, CORS, throttling configured

## Quick Start

### Using as a Django Template

Create a new project using this template:

```bash
django-admin startproject myproject --template=https://github.com/AbrarZaved/django-project-snippet/archive/main.zip --extension=py,md,txt,env --name=.gitignore,.env.example
```

Or clone and use directly:

```bash
# Clone the repository
git clone https://github.com/AbrarZaved/django-project-snippet.git myproject
cd myproject

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Redis (required for Celery)
redis-server

# Run Celery worker (in a separate terminal)
celery -A EduTutor worker --loglevel=info --pool=solo

# Run development server
python manage.py runserver
```

> **Note**: For Celery to work, you need to run Redis and the Celery worker. See [CELERY_SETUP.md](CELERY_SETUP.md) for detailed instructions.

## Project Structure

```
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── CELERY_SETUP.md              # Celery setup guide
├── IMPLEMENTATION_SUMMARY.md    # Implementation details
├── test_celery.py               # Celery test script
├── start_celery.sh              # Quick start script
├── EduTutor/                    # Main project directory
│   ├── __init__.py              # Celery app initialization
│   ├── settings.py              # Django + Celery settings
│   ├── celery.py                # Celery configuration
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core_auth/                   # Authentication app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── exceptions.py
│   ├── models.py                # User, OTPToken
│   ├── permissions.py           # Custom permission classes
│   ├── serializers.py           # DRF serializers
│   ├── services.py              # Business logic layer
│   ├── tasks.py                 # Celery email tasks
│   ├── tokens.py                # JWT token utilities
│   ├── urls.py                  # URL routing
│   ├── views.py                 # API views
│   ├── migrations/
│   └── tests/
│       ├── test_models.py
│       ├── test_views.py
│       └── test_services.py
├── static/
├── media/
├── templates/
└── logs/
```

## Configuration

### Authentication Features

Configure authentication features in `settings.py` or via environment variables:

```python
AUTH_FEATURES = {
    # Authentication method: "JWT" or "SESSION"
    "AUTH_METHOD": "JWT",

    # Enable/disable password reset functionality
    "ENABLE_PASSWORD_RESET": True,

    # Enable/disable profile editing functionality
    "ENABLE_PROFILE_EDIT": True,

    # OTP expiry time in minutes
    "OTP_EXPIRY_MINUTES": 10,

    # OTP length
    "OTP_LENGTH": 6,
}
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Authentication Features
AUTH_METHOD=JWT
ENABLE_PASSWORD_RESET=True
ENABLE_PROFILE_EDIT=True
OTP_EXPIRY_MINUTES=10
OTP_LENGTH=6

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

# Email (for OTP delivery)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@example.com

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgres://user:password@localhost:5432/dbname

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## API Endpoints

### Authentication

| Endpoint                   | Method | Description              | Auth Required |
| -------------------------- | ------ | ------------------------ | ------------- |
| `/api/auth/register/`      | POST   | Register new user        | No            |
| `/api/auth/login/`         | POST   | Login and get tokens     | No            |
| `/api/auth/logout/`        | POST   | Logout (blacklist token) | Yes           |
| `/api/auth/token/refresh/` | POST   | Refresh access token     | No            |
| `/api/auth/token/verify/`  | POST   | Verify token validity    | No            |

### Profile

| Endpoint                    | Method    | Description      | Auth Required |
| --------------------------- | --------- | ---------------- | ------------- |
| `/api/auth/profile/`        | GET       | Get user profile | Yes           |
| `/api/auth/profile/update/` | PUT/PATCH | Update profile   | Yes           |

### Password Management

| Endpoint                                 | Method | Description                     | Auth Required |
| ---------------------------------------- | ------ | ------------------------------- | ------------- |
| `/api/auth/password/change/`             | POST   | Change password (knows current) | Yes           |
| `/api/auth/password/change/otp/request/` | POST   | Request OTP for password change | Yes           |
| `/api/auth/password/change/otp/verify/`  | POST   | Verify OTP and change password  | Yes           |
| `/api/auth/password/reset/request/`      | POST   | Request password reset OTP      | No            |
| `/api/auth/password/reset/verify/`       | POST   | Verify OTP and reset password   | No            |
| `/api/auth/password/reset/link/request/` | POST   | Request password reset link     | No            |
| `/api/auth/password/reset/link/verify/`  | POST   | Reset password with token       | No            |

### Email Verification

| Endpoint                          | Method | Description                    | Auth Required |
| --------------------------------- | ------ | ------------------------------ | ------------- |
| `/api/auth/email/verify/request/` | POST   | Request email verification OTP | Yes           |
| `/api/auth/email/verify/confirm/` | POST   | Verify email with OTP          | Yes           |

## Request/Response Examples

### Register

**Request:**

```json
POST /api/auth/register/
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**

```json
{
  "message": "Registration successful. Please verify your email.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "is_email_verified": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Login

**Request:**

```json
POST /api/auth/login/
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "is_email_verified": false
  }
}
```

### Password Reset (OTP-based)

**Step 1 - Request OTP:**

```json
POST /api/auth/password/reset/request/
{
    "email": "user@example.com"
}
```

**Step 2 - Verify OTP and Reset:**

```json
POST /api/auth/password/reset/verify/
{
    "email": "user@example.com",
    "otp": "123456",
    "new_password": "NewSecurePass123!",
    "confirm_password": "NewSecurePass123!"
}
```

## JWT Setup

### Using Access Token

Include the access token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Token Refresh

When the access token expires, use the refresh token to get a new access token:

```json
POST /api/auth/token/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token Configuration

Configure token lifetimes in `.env`:

```env
JWT_ACCESS_TOKEN_LIFETIME=60     # minutes
JWT_REFRESH_TOKEN_LIFETIME=7     # days
```

## Enabling/Disabling Features

### Disable Password Reset

```env
ENABLE_PASSWORD_RESET=False
```

This will:

- Return 403 Forbidden on password reset endpoints
- Hide password reset functionality

### Disable Profile Edit

```env
ENABLE_PROFILE_EDIT=False
```

This will:

- Return 403 Forbidden on profile update endpoints
- Return 403 on password change endpoints

## Architecture

This template follows a **service-layer architecture**:

1. **Views** (`views.py`) - Handle HTTP requests/responses, thin logic
2. **Serializers** (`serializers.py`) - Data validation and transformation
3. **Services** (`services.py`) - Business logic, database operations
4. **Models** (`models.py`) - Data models and model-level methods
5. **Permissions** (`permissions.py`) - Access control

### Key Services

- `UserService` - User CRUD operations
- `TokenService` - JWT token generation/blacklisting
- `AuthenticationService` - Login/logout logic
- `OTPService` - OTP generation and verification
- `PasswordService` - Password change operations
- `PasswordResetService` - Password reset flow
- `EmailVerificationService` - Email verification
- `EmailService` - Email sending

## Testing

Run tests:

```bash
python manage.py test core_auth
```

Run with coverage:

```bash
pip install coverage
coverage run manage.py test core_auth
coverage report
```

## Production Deployment

### Checklist

1. Set `DEBUG=False`
2. Generate a new `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up PostgreSQL database
5. Configure email backend (SMTP)
6. Set up HTTPS
7. Configure CORS origins
8. Review throttling rates

### Example Production Settings

```env
DEBUG=False
SECRET_KEY=your-very-secure-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@db.host:5432/proddb
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and feature requests, please use the GitHub issue tracker.
