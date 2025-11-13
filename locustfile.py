
from locust import HttpUser, task, between
import os
import io

class FileStorageUser(HttpUser):
    wait_time = between(1, 3)  # seconds between tasks

    @task
    def get_root(self):
        """Test the root endpoint"""
        self.client.get("/")

    @task
    def get_health(self):
        """Test the health endpoint"""
        self.client.get("/health")

    @task
    def upload_file(self):
        """Upload a small file to /files"""
        content = b"load test file content"
        files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}
        self.client.post("/files", files=files)

    @task
    def list_files(self):
        """List stored files"""
        self.client.get("/files")
