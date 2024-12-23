# API Project Template

Welcome to my project 📁, his project is the core of a bigger application. This is intended to be used as a template. I am also using this project to learn 🤓 please leave any recommendations.

📓 I followed the best practices described in this [Repository](https://github.com/zhanymkanov/fastapi-best-practices?tab=readme-ov-file#project-structure).

🌟 Based on the project from Tiangolo's [Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/api/routes/login.py).

## Setup instructions

To setup locally please follow the following steps

1. Install `Postgresql` locally or in a docker container and update the `.env` file with the following credentials:

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
   FIRST_SUPERUSER_PHONENUMBER= # With extension example: '+11234567890'
   FIRST_SUPERUSER_EMAIL=
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
   EMAIL_RESET_TOKEN_EXPIRE_HOURS=

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

8. Run the RESTAPI using a debuger in `.vscode/launch.json` or using command:

   ```
   fastapi dev src/main.py
   ```

9. Using MailHog SMTP Server (for testing emails):

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
   SMTP_PORT=1025

   # Code bellow omitted 👇
   ```

   9.1 Install and start MailHog by running:

   **For Mac:**

   ```
   brew update && brew install mailhog
   ```

   ```
   mailhog
   ```

   **For Linux (Debian or Ubuntu)**

   ```
   sudo apt-get -y install golang-go
   go get github.com/mailhog/MailHog
   ```

   ```
   /path/to/MailHog # The path to the MailHog installation.
   ```

   The service will catch the outgoing email and display it at [`http://localhost:8025`](http://localhost:8025).

## Development recommendations

### Creating email templates

To create a email template the project uses mjml, a markup language used for designing responsive HTML emails.

1. Install mjml's Visual Studio Code [extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml).

   Press `F1` and type `ext install vscode-mjml`.

2. Create a `.mjml` file in the `src/mail/templates/src`.

3. To preview the contents press `F1` or `Ctrl+Shift+P` and type `MJML: Open Preview to the Side`.

4. To generate the html file press `F1` or `Ctrl+Shift+P` and type `MJML: Export HTML` modify the file name and save it pressing `Enter ↩️`.

### Creating tests and testing

For testing an in-memory data base is used. You can check the configurations in the `conftest.py` file.

I recommend reading about [fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html), which are a very useful feature of pytest and are heavily use in this project.

Aim to test 80-90% of your code. 🤯

#### Writing and running unit tests

1. Create a directory with the same name that the package in the `src/` directory it will test.
   ```
   ├── src/
   │   └── auth/
   ├── tests/
       └── auth/
   ```
2. Inside the folder create files with the `test_` prefix or `_test` sufix to test the individual modules (router, service, etc.).
   ```
   ├── src/
   │   └── auth/
   │        ├── router.py
   │        └── service.py
   ├── tests/
       └── auth/
            ├── test_router.py
            └── service_test.py
   ```
3. Create the necesary test(s). These should be independent from each other!

4. Run the tests with the commands:

   Running all tests:

   ```
   pytest
   ```

   Running all tests in a test\_ file:

   ```
   pytest tests/route/to/test_file_name.py
   ```

   Running a specific test in a test\_ file:

   ```
   pytest tests/route/to/test_file_name.py::test_function_name
   ```

#### Data for endpoints

Pay attention to the way the endpoint takes data as query parameters or as a request body.

- Query parameters:

  ```
  r = client.get(
           url=f"{settings.API_V1_STR}/example/path/{parameter}"
        )
  ```

- Form data:

  ```
  data_body = {
     "parameter1": value,
     "parameter2": value
     }

  r = client.post(
        url=f"{settings.API_V1_STR}/example/path/",
        headers=example_headers,
        data=data_body, # <- Changes here
     )
  ```

- Request body:

  ```
  data_body = {
     "parameter1": value,
     "parameter2": value
     }

  r = client.post(
        url=f"{settings.API_V1_STR}/example/path/",
        headers=example_headers,
        json=data_body, # <- Changes here
     )
  ```

#### Tests interference

Make sure that the created `fixtures` are properly scoped. Properly clean up test data. Feel free to leave any recommendations for this problem.

For more information about testing [check out this video](https://youtu.be/cHYq1MRoyI0?si=8vPOAz5H1fWHW6Mb) from **_freeCodeCamp.org_** (🔥).

### New models and revisions

It is recommended to create a new folder for each module, for example to create a `customers` application:

1. Create a folder in the `src/` directory:

   ```
      ├── src/
         └── customers/
   ```

2. Create a `models.py` file inside this folder.

   ```
      ├── src/
         └── customers/
               └── models.py
   ```

3. Add the tables into the file with SQLModel.

   ```
   from sqlmodel import SQLModel

   class Customer(SQLModel, table= True):
      id: int | None = Field(default=None, primary_key=True)
      first_name: str = Field(max_length=50)
      last_name: str = Field(max_length=50)
      birthday: date
      phone_number: int

   # Add all the necessary columns and models here 👇
   ```

#### Creating the alembic revision

To create the alembic revision correctly follow the steps:

1. Import the model to the global models:

   ```
   ├── src/
         └── models.py
   ```

   Add the model there:

   ```
   # Add all the models to this file in order to generate automatic migrations

   from src.customers.models import *
   # Code omited below 👇
   ```

2. Run the command:

   ```
   alembic revision --autogenerate -m "Added a customers table."
   ```

3. Check the newly generated revision, add the `sqlmodel` library import:

   ```
   # code omited above 👆

   import sqlmodel

   # code omited bellow 👇
   ```

4. Finally upgrade the data base, running:

   ```
   alembic upgrade head
   ```

## Recommended resources 📚

In order to properly understand Tiangolo's project and start developing, the following resources 🔗 were helpful for me:

- The ⚡ **FastAPI** [official documentation](https://fastapi.tiangolo.com).
- The 🧰 **SQLModel** [official documentation](https://sqlmodel.tiangolo.com).
- The 🔍 **Pydantic** [official documentation](https://docs.pydantic.dev/latest/).
- The 📧 **MJML** [official documentation](https://documentation.mjml.io/#getting-started).
- The 🧪 **Pytest** [official documentation](https://docs.pytest.org/en/stable/getting-started.html#).
