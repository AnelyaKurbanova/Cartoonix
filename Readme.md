# **Cartoonix**

Сreating a social network integrated with the capabilities of artificialintelligence (AI) to generate multimedia content.


---

## **📋 Prerequisites**

Before starting, ensure you have the following installed:
-  **Python 3.11.x**
-  **pip** (Python package manager)
-  **Virtualenv**
-  **Redis**

---

## **Installation Steps**

### **1. Clone the Repository**
Clone the repository and navigate into the project folder:
```bash
git clone https://github.com/AnelyaKurbanova/Cartoonix.git
cd project
```

### **2. Set Up a Virtual Environment**
Create and activate a virtual environment :
```bash
python -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**
Install the required Python packages :
```bash
pip install -r requirements.txt
```


### **4. Install and Configure Redis**
Install the required Python packages :
For Linux/macOS:
```bash
sudo apt update
sudo apt install redis
sudo systemctl start redis
sudo systemctl enable redis
```
Verify Redis is running:
```bash
redis-cli ping
```

Expected output: PONG.


## **Database setup**
### **1. Apply Migrations**
Set up the database schema:
```bash
python manage.py migrate
```

### **2. Create a Superuser**
Set up the database schema:
```bash
python manage.py createsuperuser
```


## **Running the Project**

### **1. Start the Development Server**
Run the Django server:
```bash
python manage.py runserver
```

### **2.  Start Celery Workers**
Run Celery workers to handle background tasks:
```bash
celery -A cartoonix worker --loglevel=info
```




## **Logging and Troubleshooting**
### **1. Logging**

```bash
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_api': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/api_access.log'),
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'api_logger': {
            'handlers': ['file_api', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'error_logger': {
            'handlers': ['file_error', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

```

### **2.  Redis Troubleshooting**
Check if Redis is running:
```bash
redis-cli ping
```

If Redis is not running:
```bash
sudo systemctl start redis
```

## **API Documentation**

This project includes a Swagger UI for exploring the API endpoints.

### **Access Swagger**
After running the server, open your browser and navigate to:

[http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)

















