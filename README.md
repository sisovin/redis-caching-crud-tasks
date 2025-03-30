# Redis Caching CRUD Tasks

A full-stack application demonstrating Redis caching with Django REST API and Vue.js frontend for efficient task management.

![Redis Caching](https://img.shields.io/badge/Redis-Caching-red)
![Django](https://img.shields.io/badge/Backend-Django-green)
![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-blue)

## Project Overview

This project demonstrates how to implement Redis caching in a Django REST API with a Vue.js frontend. The application allows users to create, read, update, and delete tasks while utilizing Redis for efficient data caching and retrieval.

## Features

- **Task Management**: Create, read, update, and delete tasks
- **Redis Caching**: Improve performance with in-memory data caching
- **Memoization**: Function-level caching for expensive operations
- **Cache Expiration**: Automatic invalidation of stale data
- **Stateless Architecture**: Separate caching from primary storage

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: Vue.js, Axios
- **Caching**: Redis
- **Documentation**: Swagger/OpenAPI

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm
- Redis server

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sisovin/redis-caching-crud-tasks.git
   cd redis-caching-crud-tasks
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux or macOS
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the Django server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Access the application at `http://localhost:3000`

## Full Project Structure

Below is structure with multiple Django apps, user authentication, advanced Redis caching strategies, and proper testing setup without relying on Docker. Here's the recommended structure:

```
redis-caching-crud-tasks/
├── backend/
│   ├── config/                     # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings/               # Split settings
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Common settings
│   │   │   ├── development.py      # Dev-specific settings
│   │   │   └── production.py       # Prod-specific settings
│   │   ├── urls.py                 # Root URL routing
│   │   └── wsgi.py
│   ├── task_manager/               # Tasks app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── accounts/                   # User authentication app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core/                       # Shared functionality
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── cache/                  # Centralized caching
│   │   │   ├── __init__.py
│   │   │   ├── backends.py         # Custom cache backends
│   │   │   ├── decorators.py       # Cache decorators
│   │   │   ├── patterns.py         # Caching patterns
│   │   │   └── utils.py            # Redis utilities
│   │   └── middleware/             # Custom middleware
│   ├── tests/                      # Top-level tests
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── test_caching.py         # Caching tests
│   │   └── test_integration.py     # Cross-app tests
│   ├── manage.py
│   ├──swagger.yaml
│   ├──postman.json
│   └── requirements/               # Split requirements
│       ├── base.txt                # Common dependencies
│       ├── dev.txt                 # Development dependencies
│       └── prod.txt                # Production dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/             # Shared components
│   │   │   ├── tasks/              # Task components
│   │   │   └── auth/               # Auth components
│   │   ├── services/
│   │   │   ├── api.js              # Base API config
│   │   │   ├── auth.service.js     # Auth API calls
│   │   │   └── tasks.service.js    # Tasks API calls
│   │   ├── store/                  # Vuex store modules
│   │   │   ├── index.js
│   │   │   ├── auth.module.js
│   │   │   └── tasks.module.js
│   │   ├── views/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── router.js
│   ├── .env.development            # Environment variables
│   ├── .env.example                # Example environment variables
│   ├── package.json
│   └── vue.config.js
├── scripts/                        # Helper scripts
│   ├── setup_dev.py                # Development setup script
│   └── reset_cache.py              # Cache management utility
├── .gitignore
└── README.md
```

## Redis Caching Implementation

### 1. Introduction to Redis and Its Main Purpose

Redis is an open-source, in-memory data structure store used as a database, cache, and message broker. It supports various data structures such as strings, hashes, lists, sets, and more. Redis enhances performance by storing data in memory, allowing for faster data retrieval compared to traditional disk-based databases. In our Django REST API, Redis caches frequently accessed data, reducing database load and improving response times.

### 2. Memoization - Function-Level Caching

Memoization caches the results of expensive function calls and returns the cached result when the same inputs occur again. This significantly improves the performance of functions that are called frequently with the same arguments. Our implementation uses Redis to store these cached results, making repeated API calls much faster.

### 3. Using Redis for Caching Database Queries in API Calls

Caching database queries greatly improves API call performance by reducing database hits. By storing query results in Redis, we can quickly retrieve the cached data for subsequent requests, reducing database load and improving response times.

### 4. Caching with Redis for Efficient Data Retrieval and Expiration

Redis allows us to set expiration times for cache entries, ensuring stale data is automatically invalidated. This maintains the freshness of cached data and prevents serving outdated information. Our implementation configures Redis to automatically remove expired cache entries, making it an efficient caching solution.

### 5. Storing Data in a Separate Store for Statelessness

Separating caching from primary storage helps maintain statelessness in the application. By storing cached data in Redis, we ensure the application remains stateless and can scale horizontally without issues. This also allows for better management of cached data, as it is stored separately from the primary database.

## API Documentation

The API is documented using Swagger/OpenAPI. You can access the documentation at `http://localhost:8000/swagger/` when the backend server is running.

## Frontend Components

- **TaskForm**: Component for creating new tasks
- **TaskList**: Component for displaying the list of tasks
- **TaskItem**: Component for displaying individual task details

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

sisovin - [GitHub Profile](https://github.com/sisovin)

Project Link: [https://github.com/sisovin/redis-caching-crud-tasks](https://github.com/sisovin/redis-caching-crud-tasks)


This project provides comprehensive information about your project, its architecture, setup instructions, and key features. It's well-structured and includes badges to make it visually appealing on GitHub.
