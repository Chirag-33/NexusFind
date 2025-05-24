# NexusFind
NexusFind is an e-commerce platform built with Django and PostgreSQL. It enables users to browse products, add items to a cart, make purchases, and manage their profiles. The platform supports user authentication, product management, and a seamless shopping experience with a responsive interface.

## Features
- User authentication (Sign Up, Sign In, Sign Out).
- Product browsing and search functionality.
- Shopping cart and checkout process.
- Order history and user profile management.
- Admin panel for managing products and orders.
- Responsive frontend styled with Tailwind CSS.

## Usage:
### Basic setup and dependency management:
- Install `pipenv`:
```bash
pip install pipenv
```

- Activate the Virtual Environment:
```bash
pipenv shell
```

- Install required libraries from the `Pipfile.lock`:
```bash
pipenv install
```

OR

- Using pre-installed "venv" to create Virtual Environment:
```bash
python -m venv .venv
```

- Activate the Virtual Environment:
```bash
.venv/Scripts/activate.ps1
```

- Install all requirements from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Pre-requisites:
- Update the `.env` file with necessary configurations (e.g., `SECRET_KEY`, `DB_NAME` for PostgreSQL).
- PostgreSQL installed and running, with a database created for the project.
- Run migrations to set up the PostgreSQL database:
```bash
python manage.py migrate
```

### To run the code:
- Run the Django server:
```bash
python manage.py runserver
```

- Access the application at `http://127.0.0.1:8000/` in your browser.

## Description about various files:
- **manage.py**: Django's command-line utility for managing the project.
- **NexusFind**:
    - **settings.py**: Contains Django project settings, including PostgreSQL database configuration, authentication, and app settings.
    - **urls.py**: Defines URL patterns for the project, routing to views in the apps.
    - **wsgi.py**: Provides WSGI configuration for production deployment.
    - **asgi.py**: Supports ASGI-compatible servers for asynchronous features.

- **App Structure**:
  - **views.py**: Handles logic for respective feature.
  - **urls.py**: Maps URLs for their respective views.
  - **models.py**: Defines database schema for users, products, orders, carts,etc.

- **templates**: Contains HTML files for rendering the UI, including pages for product listings, cart, checkout, and user profiles, styled with Tailwind CSS.
- **static**: Stores static assets like CSS, JavaScript, and images, including Tailwind CSS configurations.
- **Pipfile**: Specifies project dependencies in a structured format.
- **Pipfile.lock**: Locks dependency versions for consistent environments.
