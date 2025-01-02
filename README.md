# Mito - Django Project Template Generator

Mito comes from the biological term "Mitosis" (cell division). Just as cells divide to create new life, Mito project template helps developers quickly create new Django applications. Each project created by Mito inherits carefully designed best practices while maintaining its own uniqueness.

> Like cell division, one perfect template can create countless excellent projects.

## Why Choose Mito?

- 🧬 **Great Foundation**: Integrates Django development best practices
- 🚀 **Quick Start**: Create a complete project structure in minutes
- 📦 **Ready to Use**: Pre-configured development environment and tools
- 🛠 **Customizable**: Easily adjust project settings as needed

## Design Philosophy

### Frontend-Backend Separation

- 🔄 **API-First Design**: Build standard RESTful APIs with Django REST framework
- 🎯 **Flexible Frontend Integration**: Support Vue.js, React and other modern frontend frameworks
  - Frontend code can be integrated in project's `ui` directory
  - Or managed as separate project communicating via API
- 📚 **API Documentation**: Integrated Swagger UI for interactive API docs

### Asynchronous Processing

- 🚀 **Celery Integration**: Handle time-consuming tasks and background jobs
- ⏰ **Scheduled Tasks**: Task scheduling with Celery Beat
- 📊 **Task Monitoring**: Visualize task execution status and results

### Developer Friendly

- 🛠 **Complete Toolchain**: Pre-configured development, testing and deployment tools
- 📦 **Dependency Management**: Strict dependency management with requirements.txt
- 🔧 **Environment Isolation**: Separate configs for development, testing and production

This architecture provides:

- Better scalability and maintainability
- Clear separation of concerns  
- Flexible technology choices
- Powerful async processing capabilities

## Running in Production

The easiest way to get started is by using Docker Compose:

1. Clone the repository (you can rename the project to whatever you prefer, for instance, your_new_project):

   ```bash
   git clone https://github.com/xiaoquqi/django-starter-template.git your_new_project
   cd your_new_project
   ```

2. Copy the environment configuration file:

   ```bash
   cp .env.sample .env
   ```

### CSRF_TRUSTED_ORIGINS

- This setting defines the trusted domains for CSRF verification.
- In a production environment, you must include the domain of your admin portal to ensure proper access.

- Use a comma-separated list of trusted domains. For example:

   ```bash
   export CSRF_TRUSTED_ORIGINS=https://admin.example.com,https://api.example.com
   ```

3. Start the services:

   ```bash
   docker-compose up -f docker-compose.prod.yaml -d
   ```

4. Access the services:
   - Swagger API Documentation: http://localhost/swagger/
   - Admin Interface: http://localhost/admin/
       - Default username and password: admin/adminpassword
   - Flower(Celery Task Management): http://localhost:81/

### Containers

| Containers         | Description                                      |
|--------------------|--------------------------------------------------|
| mito-api           | The main Django application for handling requests and serving the API. |
| mito-worker        | A Celery worker for processing background tasks asynchronously. |
| mito-scheduler     | A Celery scheduler for managing periodic tasks.  |
| mito-nginx         | Nginx server for serving static files and acting as a reverse proxy. |
| mito-mariadb       | MariaDB database service for storing application data. |
| mito-redis         | Redis service for caching and message brokering. |
| mito-flower        | A web-based tool for monitoring and managing Celery tasks. |

## Developer Quick Guide

You can use this project as a foundation for developing new applications. I have created a simple starter app based on useful Django modules, and you are welcome to modify anything as you see fit. I will highlight the modifications to help you quickly set up a new project.

### Building the Development Environment

It is recommended to use an IDE with AI enhancements, such as VS Code with Copilot, Cursor, WindSurf, or any other tool you prefer. We are in the era of AI, so embrace it and become the master of AI.

1. Clone the repository (you can rename the project to anything you like, for example, your_new_project):

   ```bash
   git clone https://github.com/xiaoquqi/django-starter-template.git your_new_project
   cd your_new_project
   ```

2. Create and activate a virtual environment:

   ```bash
   virtualenv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database and create a superuser:

   ```bash
   export DJANGO_DEBUG=True

   python manage.py migrate

   # Create a superuser
   python manage.py createsuperuser --username admin --email admin@example.com
   # You will be prompted to enter a password
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the services:
   - Swagger API Documentation: http://localhost:18080/swagger/
   - Admin Interface: http://localhost:18080/admin/
       - Default username and password: admin/adminpassword
   - Flower(Celery Task Management): http://localhost:18081/

## Django Code Structure

All the Django code is located in the api directory, which is generated by the django-admin startproject command. Therefore, all backend development is conducted within this directory.

### Django Project Structure

```
api                          // The main application directory containing all project-related files.
├── accounts                 // Directory for user account management and authentication.
├── core                     // Django project directory, contains all settings.
│   ├── asgi.py              // ASGI configuration for asynchronous support.
│   ├── celery.py            // Configuration for Celery task management.
│   ├── __init__.py          // Initializes the core package.
│   ├── settings             // Directory containing various settings for the application.
│   │   ├── base.py          // Base settings for the Django project.
│   │   ├── celery.py        // Celery-specific settings.
│   │   ├── __init__.py      // Initializes the settings package.
│   │   ├── logging_config.py // Configuration for logging in the application.
│   │   ├── rest.py          // Settings specific to Django REST framework.
│   │   └── swagger.py       // Configuration for Swagger API documentation.
│   ├── swagger.py           // Main Swagger configuration for the application.
│   ├── urls.py              // URL routing for the core application.
│   └── wsgi.py              // WSGI configuration for serving the application.
├── docker                   // Directory for Docker-related files.
├── Dockerfile               // Instructions for building the Docker image.
├── locale                   // Directory for localization files.
├── manage.py                // Command-line utility for managing the Django project.
├── tests                    // Directory containing test cases for the application.
└── v1                       // Version 1 of the API.
    └── sample               // Sample Django application
```

### Django Project Settings

This project is slightly different from a standard Django project. I have split the settings into several parts, allowing you to add or modify options based on your requirements.

#### How to add a new setting?

If you want to add configurations that may change depending on the environment, it is recommended to use environment variables. I have already set up automatic loading of the .env file located in the project's base directory. You can copy the .env.sample file to .env before starting development.

To add new environment variables in a Django project and configure them at startup, follow these steps:

1. Update the `.env.sample` File

First, define the new environment variable in the `.env.sample` file. For example, if you want to add a variable named `NEW_VARIABLE`, you can do it like this:

2. Load the new environment variable in base.py: Next, you need to load this new environment variable in the api/core/settings/base.py file. You can use the os.getenv() function to retrieve the value of this variable.

``` python
# ... existing code ...

# New environment variable
NEW_VARIABLE = os.getenv("NEW_VARIABLE", "default_value")  # Set default value

# ... existing code ...
```

3. Use the new environment variable in the code: Now, you can use this new environment variable in other parts of the project. For example, you can use it in views, models, or other settings.

``` python
from django.http import JsonResponse
from django.conf import settings

def example_view(request):
    # Use your new environment here
    new_variable_value = settings.NEW_VARIABLE
    return JsonResponse({"new_variable": new_variable_value})
```

4. Ensure that the .env file is loaded at startup: Make sure to load the .env file when the project starts so that the new environment variables can be read correctly. You have already used load_dotenv(ENV_DIR) in base.py to load the environment variables, ensuring that the new variables are read at startup. 

By following these steps, you can successfully add new environment variables and use them in your Django project.

## Authentication

### JWT

In this project, JWT (JSON Web Token) is used as the default authentication method. JWT allows you to securely transmit information between parties as a JSON object. 

#### How to use JWT?

1. **Normal Authentication**: To authenticate a user, send a POST request to the `/api/v1/auth/token/` endpoint with the user's credentials (username and password). If the credentials are valid, you will receive an access token and a refresh token.

   Example request:

   ```http
   POST /api/v1/auth/token/
   Content-Type: application/json

   {
       "username": "your_username",
       "password": "your_password"
   }
   ```

   Example response:

   ```json
   {
       "access": "your_access_token",
       "refresh": "your_refresh_token"
   }
   ```

2. **Refreshing the Token**: When the access token expires, you can obtain a new access token by sending a POST request to the `/api/v1/token/refresh/` endpoint with the refresh token.

   Example request:

   ```http
   POST /api/v1/token/refresh/
   Content-Type: application/json

   {
       "refresh": "your_refresh_token"
   }
   ```

   Example response:
   ```json
   {
       "access": "your_new_access_token"
   }
   ```

By following these steps, you can effectively use JWT for authentication and token management in this project.

### About `accounts`

By default, all user authentication and authorization operations should be placed in the accounts directory. The accounts directory contains a standard Django application that implements a profile, establishing a one-to-one relationship with the default Django user module to extend user capabilities. Here is the structure of the accounts directory.

```
api
├── accounts
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
```

## Django Application

### Why We Have a v1 Directory

In actual development, as features continue to iterate and update, the API interfaces will also change with the increasing demands. Therefore, we have added a v1 directory in the app to accommodate the needs for future version development and iteration. This structure allows us to manage different versions of the API effectively, ensuring backward compatibility while enabling the introduction of new features and improvements in subsequent versions.

### Sample Application

In the `api/v1/sample` directory, you will find a complete example of a Django application that implements a blogging system.

This sample application contains a simple blog data structure, including posts, tags, and categories. Posts and tags have a many-to-many relationship, while posts and categories have a one-to-many relationship. You can also create a new post with new tags and categories, and the overridden create method will function in the serializers.py file. You can use this application as a sample and develop new applications according to your requirements.

You can test the interface on the Swagger page and find more details in the code.

### Create a new App

To create a new app under the `v1` directory in your Django project, follow these steps:

1. Open your terminal and navigate to the root directory of your Django project.

2. Run the following command to create a new app (replace `your_new_app` with the desired app name):

   ```bash
   python manage.py startapp v1/your_new_app
   ```

3. After the app is created, you will need to add it to your project's settings. Open `api/core/settings/base.py` and add the new app to the `INSTALLED_APPS` list:

   ```python
   INSTALLED_APPS = [
       ...
       'v1.your_new_app',
       ...
   ]
   ```

4. Now, you can start defining your models, views, and serializers in the newly created app directory (`v1/your_new_app`).

5. Don't forget to create migrations for your models and apply them:

   ```bash
   python manage.py makemigrations v1/your_new_app
   python manage.py migrate
   ```

6. Finally, you can start developing your API endpoints in the `views.py` file of your new app.

By following these steps, you can effectively create and set up a new app under the `v1` directory in your Django project.

## Project Modules

This list contains the modules that already exist in this project.

| Module Name                        | Description                                                                                     |
|------------------------------------|-------------------------------------------------------------------------------------------------|
| Django                             | The core framework for building web applications.                                              |
| Django REST framework              | A framework for building RESTful APIs.                                                         |
| djangorestframework_simplejwt      | Extension for JWT authentication support in Django REST framework.                             |
| djangorestframework-camel-case     | Provides JSON renderers and parsers that convert between camelCase and snake_case.            |
| dj-rest-auth                       | Extension for user authentication and registration.                                            |
| drf-yasg                           | Tool for generating Swagger UI for APIs.                                                      |
| dj-rest-auth[with_social]         | DJ-REST-AUTH extension with social authentication support.                                     |
| python-dotenv                      | Library for loading environment variables from .env files.                                     |
| dj_database_url                    | Library for parsing database URLs.                                                             |
| celery                             | Framework for asynchronous task queues.                                                         |
| django-celery-beat                | Extension for scheduling periodic tasks in Django.                                             |
| flower                             | Tool for real-time monitoring of Celery tasks.                                                |
| gunicorn                           | WSGI server for running the application in production.                                         |
