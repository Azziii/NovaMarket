from locust import HttpUser, task, between

class RateLimiterUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task
    def web(self):
        self.client.get("/api/", headers={"Client-Type": "web"})

    @task
    def mobile(self):
        self.client.get("/api/", headers={"Client-Type": "mobile"})