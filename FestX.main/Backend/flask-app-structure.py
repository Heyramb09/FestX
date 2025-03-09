# Project Structure
fest_management/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── static/                # Static files (CSS, JS, images)
├── templates/             # Jinja2 templates
│   ├── base.html          # Base template
│   ├── auth/              # Authentication templates
│   ├── events/            # Event templates
│   ├── admin/             # Admin panel templates
│   ├── discussion/        # Discussion forum templates
│   ├── contact/           # Contact & FAQ templates
│   └── about/             # About page templates
└── app/                   # Application package
    ├── __init__.py        # Initialize app and extensions
    ├── models.py          # Database models
    ├── forms.py           # Form definitions
    ├── utils.py           # Utility functions
    ├── auth/              # Authentication blueprint
    │   ├── __init__.py
    │   ├── routes.py
    │   └── forms.py
    ├── events/            # Events blueprint
    │   ├── __init__.py
    │   ├── routes.py
    │   └── forms.py
    ├── admin/             # Admin blueprint
    │   ├── __init__.py
    │   ├── routes.py
    │   └── forms.py
    ├── discussion/        # Discussion blueprint
    │   ├── __init__.py
    │   ├── routes.py
    │   └── forms.py
    ├── contact/           # Contact blueprint
    │   ├── __init__.py
    │   ├── routes.py
    │   └── forms.py
    └── about/             # About blueprint
        ├── __init__.py
        └── routes.py
