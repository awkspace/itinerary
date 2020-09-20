# itinerary

A tool to apply pure SQL migrations to PostgreSQL databases at runtime.

Itinerary uses PostgreSQL’s [advisory locks][lock] feature to prevent multiple
instances from running migrations simultaneously. As such, it’s suitable for use
in horizontally scalable applications.

## Installation

``` sh
pip install itinerary
```

## Usage

Put raw SQL files in your migration directory, e.g.:

```
migrations/0001_create_table.sql
migrations/0002_add_column.sql
migrations/0003_create_index.sql
```

Then run the `auto_migrate` function before your application starts.

### Flask example

``` python
import itinerary
from flask import Flask
app = Flask(__name__)

if __name__ == '__main__':
    conn = psycopg2.connect(host='localhost')
    itinerary.auto_migrate(conn)
    app.run()
```

### uWSGI example

``` python
import itinerary
from uwsgidecorators import postfork

@postfork
def migrate_db():
    conn = psycopg2.connect(host='localhost')
    itinerary.auto_migrate(conn)
```

## Configuration

``` python
itinerary.auto_migrate(connection, path='migrations',
                       version_table='_version', lock_id=0)
```

* **path** – Directory to scan for migration files.
* **version_table** – Table to use to keep track of applied migrations. If it
  doesn’t exist, itinerary will create it.
* **lock_id** – The key to use when acquiring and releasing a PostgreSQL
  advisory lock.
  
[lock]: https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS
