# Todo App REST API

A comprehensive Todo application REST API built with Django, featuring dashboard-based organization, tagging, and collaboration. The project follows SOLID principles and object-oriented programming practices.

## Features

- Session-based authentication with Redis storage
- Dashboard organization for todos
- Custom color-coded tags for each dashboard
- Collaboration with role-based access control
- Todo management with priorities, due dates, and status tracking
- Public dashboard sharing with unique links
- Advanced search and filtering capabilities

## Tech Stack

- Django 5.1.7
- Redis 5.0.1 (for session storage)
- SQLite (development database)

## Project Structure

```
django-auth/
├── api/                    # Main API application
│   └── v1/                # API version 1
│       ├── todo/          # Todo functionality
│       │   ├── models/    # Data models
│       │   ├── views/     # View handlers
│       │   ├── services/  # Business logic
│       │   ├── serializers/ # Data serialization
│       │   └── utils/     # Helper utilities
│       └── auth/          # Authentication
├── main/                  # Django project settings
└── manage.py             # Django management script
```

## Setup

1. Clone the repository

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure Redis is running (required for session management):
```bash
redis-server
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the server:
```bash
python manage.py runserver
```

## API Reference

### Authentication API

#### Register a new user
```
POST /api/v1/auth/register/
```
Request body:
```json
{
    "username": "yourusername",
    "password": "yourpassword",
    "email": "your@email.com"
}
```

#### Login
```
POST /api/v1/auth/login/
```
Request body:
```json
{
    "username": "yourusername or your@email.com",
    "password": "yourpassword"
}
```
Note: You can use either your username or email address as the username.

#### Logout
```
POST /api/v1/auth/logout/
```
Authentication: Required

#### Get current user info
```
GET /api/v1/auth/user/
```
Authentication: Required

#### Check session status
```
GET /api/v1/auth/session/
```

### Dashboard API

#### List all dashboards
```
GET /api/v1/todo/dashboards/
```
Authentication: Required

#### Create a dashboard
```
POST /api/v1/todo/dashboards/
```
Authentication: Required

Request body:
```json
{
    "title": "Work Tasks",
    "description": "Tasks related to my job",
    "is_public": false
}
```

#### Get dashboard details
```
GET /api/v1/todo/dashboards/{dashboard_id}/
```
Authentication: Required (unless public dashboard)

#### Update dashboard
```
PUT /api/v1/todo/dashboards/{dashboard_id}/
```
Authentication: Required (dashboard owner only)

Request body:
```json
{
    "title": "Updated Title",
    "description": "Updated description",
    "is_public": true
}
```

#### Delete dashboard
```
DELETE /api/v1/todo/dashboards/{dashboard_id}/
```
Authentication: Required (dashboard owner only)

### Dashboard Members API

#### List dashboard members
```
GET /api/v1/todo/dashboards/{dashboard_id}/members/
```
Authentication: Required (dashboard members)

Response:
```json
{
    "success": true,
    "members": [
        {
            "id": 1,
            "user": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com"
            },
            "role": "owner",
            "joined_at": "2023-03-17T10:30:45.123456Z"
        }
    ]
}
```

#### Add member to dashboard
```
POST /api/v1/todo/dashboards/{dashboard_id}/members/
```
Authentication: Required (dashboard owner only)

Request body:
```json
{
    "email": "colleague@example.com",
    "role": "editor"
}
```
Note: Role must be one of: "editor", "viewer"

Response:
```json
{
    "success": true,
    "id": 2,
    "user": {
        "id": 2,
        "username": "colleague",
        "email": "colleague@example.com"
    },
    "role": "editor",
    "joined_at": "2023-03-18T15:20:30.123456Z"
}
```

#### Update member role
```
PUT /api/v1/todo/dashboards/{dashboard_id}/members/{member_id}/
```
Authentication: Required (dashboard owner only)

Request body:
```json
{
    "role": "viewer"
}
```

#### Remove member from dashboard
```
DELETE /api/v1/todo/dashboards/{dashboard_id}/members/{member_id}/
```
Authentication: Required (dashboard owner only)

### Tags API

#### List dashboard tags
```
GET /api/v1/todo/dashboards/{dashboard_id}/tags/
```
Authentication: Required (dashboard members)

#### Create tag
```
POST /api/v1/todo/dashboards/{dashboard_id}/tags/
```
Authentication: Required (dashboard editors/owner)

Request body:
```json
{
    "name": "Important",
    "color": "#FF5733"
}
```

#### Update tag
```
PUT /api/v1/todo/dashboards/{dashboard_id}/tags/{tag_id}/
```
Authentication: Required (dashboard editors/owner)

Request body:
```json
{
    "name": "Urgent",
    "color": "#FF0000"
}
```

#### Delete tag
```
DELETE /api/v1/todo/dashboards/{dashboard_id}/tags/{tag_id}/
```
Authentication: Required (dashboard editors/owner)

### Todos API

#### List todos in a dashboard
```
GET /api/v1/todo/dashboards/{dashboard_id}/todos/
```
Authentication: Required (dashboard members or public)

Query parameters:
- `status`: Filter by status (`pending` or `completed`)
- `priority`: Filter by priority (1-5)
- `tags`: Filter by tag IDs (comma-separated)
- `sort`: Sort by field (`created_at`, `priority`, `due_date`)
- `order`: Sort order (`asc` or `desc`)

#### Create todo
```
POST /api/v1/todo/dashboards/{dashboard_id}/todos/
```
Authentication: Required (dashboard editors/owner)

Request body:
```json
{
    "title": "Implement feature X",
    "description": "Create the backend for feature X",
    "priority": 4,
    "due_date": "2023-12-31",
    "tags": [1, 3]
}
```

#### Get todo details
```
GET /api/v1/todo/dashboards/{dashboard_id}/todos/{todo_id}/
```
Authentication: Required (dashboard members or public)

#### Update todo
```
PUT /api/v1/todo/dashboards/{dashboard_id}/todos/{todo_id}/
```
Authentication: Required (dashboard editors/owner)

Request body:
```json
{
    "title": "Updated title",
    "description": "Updated description",
    "priority": 5,
    "due_date": "2023-12-15",
    "tags": [2, 4]
}
```

#### Delete todo
```
DELETE /api/v1/todo/dashboards/{dashboard_id}/todos/{todo_id}/
```
Authentication: Required (dashboard editors/owner)

#### Mark todo as complete
```
POST /api/v1/todo/dashboards/{dashboard_id}/todos/{todo_id}/complete/
```
Authentication: Required (dashboard editors/owner)

#### Mark todo as incomplete
```
POST /api/v1/todo/dashboards/{dashboard_id}/todos/{todo_id}/uncomplete/
```
Authentication: Required (dashboard editors/owner)

#### Search todos
```
GET /api/v1/todo/dashboards/{dashboard_id}/todos/search/
```
Authentication: Required (dashboard members)

Query parameters:
- `q`: Search query (required)
- `status`: Filter by status
- `priority`: Filter by priority
- `tags`: Filter by tag IDs (comma-separated)

## Permission System

The API implements a role-based permission system for dashboards:

- **Owner**: Full control over the dashboard, including deletion and member management
- **Editor**: Can create, edit, and delete todos and tags
- **Viewer**: Can only view dashboard contents

## Response Format

All API responses follow a consistent format:

### Success responses:
```json
{
    "success": true,
    "data_field1": "value1",
    "data_field2": "value2"
}
```

### Error responses:
```json
{
    "success": false,
    "error": "Detailed error message"
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200`: Success
- `201`: Resource created successfully
- `400`: Bad request (invalid data)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Resource not found
- `500`: Server error

## Example Workflow

1. Register a user account:
   ```
   POST /api/v1/auth/register/
   {
     "username": "john_doe",
     "password": "secure_password123",
     "email": "john@example.com"
   }
   ```

2. Log in to obtain a session:
   ```
   POST /api/v1/auth/login/
   {
     "username": "john_doe",
     "password": "secure_password123"
   }
   ```

3. Create a dashboard:
   ```
   POST /api/v1/todo/dashboards/
   {
     "title": "Work Projects",
     "description": "Tasks for current work projects",
     "is_public": false
   }
   ```

4. Create tags for the dashboard:
   ```
   POST /api/v1/todo/dashboards/1/tags/
   {
     "name": "Urgent",
     "color": "#FF0000"
   }
   ```

5. Create todos and assign tags:
   ```
   POST /api/v1/todo/dashboards/1/todos/
   {
     "title": "Complete API documentation",
     "description": "Finish the API docs for the Todo app",
     "priority": 4,
     "due_date": "2023-12-31",
     "tags": [1]
   }
   ```

6. Invite team members to collaborate:
   ```
   POST /api/v1/todo/dashboards/1/members/
   {
     "email": "colleague@example.com",
     "role": "editor"
   }
   ```

7. Update todo status as tasks progress:
   ```
   POST /api/v1/todo/dashboards/1/todos/1/complete/
   ```

## Development Guidelines

This project follows SOLID principles and object-oriented programming practices:

1. Single Responsibility Principle: Each class has one job
2. Open/Closed Principle: Open for extension, closed for modification
3. Liskov Substitution Principle: Derived classes must be substitutable for base classes
4. Interface Segregation Principle: Specific interfaces over general ones
5. Dependency Inversion Principle: Depend on abstractions, not concretions

Code standards:
1. Explicit type annotations for all function parameters and return values
2. Small focused functions rather than large complex ones
3. Clear descriptive naming of variables and functions
4. Clean, self-explanatory code without relying on comments 