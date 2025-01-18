"""
This module defines the models for the URL Shortener application.

Classes:
- URL: Represents the shortened URL and its associated data.
- Log: Tracks access logs for the shortened URLs.
"""

from django.db import models


class URL(models.Model):
    """
    Represents a shortened URL.

    Fields:
    - original_url (URLField): The original, full-length URL provided by the user.
    - shortened_url (CharField): A unique, shortened version of the URL.
    - creation_timestamp (DateTimeField): The timestamp when the shortened URL was created.
    - expiration_timestamp (DateTimeField): The timestamp when the shortened URL will expire.
    - access_count (PositiveIntegerField): The number of times the shortened URL has been accessed.

    Methods:
    - __str__: Returns a string representation of the shortened URL and original URL.
    """

    objects = models.Manager()

    original_url = models.URLField(max_length=2048)
    shortened_url = models.CharField(max_length=50, unique=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    expiration_timestamp = models.DateTimeField(null=True, blank=True)
    is_password_protected = models.BooleanField(default=False)
    password = models.CharField(max_length=50, null=True, blank=True)
    access_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.shortened_url}"


class Log(models.Model):
    """
    Tracks access logs for a shortened URL.

    Fields:
    - url (ForeignKey): A reference to the URL model.
    - access_timestamp (DateTimeField): The timestamp when the URL was accessed.
    - ip_address (GenericIPAddressField): The IP address of the user who accessed the URL.

    Methods:
    - __str__: Returns a string representation of the log entry.
    """

    objects = models.Manager()

    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name="logs")
    access_timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Log for {str(self.url)} at {self.access_timestamp}"
