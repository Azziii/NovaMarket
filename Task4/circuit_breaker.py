from locust import HttpUser, task, between

class CircuitBreakerUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @task(3)
    def fast(self):
        self.client.get("/logistics/fast")

    @task(2)
    def error(self):
        self.client.get("/logistics/error")

    @task(2)
    def slow(self):
        self.client.get("/logistics/slow")