"""
Load testing with Locust for the AI personalization system.

Usage:
    locust -f backend/tests/load_test.py --headless -u 100 -r 10 --run-time 60s

With UI:
    locust -f backend/tests/load_test.py

Options:
    -u: Number of users
    -r: Spawn rate (users/second)
    --run-time: Duration (e.g., 60s, 5m)
    --headless: Run without UI
"""

import random
import time
from locust import HttpUser, task, between
from locust.contrib.fasthttp import FastHttpUser


class PortfolioUser(HttpUser):
    """Simulates a user interacting with the portfolio"""

    wait_time = between(1, 5)  # Wait 1-5 seconds between requests

    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post(
            "/api/admin/login", json={"username": "admin", "password": "admin"}
        )

        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            self.token = None
            self.environment.runner.quit()

    def on_stop(self):
        """Cleanup when stopping"""
        pass

    @task(30)  # 30% of requests
    def get_personalization(self):
        """Get personalization rules (most common)"""
        user_id = f"user_{random.randint(1, 10000)}"
        response = self.client.get(
            f"/api/personalization?user_id={user_id}", name="/api/personalization"
        )

        # Track success/failure
        if response.status_code != 200:
            response.failure(f"Got {response.status_code}")

    @task(40)  # 40% of requests
    def create_event(self):
        """Create/track analytics events"""
        event_types = [
            "project_click",
            "skill_hover",
            "section_view",
            "contact_intent",
            "deep_read",
        ]

        event_name = random.choice(event_types)
        user_id = f"user_{random.randint(1, 10000)}"

        payload = {
            "event_name": event_name,
            "user_pseudo_id": user_id,
            "event_params": {"source": "load_test", "timestamp": int(time.time())},
            "event_timestamp": int(time.time() * 1000),
        }

        response = self.client.post("/api/events", json=payload, name="/api/events")

        if response.status_code not in [200, 201]:
            response.failure(f"Got {response.status_code}")

    @task(20)  # 20% of requests
    def search_events(self):
        """Search events in admin (authenticated)"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.get(
            "/api/admin/events/search",
            params={
                "hours": 24,
                "limit": random.randint(10, 100),
                "offset": random.randint(0, 50),
            },
            headers=headers,
            name="/api/admin/events/search",
        )

        if response.status_code != 200:
            response.failure(f"Got {response.status_code}")

    @task(10)  # 10% of requests
    def get_insights(self):
        """Get AI insights (authenticated)"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.get(
            "/api/admin/insights", headers=headers, name="/api/admin/insights"
        )

        if response.status_code != 200:
            response.failure(f"Got {response.status_code}")


class FastPortfolioUser(FastHttpUser):
    """Performance-optimized user (uses FastHttpUser)"""

    wait_time = between(1, 3)

    @task
    def get_health(self):
        """Simple health check"""
        self.client.get("/health")


# Configuration for different load scenarios
SCENARIOS = {
    "baseline": {"users": 10, "spawn_rate": 2, "duration": "60s"},
    "normal": {"users": 50, "spawn_rate": 5, "duration": "300s"},
    "stress": {"users": 200, "spawn_rate": 20, "duration": "600s"},
    "spike": {"users": 500, "spawn_rate": 100, "duration": "120s"},
}


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(level=logging.INFO)

    # Example: Run baseline scenario
    scenario = SCENARIOS.get(sys.argv[1] if len(sys.argv) > 1 else "normal")

    print(f"""
    Load Test Configuration:
    - Users: {scenario['users']}
    - Spawn rate: {scenario['spawn_rate']} users/second
    - Duration: {scenario['duration']}
    
    Run with:
        locust -f backend/tests/load_test.py \\
          -u {scenario['users']} \\
          -r {scenario['spawn_rate']} \\
          --run-time {scenario['duration']} \\
          --headless
    """)
