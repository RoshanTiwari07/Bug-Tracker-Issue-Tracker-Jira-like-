# Testing Guide

This document explains how to run tests for the Bug Tracker backend.

## 📋 Test Coverage

The test suite includes comprehensive tests for all major features:

### 1. **Authentication Tests** (`test_auth.py`)
- ✅ Root endpoint
- ✅ Health check
- ✅ Login with invalid credentials

### 2. **User Tests** (`test_users.py`)
**Registration Tests:**
- ✅ Register new user
- ✅ Register with duplicate email
- ✅ Register with duplicate username

**Login Tests:**
- ✅ Successful login
- ✅ Login with invalid password
- ✅ Login with nonexistent user

**Profile Tests:**
- ✅ Get current user profile
- ✅ Update user profile
- ✅ Access without authentication

**Token Tests:**
- ✅ Refresh access token
- ✅ Token validation

### 3. **Project Tests** (`test_projects.py`)
- ✅ Create project
- ✅ List projects
- ✅ Get specific project
- ✅ Update project
- ✅ Delete project
- ✅ Create without authentication
- ✅ Get nonexistent project

### 4. **Ticket Tests** (`test_tickets.py`)
**CRUD Operations:**
- ✅ Create ticket
- ✅ Get ticket details
- ✅ Update ticket
- ✅ Change ticket status
- ✅ Delete ticket

**Search & Filter:**
- ✅ Search by keyword
- ✅ Filter by priority
- ✅ Filter by status
- ✅ Pagination

### 5. **Comment Tests** (`test_comments.py`)
**Comment Operations:**
- ✅ Add comment to ticket
- ✅ Get all comments
- ✅ Update comment
- ✅ Delete comment
- ✅ Comment without authentication
- ✅ Comment on nonexistent ticket

**Nested Replies:**
- ✅ Reply to comment
- ✅ Threading support

### 6. **Attachment Tests** (`test_attachments.py`)
**File Operations:**
- ✅ Upload file
- ✅ Get ticket attachments
- ✅ Download file
- ✅ Delete file
- ✅ Upload without authentication
- ✅ Upload to nonexistent ticket
- ✅ Multiple file uploads

---

## 🚀 Running Tests

### Run All Tests

```bash
docker-compose exec backend pytest
```

### Run All Tests with Verbose Output

```bash
docker-compose exec backend pytest -v
```

### Run Specific Test File

```bash
# Test authentication
docker-compose exec backend pytest tests/test_auth.py -v

# Test users
docker-compose exec backend pytest tests/test_users.py -v

# Test projects
docker-compose exec backend pytest tests/test_projects.py -v

# Test tickets
docker-compose exec backend pytest tests/test_tickets.py -v

# Test comments
docker-compose exec backend pytest tests/test_comments.py -v

# Test attachments
docker-compose exec backend pytest tests/test_attachments.py -v
```

### Run Specific Test Class

```bash
# Test user registration
docker-compose exec backend pytest tests/test_users.py::TestUserRegistration -v

# Test project creation
docker-compose exec backend pytest tests/test_projects.py::TestProjectManagement -v

# Test ticket search
docker-compose exec backend pytest tests/test_tickets.py::TestTicketSearch -v
```

### Run Specific Test Method

```bash
# Test login success
docker-compose exec backend pytest tests/test_users.py::TestUserLogin::test_login_success -v

# Test create project
docker-compose exec backend pytest tests/test_projects.py::TestProjectManagement::test_create_project -v
```

### Run with Coverage Report

```bash
docker-compose exec backend pytest --cov=app tests/ -v
```

### Run Tests Matching Pattern

```bash
# Run all tests with "create" in the name
docker-compose exec backend pytest -k "create" -v

# Run all authentication tests
docker-compose exec backend pytest -k "auth" -v

# Run all search tests
docker-compose exec backend pytest -k "search" -v
```

### Run with Detailed Output

```bash
docker-compose exec backend pytest -vv --tb=long
```

### Run Last Failed Tests

```bash
docker-compose exec backend pytest --lf
```

### Run Failed Tests First

```bash
docker-compose exec backend pytest --ff
```

---

## 📊 Test Examples

### Example 1: Run All User Tests

```bash
docker-compose exec backend pytest tests/test_users.py -v

# Output:
# test_users.py::TestUserRegistration::test_register_new_user PASSED
# test_users.py::TestUserRegistration::test_register_duplicate_email PASSED
# test_users.py::TestUserLogin::test_login_success PASSED
# test_users.py::TestUserLogin::test_login_invalid_password PASSED
# ...
```

### Example 2: Run Project Creation Test

```bash
docker-compose exec backend pytest tests/test_projects.py::TestProjectManagement::test_create_project -v

# Output:
# test_projects.py::TestProjectManagement::test_create_project PASSED
```

### Example 3: Run with Coverage

```bash
docker-compose exec backend pytest --cov=app tests/ --cov-report=html

# Generates coverage report in htmlcov/index.html
```

### Example 4: Run Specific Test Class

```bash
docker-compose exec backend pytest tests/test_tickets.py::TestTicketSearch -v

# Output:
# test_tickets.py::TestTicketSearch::test_search_by_keyword PASSED
# test_tickets.py::TestTicketSearch::test_search_by_priority PASSED
# test_tickets.py::TestTicketSearch::test_search_by_status PASSED
# test_tickets.py::TestTicketSearch::test_search_with_pagination PASSED
```

---

## 🔍 Understanding Test Structure

Each test file follows this structure:

```python
class TestFeatureName:
    """Test description"""
    
    @pytest.fixture
    def setup(self):
        """Fixture for setup and teardown"""
        # Setup code
        return data
    
    def test_functionality(self, setup):
        """Test description"""
        # Arrange: Setup test data
        # Act: Execute the code
        response = client.post(...)
        
        # Assert: Check results
        assert response.status_code == 201
```

### Common Assertions

```python
# Status codes
assert response.status_code == 200      # Success
assert response.status_code == 201      # Created
assert response.status_code == 204      # No content
assert response.status_code == 400      # Bad request
assert response.status_code == 401      # Unauthorized
assert response.status_code == 403      # Forbidden
assert response.status_code == 404      # Not found

# Response data
data = response.json()
assert data["id"] in data
assert data["username"] == expected_username
assert len(data) > 0
```

---

## 🛠️ Debugging Tests

### View Detailed Test Output

```bash
docker-compose exec backend pytest tests/test_users.py -vv --tb=long
```

### Show Print Statements

```bash
docker-compose exec backend pytest tests/test_users.py -s
```

### Stop at First Failure

```bash
docker-compose exec backend pytest tests/ -x
```

### Drop into Debugger on Failure

```bash
docker-compose exec backend pytest tests/ --pdb
```

---

## ✅ CI/CD Integration

To run tests in CI/CD pipeline:

```bash
#!/bin/bash
# Run tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=xml tests/

# Check coverage is above 80%
coverage report --fail-under=80
```

---

## 📈 Test Statistics

- **Total Test Files:** 6
- **Total Test Classes:** 15+
- **Total Test Methods:** 60+
- **Coverage:** All major endpoints covered

---

## 🎯 Best Practices

1. **Use Fixtures** - Share setup code across tests
2. **Test One Thing** - Each test should verify one behavior
3. **Clear Names** - Test names should describe what is tested
4. **Arrange-Act-Assert** - Follow AAA pattern
5. **Don't Test Implementation** - Test behavior, not code
6. **Mock External Services** - Isolate tests from dependencies

---

## 📞 Troubleshooting

### Tests Fail with Database Error

```bash
# Reset database and retry
docker-compose down -v
docker-compose up -d
docker-compose exec backend pytest tests/
```

### Tests Timeout

```bash
# Increase timeout
docker-compose exec backend pytest tests/ --timeout=30
```

### Import Errors

```bash
# Verify dependencies
docker-compose exec backend pip check

# Rebuild container
docker-compose down
docker-compose up -d --build
```

---

**Status:** All tests ready to run ✅  
**Last Updated:** January 27, 2026
