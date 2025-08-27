from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Q,
    F,
    Value,
    Func,
    Avg,
    Count,
    Max,
    Min,
    Sum,
    ExpressionWrapper,
    DecimalField,
)
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from templated_mail.mail import BaseEmailMessage
from store.models import Product, Customer, Collection, Order, OrderItem
from tags.models import TaggedItem


def home(request):

    # Lecture-wise Notes (Change 0 to 1 in `if` to get a block executed. (Didn't comment-out the code so that it's still colored and hence more readable.)):
    # (Using `list`s since `QuerySet`s are lazy.)
    # NOTE: Below examples doesn't contain all possible queries but just a basic intro. Refer to API Reference https://docs.djangoproject.com/en/5.2/ref for that.

    # Retrieving Objects:
    if 0:

        list(Product.objects.all())
        # returns queryset of all the objects
        # Note: `QuerySet` objects contains the actual objects/instances of the queried model class.
        # Access to the data is done using `object.attr` syntax. E.g. `product.title` (`product` is `Product`'s instance var / object)

        Product.objects.get(pk=1)
        # returns single object

        # Product.objects.get(pk=0)
        # if object does not exist, raise `DoesNotExist` exception

        # So one solution is:
        try:
            Product.objects.get(pk=0)
        except ObjectDoesNotExist:
            pass

        # But better:
        Product.objects.filter(pk=0).first()
        # `.first()` returns the first object from the qs, if the qs is empty, it returns `None`

        # We can also pre-check:
        Product.objects.filter(pk=0).exists()
        # returns bool

    # Filtering Objects:
    if 0:

        list(Product.objects.filter(unit_price=10))

        # What if we want other operators like `>`?
        list(Product.objects.filter(unit_price__gt=20))

        # SQL's `BETWEEN` keyword:
        list(Product.objects.filter(unit_price__range=(20, 25)))  # inclusive

        # We can also use the relationship field, and use the related table's field name:
        list(Product.objects.filter(collection__title="Pets"))
        # Lookup types can be applied on top of this as well.

        # `LIKE`:
        list(Product.objects.filter(title__contains="coffee"))
        # case-insensitive:
        list(Product.objects.filter(title__icontains="coffee"))
        # We also have `startswith`, `endswith`, etc.

        # Dates:
        list(Product.objects.filter(last_update__year=2021))
        # i.e. we can extract individual components of a date / datetime field

        # NULL:
        list(Product.objects.filter(description__isnull=True))

        # Exercises (from ORM_Filtering.pdf):

        # 1) Customers with .com accounts:
        list(Customer.objects.filter(email__endswith=".com"))

        # 2) Collections that don’t have a featured product:
        list(Collection.objects.filter(featured_product__isnull=True))

        # 3) Products with low inventory (less than 10):
        list(Product.objects.filter(inventory__lt=10))

        # 4) Orders placed by customer with id = 1:
        list(Order.objects.filter(customer=1))

        # 5) Order items for products in collection 3:
        list(OrderItem.objects.filter(product__collection=3))
        # `__`: nested lookup

    # Complex Lookups Using Q Objects:
    if 0:

        # Multiple filters (`AND` in SQL):
        list(Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20))
        # But better:
        list(Product.objects.filter(inventory__lt=10, unit_price__lt=20))

        # But how would we do `OR`, there comes `Q` (short for query) objects:
        list(Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20)))
        # Every `Q` object take a single kwarg.
        # `|` = Bitwise OR -> SQL `OR`
        # `&` = Bitwise AND -> SQL `AND`
        # `~` = Bitwise NOT -> SQL `NOT`
        list(Product.objects.filter(Q(inventory__lt=10) | ~Q(unit_price__lt=20)))

    # Referencing Fields using F Objects:
    if 0:

        # `F` (for field) objects are used when we want records where field1 == field2:
        # list(Product.objects.filter(inventory=unit_price))  # can't do this, right, so ->
        list(Product.objects.filter(inventory=F("unit_price")))
        # And, we can also use `__` to navigate to a related field's table like we did in "Filtering Objects" section above:
        list(Product.objects.filter(description=F("collection__title")))
        # In `collection__title`, `collection` is the foreign key, `title` is a field in the Collection table.

        # This was pretty straight-forward.

    # Sorting:
    if 0:

        # Asc:
        list(Product.objects.order_by("title"))
        # Desc:
        list(Product.objects.order_by("-title"))
        list(Product.objects.order_by("title").reverse())

        # Sorting on two fields, one after other (just like we do in python):
        list(Product.objects.order_by("unit_price", "title"))
        list(Product.objects.order_by("-unit_price", "title"))

        # And obviously `order_by` works on `QuerySet`s.

        # Getting the first/last / min/max / top:
        Product.objects.order_by("-unit_price")[0]
        # We've convenience methods for this:
        Product.objects.earliest("unit_price")  # basically, ASC
        Product.objects.latest("unit_price")  # basically, DESC

    # Limiting Results:
    if 0:

        # `LIMIT 5`:
        list(Product.objects.all()[:5])

        # `LIMIT 15 OFFSET 10` (skip 10, then give (next) 15):
        list(Product.objects.all()[10:25])

    # Selecting Fields to Query:
    if 0:

        # Selecting selected columns instead of *:
        list(Product.objects.values("id", "title", "collection__title"))
        # Note that we can also use the related field using `__`, this is done using (INNER) JOIN by Django.
        # Also, as we know that `QuerySet` objects contains the actual objects/instances of the queried model class.
        # But, above return a `ValuesQuerySet` which is basically a `QuerySet` of `dict` objects not model class objects.
        # Key-value pairs are field-value.
        # e.g. vqs[0] = {'id': 2, 'title': 'Island Oasis - Raspberry', 'collection_title': 'Beauty'}

        list(Product.objects.values_list("id", "title", "collection__title"))
        # Same as above, this just contains `tuple` instead of `dict`.
        # e.g. vqs[0] = (2, 'Island Oasis - Raspberry', 'Beauty')

        # Exercise: Select products that have been ordered and sort them by title
        ordered_product_ids = OrderItem.objects.values("product_id").distinct()
        list(Product.objects.filter(id__in=ordered_product_ids).order_by("title"))

    # Deferring Fields:
    if 0:

        # Like `.values()` in the sense that used to get only a selected fields, but returns model class objects instead of `dict`s:
        if 0:
            for product in Product.objects.only("id", "title"):  # 1 query
                print(product.id, product.title)  # correct
                print(product.description)  # bug: 1 query n times
        # What's the bug?
        # When we use `only()`, the returned queryset contains the objects with only the fields passed as arg.
        # If by mistake we access any other field, then the Django won't throw an error, but instead go ahead and query the DB to get the result.
        # So, if that bug is inside a for loop and run for every record in our table like above, it would hang the app for some seconds.
        # Hence, take precaution using this.

        # Opposite of `only` in working, selects all the fields other than specified one(s):
        list(Product.objects.defer("description"))
        # Also, same precaution to be taken here as well.

    # Selecting Related Objects:
    if 0:

        if 0:
            for product in Product.objects.all():  # 1 query
                print(product.title, end=" --- ")  # correct
                print(product.collection.title)  # bug: 1 query n times
        # [First of all, didn't know we can do `product.collection.title`,
        # Django automatically generates this query with the help of INNER JOIN, just like it does in the case of dunder `collection__title`.]
        # What's the bug?
        # Exactly same problem as above, it is being done n times.
        # But, what if we actually want to access the values of related field's table's other fields.
        # There comes `select_related()` (for `OneToOneField` & `ForeignKey`):
        for product in Product.objects.select_related("collection"):  # 1 query
            print(product.title, end=" --- ")  # correct
            print(product.collection.title)  # correct
        # Here, Django uses a INNER JOIN at the very start only, and selects all the fields of both tables, hence all the fields can be accessed. (Only 1 query in total.)
        # Important notes:
        # - We can use `Product.objects.select_related('collection__title')` i.e. nested lookup as well.
        #   - To select `title`, `collection` needs to be selected, so we never need to do `Product.objects.select_related('collection', 'collection__title')`,
        #     and it's considered redundant.
        # - Multiple fields can also be supplied: `OrderItem.objects.select_related('order', 'product')`

        # `prefetch_related()` (for `ManyToManyField` & reverse `ForeignKey` (i.e., when accessing the `_set` on a model)):
        list(Product.objects.prefetch_related("promotions"))
        # IMP: Read the markdown notes for this.

        # What if we want to access data from `OneToOneField` / `ForeignKey` and `ManyToManyField` / reverse `ForeignKey` together?
        # We can call `select_related` & `prefetch_related` one after another (in any order since both of them return a QS):
        list(
            Product.objects.select_related("collection").prefetch_related("promotions")
        )

        # Exercise: Get the last 5 orders with their customer and items (incl product)
        orders = (
            Order.objects.order_by("-placed_at")[:5]
            .select_related("customer")
            .prefetch_related("orderitem_set__product")
        )
        # # (Prefetching `orderitem_set__product` prefetches `orderitem_set`.)
        for order in orders:
            print(f"Order ID: {order.id}, Customer: {order.customer.first_name}")
            for item in order.orderitem_set.all():
                print(
                    f"- Item ID: {item.id}, Product: {item.product.title}, Quantity: {item.quantity}"
                )

    # Aggregating Objects:
    if 0:

        print(Product.objects.aggregate(Count("id")))
        # Why do we need this when we can use:
        print(Product.objects.count())
        # Because `Count()` can be used to count on any field, `count()` counts all the records.
        # Also, multiple aggregates can be passed:
        print(Product.objects.aggregate(Count("id"), Min("unit_price")))
        # {'id__count': 1000, 'unit_price__min': Decimal('1.06')}
        # Returns the dict containing:
        # - key = param name if used else arg inside the aggregate object
        # - value = result
        # So, we can also do if we want:
        print(Product.objects.aggregate(count=Count("id"), min_price=Min("unit_price")))
        # {'count': 1000, 'min_price': Decimal('1.06')}

        # Exercises (from ORM_Aggregating.pdf):
        print("-" * 100)

        # 1) How many orders do we have?
        print(Order.objects.aggregate(Count("id")))
        # Or just:
        print(Order.objects.count())

        # 2) How many units of product 1 have we sold?
        print(OrderItem.objects.filter(product=1).aggregate(Sum("quantity")))

        # 3) How many orders has customer 1 placed?
        print(Order.objects.filter(customer=1).aggregate(Count("id")))
        # Or just:
        print(Order.objects.filter(customer=1).count())

        # 4) What is the min, max and average price of the products in collection 3?
        print(
            Product.objects.filter(collection=3).aggregate(
                Min("unit_price"), Max("unit_price"), Avg("unit_price")
            )
        )

    # Annotating Objects:
    if 0:

        # Only `Expression` objects can be passed (`Value()`, `F()`, `Q()`, etc.):
        list(Customer.objects.annotate(new=Value(True)))
        # kwarg where keyword would be the name of the column, arg would be the values

        list(Customer.objects.annotate(new_id=F("id") + 1))

        # One important thing, check the MD notes of this section.

    # Calling Database Functions:
    if 0:

        # Generic `Func()`:
        list(
            Customer.objects.annotate(
                full_name=Func(
                    F("first_name"), Value(" "), F("last_name"), function="CONCAT"
                )
            )
        )

        # Dedicated class:
        list(
            Customer.objects.annotate(
                full_name=Concat("first_name", Value(" "), "last_name")
            )
        )

    # Grouping Data:
    if 0:

        # If we want to see number of orders each customer has placed:
        if 0:
            list(Customer.objects.annotate(Count("order_set")))
        # `FieldError`
        # `_set` name won't work here, just the name of the model in lowercase would work.
        # Why? Because `_set` naming is a Python API which sends a JOIN query to the DB.
        # However, queryset methods are a part of Query API (works on DB level), in which model names in lowercase only are used.
        list(Customer.objects.annotate(Count("order")))

        # Exercises (from https://jasonxqh.github.io/2021/07/05/Django%E5%AD%A6%E4%B9%A01/#Annotating-Exercises):

        # 1) Customers with their last order ID:
        list(Customer.objects.annotate(last_order_id=Max("order")))

        # 2) Collections and count of their products:
        list(Collection.objects.annotate(Count("product")))

        # 3) Customers with more than 5 orders:
        list(Customer.objects.annotate(Count("order")).filter(order__count__gt=5))
        # Or:
        list(
            Customer.objects.annotate(order_count=Count("order")).filter(
                order_count__gt=5
            )
        )

        # 4) Customers and the total amount they’ve spent:
        list(
            Customer.objects.annotate(
                total_spend=Sum(
                    F("order__orderitem__unit_price") * F("order__orderitem__quantity")
                )
            )
        )
        # IMPORTANT:
        # We need to `select_related`/`prefetch_related` only when we're accessing related fields here in python using ORM object attributes (Python API).
        # In other cases like above, Django makes the required joins since it beforehand has all related fields.
        # In other words:
        # Use `select_related` or `prefetch_related` when you plan to access related objects via ORM attributes in Python after the query.
        # For queries that only retrieve raw fields from related tables (e.g., using .values(), .annotate()),
        # Django generates the necessary SQL joins for those fields automatically.

        # 5) Top 5 best-selling products and their total sales:
        list(
            Product.objects.annotate(
                total_sales=Sum("orderitem__quantity", default=0)
            ).order_by("-total_sales")[:5]
        )

    # Working with Expression Wrappers:
    if 0:

        # Show discounted price:
        if 0:
            list(Product.objects.annotate(discounted_price=F("unit_price") * 0.9))
        # `FieldError`: because type(unit_price) = Decimal, type(.9) = Float
        # So, using `ExpressionWrapper()`:
        discounted = ExpressionWrapper(
            expression=F("unit_price") * 0.9, output_field=DecimalField()
        )
        list(Product.objects.annotate(discounted_price=discounted))

    # Querying Generic Relationships:
    if 0:

        # Since the liked item can belong to any model:
        content_type = ContentType.objects.get_for_model(Product)

        # Now, getting all the tags product with id 1 is tagged with:
        list(
            TaggedItem.objects.select_related("tag").filter(
                content_type=content_type, object_id=1
            )
        )
        # `object_id=1` hardcoded here, but in real app, id would come from the client side
        # e.g. when a user open a product page, we need to show all the tags, so we'd get the product id, query the tags, and return.

    # Custom Managers:
    if 0:

        # (Check the code in `tags.models`.)
        # Now, following is equivalent as above section:
        list(TaggedItem.objects.get_for(model=Product, obj_id=1))

    # Understanding QuerySet Cache:
    if 0:

        # Read MD notes.
        pass

    # Creating Objects:
    if 0:

        new_collection = Collection()
        new_collection.title = "Games"
        new_collection.save()
        # Or:
        new_collection = Collection(title="Games")
        new_collection.save()
        # Or just:
        new_collection = Collection.objects.create(title="Games")

        # Saving relationship fields:
        # Either we can do:
        # `featured_product=<Product object>`
        # Or:
        # `featured_product_id=<id of a Product>`

    # Updating Objects:
    if 0:

        # Same as creation, just give an existing pk/id, and Django would translate it to UPDATE instead of CREATE:
        # But, note that if the `pk` doesn't exist, then this would create a new record!
        if 0:
            new_collection = Collection(pk=15, title="Tech")
            new_collection.save()
        # Problem with this: For all the fields which are not updated, are reset to `null` or empty str.
        # (Some other ORMs doesn't have this problem, because they've a feature change tracking, which as the name suggests tracks
        # which fields are changed, and only updates them.)
        # So, the correct approach is basically just getting the current data into the memory, then update:
        # (So the data we're updating would just overwrite in memory, and the other fields remain the same.)
        new_collection = Collection.objects.get(pk=15)
        new_collection.title = "Tech"
        new_collection.save()

        # But that looks like a lot of code for a simple update, that's why we've a convenience method here as well just like `create()`:
        # Note that first we need to `filter` (`get` won't work since `update` is not a `models.Model` method, it's a `QuerySet` method), and then update:
        # Hence, also note that it can be used to update multiple records in one go, all the objects which are there in returned QuerySet.
        print(
            "Rows affected:",
            Collection.objects.filter(pk=15).update(featured_product_id=2),
        )

    # Deleting Objects:
    if 0:

        # Unlike above two, deleting is very straight-forward since `delete()` is available in both `QuerySet` and `models.Model`:
        print(Collection(pk=18).delete())
        print(Collection.objects.filter(id__gt=18).delete())
        # Returns the number of objects deleted and a dictionary with the number of deletions per object type.

        # Doubt: First selecting, then deleting, why not DELETE-ing directly?

    # Transactions:
    if 0:

        # Example usage of transaction:
        if 0:
            order = Order.objects.create(customer_id=1)
            item = OrderItem.objects.create(
                order=order, product_id=1, quantity=1, unit_price=10
            )
        # Now, if 1st line is executed, but 2nd fails, then we would left with a order without order_item.

        # To avoid that, either we decorate a function inside which all the code would be a single transaction using `@transaction.atomic`.
        # Or, we can use `with` context manager:
        with transaction.atomic():
            order = Order.objects.create(customer_id=1)
            item = OrderItem.objects.create(
                order=order, product_id=1, quantity=1, unit_price=10
            )

        # https://docs.djangoproject.com/en/5.2/topics/db/transactions/#controlling-transactions-explicitly

    # Executing Raw SQL Queries:
    if 0:

        # (Simple query just for example)
        list(Product.objects.raw("SELECT * FROM store_product"))
        # returns RawQuerySet
        # QuerySet vs. RawQuerySet: https://g.co/gemini/share/2222a9d92831

        # Above still have Model objects inside RawQuerySet, and the data is still mapped, i.e. can be access using `.`.
        # But, what if we don't want the data to link to the object, or we want to use store procedures,
        # in these cases we can directly use direct DB connection, skipping the ORM layer completely:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM store_product")
            # We can also use stored procedures:
            cursor.callproc("get_customers", [1, 2, 3])
        # (Always use `with` context manager so that connection is automatically closed even in the case of an Exception.)

    # return HttpResponse("This is the home page of the playground app.")
    return render(request, template_name="index.html", context={"heading": "Home Page"})


def test_mail(request):

    try:

        if 0:
            send_mail(
                subject="Testing `send_mail`",
                message="Hello there!",
                from_email=None,
                recipient_list=["samyak65400@gmail.com"],
                html_message="<h1>Hello there!</h1>",
            )

        if 0:
            mail_admins(subject="Testing `mail_admins`", message="Hello admin!")

        if 0:
            msg = EmailMessage(
                subject="Testing `EmailMessage` for Attachment",
                body="PFA",
                to=["someone@gmail.com"],
            )
            msg.attach_file(path="media/playground/bike.jpg")
            msg.send()

        if 1:
            BaseEmailMessage(
                context={"name": "Samyak"}, template_name="mails/hello.html"
            ).send(to=["someone@gmail.com"])

    except BadHeaderError as e:
        return HttpResponse(e)

    return HttpResponse("Mails sent.")
