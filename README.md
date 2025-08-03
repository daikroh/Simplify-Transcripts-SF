# Simplify-Transcripts-SF

## Installation
It's recommended to create a virtual environment to install the dependencies.

Create the virtual environment:
```
python3 -m venv demo
```

And activate it:
```
source demo/bin/activate
```

To deactivate it:
```
deactivate
```

To install the dependencies:
```
pip install -r /path/to/requirements.txt
```

To update list of dependencies:
```
pip freeze > requirements.txt
```

To run the server:
```
cd simplify_transcripts
python3 manage.py runserver
```

## Create PostgreSQL Database
If you don't have PostgreSQL set up yet:
Install Postgres.app and add to path:
```
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
source ~/.zshrc
```

The credentials in settings.py will be the configurations you use in the Postgres.app.

To verify, create a superuser and enter the Django admin page:
```
python manage.py createsuperuser
python manage.py runserver
```

To enter database:
```
psql -U postgres -d meetings
```

To create the databases:
```
python manage.py makemigrations
python manage.py migrate
```

Optimizing indexing, trigram similarity for partial matching, vector for semantic matching:
```
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;
```