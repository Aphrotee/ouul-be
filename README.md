# Ouul Backend
# App Deployment Guide

## Introduction
This guide provides step-by-step instructions to deploy the Ouul backend application. The deployment process covers setting up the environment, installing dependencies, running the application, and securing the deployment.

## Prerequisites
- Python 3.7+
- Git
- Virtualenv
- Uvicorn (ASGI server)
- PostgreSQL

## 1. Clone the Repository
First, clone the repository from GitHub:

```bash
$ git clone https://github.com/Brandcery/Ouul-backend.git

$ cd /Ouul-backend
```

## 2. Activate the Virtual Environment
```
$ source venv/bin/activate
```

## 3. Install Dependencies
Install the required Python packages using pip:

```
$ pip install -r requirements.txt
```

## 4. Configure Environment Variables
Create/Update the .env file in the root of this project and add necessary environment variables. Here's an example:

```
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

## 5. Create All The Database Tables Required
Run the following script
```
$ ./create_tables.py
```


## 6. Run the Application
To run the FastAPI application using Uvicorn:

```
uvicorn app.main:app --reload
```