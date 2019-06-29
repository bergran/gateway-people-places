# Gateway

This is a gateway, his function is to proxy places and people. Also if you request places, it's going to
response with places with him people (not deleted)


### Diagram
 
![Diagram](./gateway%20diagram.png)

### Before Up

App is ready to deploy it with some resources before app is up.

Proccess to up app is the next:

- Install app dependencies.
- Run migrate with alembic.
- Generate dummy data.
- Run app

Now, you should know that you has the power to set RESOURCE_ORIGIN origin, PLACES_MICROSERVICES and
PEOPLE_MICROSERVICES address services

Environment variables

```bash
      RESOURCE_ORIGIN: Place model has a property to notify some microservice to some place. This will be 
      the origin which it will create dummy data
      PLACES_MICROSERVICES: Place address service
      PEOPLE_MICROSERVICES: People address service
```

### How to deploy it?

It's ready to deploy with docker and docker-compose. Docker compose is a system that
allow you to have some services as pack using docker as containers, eg:

- database
- app
- redis
- whatever you need

now, that you know what is docker-compose we will start to deploy, you only need to follow this guide:

- docker network create microservice # This command will allow you to create a external network to comunicate with other services.
- docker-compose -f deployments/docker-compose.yml -p places up -d # And this will up the services that you need to run database and app.

This command runs db and app into 2 containers and it does to has another context. This is
very interesant because if you are builting microservices it will run as separated environments

 
### How to run project?

It's easy, you two options to run project.

- sh scripts/runserver.sh
- python main.py


### How to make migrations?

After create your models, you can use alembic directly or use script.

- `sh scripts/makemigrations "Some info about your migration"`
- `alembic revision --autogenerate -m "Some info about your migration"`

and migrate it on database:

- `sh scripts/migrate`
- `PYTHONPATH=.; alembic upgrade`


### Features

* User model agnostic. you choose your models
* Database and migrations with SqlAlchemy and Alembic.
* JWT Integration extraction only.
* TransactionTestCase, that means it could querying with test.

### Api documentation

App documentation is in the next route `/docs/`, `/redocs/` or open api format `/api/v1/openapi.json`

If you want to use Postmant, it is compatible with OpenApi, you only has to import with url to `/api/v1/openapi.json`


### Architecture


The architecture is made for medium-sized backends and It is placed in the following directory structure:

* alembic: database Migrations, you should change nothing here unless you need to remove
bad migration. Then just go to versions and remove them.
* apps: It is our api code, separated in some application modules. Later we will comment more about it.
* core: is where our code is shared among apps, for example: middlewares, dependencies, serializers, utils, etc.
* deployments: Here i put a docker-compose file, i do not suggest to use on production environment, only to develop and pre-prod
* scripts: Here i put some bash scripts to start fast project:
    * makemigrations: Create migrations/revisions from our models.
        * params: description about migration.
    * migrate: Apply migrations/revisions on Database.
    * runserver: Start server on 0.0.0.0 with hot reload.
    * startapp: create a skeleton app on apps directory.
        * params: app name.
        
### 1. App modules

Apps are part from our api/ws/graphQl logic. It's separated on:
 * models: Database models.
 * serializers: Here goes pydantic or serializers third party to your data.
 * test: As his name said, here it is saved our test.
 * views: Here goes our views logic. I'm not sure if i should separated api from ws and GraphQl views.
 At this time, all is here.
 * depends: Here we save our magic. If you do not know about what is Depends click [here](https://fastapi.tiangolo.com/tutorial/dependencies/first-steps/).
 * urls: Here we group all our router views to export it as app.
 
**Important**: To include app on project, you has to include app name into `apps` config and
include routes on core/urls.py as `app.include_router`

### 2. Database

Project database is configured to work with postgres, but it can allow work with
databases that are compatible with SqlAlchemy (MySql, Oracle, Sqlite and more...) for more
information you can click [here](https://www.sqlalchemy.org/features.html).

#### 2.1 Starting with models

As i said before, it's configure to work with SqlAlchemy. I create a shared `Base` to
inherit into the models on `core.db.meta.Meta` with `__tablename__` with model name with lower format.

**Important**: remember that models it's a module, so you have to include all your models on `__init__` into
the `__all__` variable to be recognized.

model example:

```
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column, Integer, String, DateTime

from core.db.base import Base


class Item(Base):
    __tablename__ = 'Items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    modified = Column(DateTime, default=datetime.datetime.utcnow)

```

#### 2.2 Querying

To query on your views, i added on `request.stage.session` the session as **transaction**, that means
if any exception get raised this gonna `rollback` all data info as block.

To know more about query api you can click [here](https://docs.sqlalchemy.org/en/13/orm/tutorial.html#querying)


#### 3. JWT integration

Integration with JWT is done with pyjwt, at this time just exist a `Depends` to get
jwt and other to get payload decoded.

#### 3.1 Depends

* get_jwt: it will regex always `Authorization` header with the header config that you
set it or default `JWT`. If header does not exist or has not `^{header} [A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$`
format then will raise `HTTPException` and response with status code `400`.

* get_token_decoded: it will check if jwt is valid and return payload. If token is expirate
it will raise `HTTPException` and response with status code `400`.


#### 4. Core

This is the shared code for our app, here we can find some utils to declare a model, some depends, serializers,
transactional test case, utils and config

#### 4.1 depends

It just like wizards, they can not make magic without his staff, we either can not make magic without depends on our views.

I declare some depends to reuse all time that we need it.

*  get_config: this depend will return app config from request.
*  get_database: it will return session database (Transaction)
*  get_object: it will get object or will return response with status `404`

#### 4.2 config

I'm sorry, i tried to do all light that i can posible ¯\_( ͡° ͜ʖ ͡°)_/¯.


```
BASE_DIR: absolute path to directory project
TEST_RUN: set this variable on make it test to get dummy database
SECRET_KEY: app secret
APPS: App list installed to create migrations
JWT_EXPIRATION_DELTA: Time to expirate jwt token
JWT_REFRESH_EXPIRATION_DELTA: Time to refresh token without fail
JWT_AUTH_HEADER_PREFIX: work that will start Authorization header, default: JWT
JWT_SECRET_KEY: secret to sign jwt
BACKEND_CORS_ORIGINS: url list to allow requests
PROJECT_NAME: Project name
SENTRY_DSN: 
SMTP_TLS: -
SMTP_PORT: -
SMTP_HOST: -
SMTP_USER: -
SMTP_PASSWORD: -
EMAILS_FROM_EMAIL: -
EMAILS_FROM_NAME: -
EMAIL_RESET_TOKEN_EXPIRE_HOURS: -
EMAIL_TEMPLATES_DIR: -
EMAILS_ENABLED: -
DATABASES: it's a dictionary with database information
```

You can set all of these variables with environment variable.


### Testing

It's implemented with pytest so it's easy to make test for each module app with the autodiscover feature.
Also i created `TransactionalTestCase` to create on `setUp` some information for your api and check it later making requests with client.

On finish each test it will delete all data store and it will create again with `setUp` to have always clean environment.
If you have to overwrite `tearDown` class, you should use super method to clean environment after test pass.

On finish all tests, it will delete test database.


Fixtures:

* session: database session, you can get it on `self.session`
* client: client to make request, you can get it on `self.client`
* base: base del, you can get it on `self.Base`


### Generate dummy data

In this template it's installed factory-boy library so if you want to do it, go [here](https://factoryboy.readthedocs.io/en/latest/orms.html#managing-sessions)

No needed to generate dummy data


### More info

This app origing is from [Fast-Api-Template](https://github.com/bergran/fast-api-project-template) boilerplate
