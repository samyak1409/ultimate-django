# [The Ultimate Django Series](https://codewithmosh.com/p/the-ultimate-django-series)

## Django Fundamentals > Creating Your First Django Project

### Virtual Env:

`pip3 install pipenv`

Now, move to the dir where you want the virtual env to be, there:  
`pipenv install django`

(A virtual env is created at a location like `/Users/samyak/.local/share/virtualenvs/Ultimate_Django-xxxxxxxx`, where all the libs are installed.)

Also, `Pipfile` is also created which looks like `requirements.txt`, but `pipenv` automatically adds the packages we install (using `pipenv`) to this file.

Get the path of current venv:  
`pipenv --venv`

Activate the venv:  
`pipenv shell`

IMPORTANT: Make sure whenever you do anything in the terminal inside this dir, venv is activated, the termnial would look like:  
`(Ultimate Django) samyak@Mac Ultimate Django %` or `Ultimate Djangosamyak@Mac Ultimate Django %`  
i.e. dir name prefix before `samyak@Mac`

## Django Fundamentals > Creating Your First App

https://en.wikipedia.org/wiki/Django_(web_framework):  
It follows the model–template–views (MTV) architectural pattern.  
Despite having its own nomenclature, such as naming the callable objects generating the HTTP responses "views", the core Django framework can be seen as an MVC architecture. It consists of an object-relational mapper (ORM) that mediates between data models (defined as Python classes) and a relational database ("Model"), a system for processing HTTP requests with a web templating system ("View"), and a regular-expression-based URL dispatcher ("Controller").

We can specify the port number explicitly if some other app is running on the default port 8000:  
`python manage.py runserver 9000`

See `INSTALLED_APPS` in `settings.py`.

`apps.py` - Should've been named `app_config.py` instead, since it contains app's configuration.  
`views.py` - Again, name is misleading, it's actually a request handler. "Views" means template/html in web dev.  
"Views" in other frameworks = "Templates" in Django.

## Django Fundamentals > Writing Views

Views or view functions takes a request and returns response.

## Django Fundamentals > Using Templates

We can replace Django's default template engine with a preferred template engine if we want.

Important: We don't use templates in Django that often now, we use Django to build APIs.

## Django Fundamentals > Using Django Debug Toolbar

https://django-debug-toolbar.readthedocs.io/en/latest/installation.html:  
`pipenv install django-debug-toolbar`
