# [The Ultimate Django Series](https://codewithmosh.com/p/the-ultimate-django-series)

## Django Fundamentals > Creating Your First Django Project

### Virtual Environment:

Install pipenv:

```bash
pip3 install pipenv
```

Now, move to the directory where you want the virtual environment to be, then run:

```bash
pipenv install django
```

This creates a virtual environment at a location like:

```
/Users/samyak/.local/share/virtualenvs/Ultimate_Django-xxxxxxxx
```

All the libraries are installed here.

A `Pipfile` is also created, which looks like a `requirements.txt` file, but `pipenv` automatically adds the packages you install (using `pipenv`) to this file.

Get the path of the current virtual environment:

```bash
pipenv --venv
```

Activate the virtual environment:

```bash
pipenv shell
```

**Important:** Make sure whenever you do anything in the terminal inside this directory, the virtual environment is activated.
The terminal would look like:

```
(Ultimate Django) samyak@Mac Ultimate Django %
```

or

```
Ultimate Djangosamyak@Mac Ultimate Django %
```

That is, the directory name appears as a prefix before `samyak@Mac`.

## Django Fundamentals > Creating Your First App

https://en.wikipedia.org/wiki/Django_(web_framework):

> It follows the model–template–views (MTV) architectural pattern.
> Despite having its own nomenclature (such as naming the callable objects generating the HTTP responses "views"), the core Django framework can be seen as an MVC architecture.  
> It consists of:  
> -- an object-relational mapper (ORM) that mediates between data models (defined as Python classes) and a relational database ("Model"),  
> -- a system for processing HTTP requests with a web templating system ("View"),  
> -- and a regular-expression-based URL dispatcher ("Controller").

We can specify the port number explicitly if some other app is running on the default port 8000:

```bash
python manage.py runserver 9000
```

See `INSTALLED_APPS` in `settings.py`.

- `apps.py` – Should've been named `app_config.py` instead, since it contains the app's configuration.
- `views.py` – Again, the name is misleading. It's actually a request handler. "Views" usually refer to templates or HTML in web development.
  "Views" in other frameworks = "Templates" in Django.

## Django Fundamentals > Writing Views

Views or view functions take a request and return a response.

## Django Fundamentals > Using Templates

We can replace Django's default template engine with a preferred template engine if we want.

> Important: We don't use templates in Django that often now. Django is primarily used to build APIs.

## Django Fundamentals > Using Django Debug Toolbar

https://django-debug-toolbar.readthedocs.io/en/latest/installation.html:

Install with:

```bash
pipenv install django-debug-toolbar
```

## Building a Data Model > Introduction to Data Modeling

Types of relationships:
- One to One
- One to Many
- Many to Many

## Building a Data Model > Organizing Models in Apps

https://en.wikipedia.org/wiki/Monolithic_application - All the models in single app.  
Problem: Complexity

https://en.wikipedia.org/wiki/Microservices - Multiple apps containing only a few models each.  
Problem: Interdependence i.e. called Coupling

Middle ground is the way to go, such that all the apps:
- are self-contained / high cohesion (focus): i.e. if we `pip` install an app in a different project, we don't need to install another app(s) just to make the models of the first app work correctly
- have zero/minimal coupling

## Building a Data Model > Creating Models

This document contains all the API references of `Field` including the field options and field types Django offers:  
https://docs.djangoproject.com/en/stable/ref/models/fields

https://docs.djangoproject.com/en/5.2/ref/models/fields/#floatfield:  
> `FloatField` vs. `DecimalField`  
> The [`FloatField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#floatfield) class is sometimes mixed up with the [`DecimalField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#decimalfield) class. Although they both represent real numbers, they represent those numbers differently. `FloatField` uses Python’s `float` type internally, while `DecimalField` uses Python’s `Decimal` type. For information on the difference between the two, see Python’s documentation for the [`decimal`](https://docs.python.org/3/library/decimal.html#module-decimal) module.

https://docs.python.org/3/library/decimal.html#module-decimal:  
> The `decimal` module provides support for fast correctly rounded decimal floating-point arithmetic.

Basically, `FloatField` has rounding errors, hence, always use `DecimalField` for sensitive fields like monetory values, which should be completely accurate.

Why we should just use `CharField.max_length = 255` in most cases instead of more precisely calculated maxes for small fields like `first_name`, `phone`:
- https://chatgpt.com/share/687272f9-c25c-800a-af95-c791f3dbb5be
- https://g.co/gemini/share/152db050dbdf

Note: Django creates a primary key `id` for every model by default, unless we define a particular field with `primary_key=True`.

## Building a Data Model > Defining One-to-one Relationships

`models.OneToOneField`

`on_delete` options:  
https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey.on_delete

Some of which are:
- `models.CASCADE`: Will delete the child record.
- `models.SET_NULL`: Will set the foreign key to NULL, record stays.
- `models.SET_DEFAULT`: Will set the foreign key to its default val, record stays.
- `models.PROTECT`: Will prevent deleting the parent record if a child record is associated, first child record would be needed to be deleted.

Child record is the one which have a foreign key relationship in its definition. E.g. Parent: `Customer`, Child: `Address`  
In `Address` model definition:  
`customer = models.OneToOneField()`

Also, Django automatically creates a reverse relationship in the parent i.e. `Customer` class, named `address`.  
But why? We can already get address from customer and vice versa, then why do we need this?

## Building a Data Model > Defining a One-to-many Relationship

`models.ForeignKey`

Note: If we want to define a foreign relationship, the other class needs to be defined above in order to reference it.  
If that's not possible (in case of circular relationship), pass the name of the class **as a string**.  
(But, only do this in case of circular relationship, not when you can just move the class above, since if we ever wanted to rename the class, we might forget to rename in the string.)

## Building a Data Model > Defining Many-to-many Relationships

`models.ManyToManyField`

## Building a Data Model > Resolving Circular Relationships

See `store.models.Collection` class.

To avoid name clash in case of circular dependency:
- If you don't want the reverse relation: Just add `related_name='+'` to tell Django to not create a reverse relationship for this particular relationship field.
- Else, use `related_name` to give the field a different name.

https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey.related_name

## Building a Data Model > Generic Relationships

As discussed in `Organizing Models in Apps`, we've a seperate app `tags`.  
Now, to define the model, we should use a generic `ContentType` model instead of our actual model(s). So that the app is actually not related, and can be used in any other project **as is**.

> `ContentType` model is specifically made for allowing generic relationships. It's there in the pre-installed django app `contenttypes`.

To define a generic relationship, we need to define three fields in total:
```python
content_type = models.ForeignKey(to=ContentType, on_delete=...)
object_id = models.PositiveIntegerField()
content_object = GenericForeignKey()
```

> Not completely understood...
