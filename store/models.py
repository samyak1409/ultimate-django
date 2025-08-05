from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from uuid import uuid4


class Collection(models.Model):

    title = models.CharField(max_length=255)

    featured_product = models.OneToOneField(
        to="Product", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    # IMPORTANT: Mosh has used `ForeignKey` but since any product can belong to only a single collection, any two collections won't have a same featured product, and hence no need of `ForeignKey`.
    # `related_name='+'`: avoid name clash by telling django to not create a reverse relationship field for this field.

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Promotion(models.Model):

    description = models.CharField(max_length=255)

    discount = models.FloatField()


class Product(models.Model):

    title = models.CharField(max_length=255)  # -> varchar(255)

    slug = models.SlugField()
    # What's slug?
    # e.g. "everyone-is-writing-wrong-time-complexit-6gil" in
    # https://leetcode.com/problems/partition-string/solutions/6923792/everyone-is-writing-wrong-time-complexit-6gil
    # is slug. It's made from the title, and is for search engines to find and rank our content better. It's basically a SEO technique.

    description = models.TextField(null=True, blank=True)

    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    # `FloatField` has rounding errors, and sensitive fields like `price` should be very accurate
    # and max price = 9999.99, digit counting concept is same as that in sql

    inventory = models.PositiveIntegerField()
    # let's use `PositiveIntegerField` instead of `IntegerField`

    last_update = models.DateTimeField(auto_now=True)
    # if this was `created_at`, we would've used `auto_now_add=True`
    # `auto_now_add`: Automatically set the field to now when the object is first created.
    # `auto_now`: Automatically set the field to now every time the object is saved.

    collection = models.ForeignKey(to=Collection, on_delete=models.PROTECT)
    # (`ForeignKey`: since multiple products can belong to a same collection.)
    # If we allowed the products belonging to none of the collections, we would've used `on_delete=models.SET_NULL, null=True`.
    # But, we've set to only allow deletion of a collection, if none of the products belong to it.

    promotions = models.ManyToManyField(to=Promotion, blank=True)

    def __str__(self) -> str:
        return self.title


class Customer(models.Model):

    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # https://docs.djangoproject.com/en/5.2/ref/models/fields/#choices
    # The first element in each tuple is the actual value to be set on the model, and the second element is the human-readable name.
    MEMBERSHIP_CHOICES = [
        ("B", "Bronze"),
        ("S", "Silver"),
        ("G", "Gold"),
    ]
    # Why we often use short codes like "B", "S", "G" in the database instead of storing "Bronze", "Silver", "Gold" directly:
    # https://chatgpt.com/share/687278b8-6010-800a-97e1-408b28dfac8c

    # Now, since we've linked this model to user model, that model already have following fields:
    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    # email = models.EmailField(unique=True)

    phone = models.CharField(max_length=255)

    birth_date = models.DateField(null=True)

    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_CHOICES[0][0]
    )

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Order(models.Model):

    PAYMENT_STATUS_CHOICES = [("P", "Pending"), ("C", "Completed"), ("F", "Failed")]

    placed_at = models.DateTimeField(auto_now_add=True)

    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_CHOICES[0][0],
    )

    customer = models.ForeignKey(to=Customer, on_delete=models.PROTECT)
    # According to me, `on_delete=models.SET_NULL, null=True` should be used. So that customer can be deleted, their order would still be present.
    # (We can also add a `deleted_user` customer in our `Customer` table, and then set the above to this customer.)
    # Mosh is using `on_delete=models.PROTECT` to protect deleting of the orders if a customer is deleted, but, that stops us from deleting a customer!!

    class Meta:
        permissions = [
            ("cancel_order", "Can cancel order"),
        ]


class OrderItem(models.Model):

    order = models.ForeignKey(to=Order, on_delete=models.PROTECT)
    # Again, acc. to me `CASCADE` should be used instead of `PROTECT`.
    # Why? If a order is deleted, there's no sense to still have the details of that order like the items in that order.

    product = models.ForeignKey(to=Product, on_delete=models.PROTECT)
    # Again, acc. to me `SET_NULL, null=True` should be there instead of `PROTECT`.
    # Why? If a product is deleted, reference should be removed.
    # (And just like in `Order.customer`, we can have a `deleted_product` product in the `Product` table.)
    # With the mosh code, any product can't be deleted ever which was ordered even once, since we'd not delete the orders ever.

    quantity = models.PositiveSmallIntegerField()

    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    # (definition same as `Product.price`)
    # We've this since price can be changed, we want to track the price at the time of order. (Important to not miss!)


class Address(models.Model):

    street = models.CharField(max_length=255)

    city = models.CharField(max_length=255)

    # If we want to allow only single address for a customer:
    # customer = models.OneToOneField(to=Customer, on_delete=models.CASCADE, primary_key=True)
    # `primary_key=True` because since we already have OneToOne relationship, we can use the customer only as a primary key

    # If we want to allow multiple addresses for a customer:
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)
    # this is one-to-many relationship
    # Here, we can't add `primary_key=True`, because `customer` column in this table would have duplicate vals.


class Cart(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4)
    # See Notes > Part 2 > 3. > [`Cart`] Problem with Default `id` Field

    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):

    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE)

    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        # Enforce Unique Product per Cart / Prevent duplicate cart items for same product:
        unique_together = [["cart", "product"]]


class Review(models.Model):

    text = models.TextField()

    date = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)

    # Keeping the fields different from mosh, his looks bad to me. Check the video "Building the Reviews API" for his fields.
