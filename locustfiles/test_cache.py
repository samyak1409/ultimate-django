from locust import HttpUser, task


class AutomatedUser(HttpUser):

    host = "http://127.0.0.1:8000"

    @task
    def test_cache(self):
        self.client.get(url="/playground/test-cache2/")
