from locust import HttpUser, task, between
from random import randint


class AutomatedUser(HttpUser):

    host = "http://127.0.0.1:8000"
    wait_time = between(1, 10)

    def on_start(self) -> None:
        response = self.client.post(url="/store/carts/")
        self.cart_id = response.json()["id"]

    @task(weight=2)
    def view_products(self):
        collection_id = randint(1, 10)
        self.client.get(
            url=f"/store/products/?collection_id={collection_id}",
            name="store/products/?collection_id",
        )

    @task(weight=4)
    def view_product(self):
        product_id = randint(1, 1000)
        self.client.get(
            url=f"/store/products/{product_id}/",
            name="store/products/:id",
        )

    @task(weight=1)
    def add_to_cart(self):
        product_id = randint(1, 10)
        self.client.post(
            url=f"/store/carts/{self.cart_id}/items/",
            json={"product": product_id, "quantity": 1},
            name="store/carts/:id/items",
        )
