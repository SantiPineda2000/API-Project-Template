# API Project Template

Welcome to my project 📁, his project is the core of a bigger application, intended to be used as a template. I am also using this project to learn please leave any recommendations.

📓 I tried following the best practices described in this [Repository](https://github.com/zhanymkanov/fastapi-best-practices?tab=readme-ov-file#project-structure).

🌟 Based on the project from Tiangolo's [Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/api/routes/login.py).

## Setup instructions

To setup locally please follow the following steps

1. Install `Postgresql` locally or in a docker container and add the following credentials in the `.env` file:

   ```
   # Postgres
   POSTGRES_SERVER= <Your_host_name>
   POSTGRES_PORT= <Available_post>
   POSTGRES_DB= <Your_database>
   POSTGRES_USER= <Your_user>
   POSTGRES_PASSWORD= <Your_password>
   ```

2. Install the `libpq` package.

   **For Mac:**

   First install the package globally, using:

   ```
    brew install libpq
   ```

   After installing, link the library so it's available system-wide, with:

   ```
    brew link libpq --force
   ```

   **For Linux:**

   ```
   sudo apt-get install libpq-dev  # Debian/Ubuntu
   sudo dnf install postgresql-libs  # Fedora
   ```

   **For Windows:**

   ```
      !!! Please research and add the steps here !!!
   ```

3. Create a virtual environment `./venv/` in the base directoty and activate it.

   **For Mac or Linux:**

   Create and then run the environment, using:

   ```
    python3 -m venv venv
   ```

   ```
    source venv/bin/activate
   ```

   **For Windows:**

   Create and run the environment, with:

   ```
    python3 -m venv venv
   ```

   ```
    venv\Scripts\activate
   ```

4. Install the development requirements in `./requirements/dev.txt`, run the following command:

   **For Mac, Linux or Windows:**

   ```
   pip install -r requirements/dev.txt
   ```

5. Create a .env file with the following contents:

   ```
   # Domain
   # This would be set to the production domain with an env var on deployment
   # used by Traefik to transmit traffic and aqcuire TLS certificates
   DOMAIN=localhost

   # Environment: local, staging, production
   ENVIRONMENT=local

   PROJECT_NAME="API Project"
   STACK_NAME=api-project

   # Backend
   BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173,https://localhost,https://localhost:5173"
   SECRET_KEY=changethis

   # First Super User
   FIRST_SUPERUSER_FIRST_NAME=john
   FIRST_SUPERUSER_LAST_NAME=doe
   FIRST_SUPERUSER=admin
   FIRST_SUPERUSER_PASSWORD=hardpassword
   FIRST_SUPERUSER_PHONENUMBER= # With extension '+1'
   FIRST_ROLE=
   FIRST_SUPERUSER_BIRTHDAY=

   # Emails
   SMTP_HOST=
   SMTP_USER=
   SMTP_PASSWORD=
   EMAILS_FROM_EMAIL=info@example.com
   SMTP_TLS=True
   SMTP_SSL=False
   SMTP_PORT=587

   # Postgres
   POSTGRES_SERVER=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=
   POSTGRES_USER=
   POSTGRES_PASSWORD=

   SENTRY_DSN=

   # Uploads Server
   UPLOADS_URL=
   ```

6. Start the PostgreSQL server.

7. Apply the migrations to the database, using:

   ```
   alembic upgrade head
   ```

8. Run the RESTAPI using the debuger in `.vscode/launch.json` or using command:

   ```
   fastapi dev src/main.py
   ```

**_Running a local SMTP test service_**

To run this service please make sure that the following environment variables are set:

```
# Code above omitted 👆

# Emails
SMTP_HOST=local
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=info@example.com
SMTP_TLS=False
SMTP_SSL=False
SMTP_PORT=587

# Code bellow omitted 👇
```

The start a python ...

## Recommended resources 📚

In order to properly understand Tiangolo's project, the following resources 🔗 were helpful for me:

- The ⚡ **FastAPI** [official documentation](https://fastapi.tiangolo.com).
- The 🧰 **SQLModel** [official documentation](https://sqlmodel.tiangolo.com).
- The 🔍 **Pydantic** [official documentation](https://docs.pydantic.dev/latest/).
