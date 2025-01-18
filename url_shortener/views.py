"""
This module contains the views for the URL shortener application.
It includes the API endpoint for shortening URLs.

Classes:
- ShortenURLView: Endpoint to shorten original URLs.
- RedirectURLView: Endpoint to redirect to original URLs.
- AnalyticsURLView: Endpoint to provide analytics data for shortened URLs.
"""

import hashlib
from datetime import datetime

import pytz
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from url_shortener.models import URL, Log


class ShortenURLView(APIView):
    """
    API endpoint that allows users to shorten URLs.
    """

    def post(self, request):
        """
        Handle POST requests to shorten a URL.

        Args:
            request (Request): The request object containing the URL to be shortened.

        Returns:
            Response: A response object containing the shortened URL or an error message.
        """
        # Get the URL from the request data.
        url = request.data.get("url")
        # If the URL is not provided, return a 400 response.
        if not url:
            return Response(
                {
                    "error": "This field is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the URL is an empty string.
        if url.strip() == "":
            return Response(
                {
                    "error": "URL cannot be an empty string.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(url) > 2048:
            return Response(
                {
                    "error": "URL length exceeds the maximum limit of 2048 characters.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        validator = URLValidator()
        try:
            # Validate the URL.
            validator(url)
        except ValidationError:
            return Response(
                {
                    "error": "Invalid URL.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the expiration timestamp is provided and is in the future.
        current_timestamp = timezone.now()
        expiration_timestamp = request.data.get("expiration_timestamp")
        if expiration_timestamp:
            try:
                naive_datetime = datetime.strptime(
                    expiration_timestamp, "%Y-%m-%d %H:%M:%S"
                )
                tz = pytz.timezone("Asia/Kolkata")
                expiration_timestamp = timezone.make_aware(naive_datetime, tz)
                if expiration_timestamp < current_timestamp:
                    return Response(
                        {
                            "error": "Expiration timestamp must be in the future.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except ValueError:
                return Response(
                    {
                        "error": "Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            finally:
                pass
        else:
            expiration_timestamp = current_timestamp + timezone.timedelta(days=1)

        # Check if the URL needs to be password protected.
        password = request.data.get("password")
        is_password_protected = bool(password)
        print(is_password_protected)

        # Generate a unique hash for the URL.
        unique_hash = hashlib.md5(f"{url}{current_timestamp}".encode()).hexdigest()[:8]
        shortened_url = f"http://localhost:8000/{unique_hash}/"

        # Check for duplicate hash and regenerate if necessary.
        while URL.objects.filter(shortened_url=shortened_url).exists():
            unique_hash = hashlib.md5(f"{url}{timezone.now()}".encode()).hexdigest()[:8]
            shortened_url = f"http://localhost:8000/{unique_hash}/"

        try:
            # Save the shortened URL to the database.
            url_instance = URL(
                original_url=url,
                shortened_url=shortened_url,
                creation_timestamp=current_timestamp,
                expiration_timestamp=expiration_timestamp,
                is_password_protected=is_password_protected,
                password=password if is_password_protected else None,
            )
            url_instance.save()
        except Exception as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Return the shortened URL and expiration timestamp in the response.
        return Response(
            {
                "shortened_url": shortened_url,
                "expiration_timestamp": expiration_timestamp,
            },
            status=status.HTTP_201_CREATED,
        )


class RedirectURLView(APIView):
    """
    API endpoint that redirects users to the original URL.
    """

    def get(self, request, short_url):
        """
        Handle GET requests to retrieve all shortened URLs.

        Args:
            request (Request): The request object.

        Returns:
            Response: A response object containing a list of shortened URLs.
        """

        # If the URL is not found, return a 400 response.
        if not short_url:
            return Response(
                {
                    "error": "This field is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the URL instance from the database.
        url_instance = get_object_or_404(
            URL, shortened_url=f"http://localhost:8000/{short_url}/"
        )

        # If the URL is password protected, check if the password is provided.
        if url_instance.is_password_protected:
            password = request.query_params.get("password")

            # If password is not provided, return a 401 response.
            if not password:
                return Response(
                    {
                        "error": "This URL is password protected. Please provide a password.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # If the password is incorrect, return a 401 response.
            if password != url_instance.password:
                return Response(
                    {
                        "error": "Incorrect password.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # If the URL has expired, return a 410 response.
        if url_instance.expiration_timestamp < timezone.now():
            return Response(
                {
                    "error": "This URL has expired.",
                },
                status=status.HTTP_410_GONE,
            )

        # Increment the access count for the URL.
        url_instance.access_count += 1
        url_instance.save()

        # Log the access to the database.
        log_instance = Log(
            url=url_instance,
            access_timestamp=timezone.now(),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        log_instance.save()

        # Redirect the user to the original URL.
        return redirect(url_instance.original_url)


class AnalyticsURLView(APIView):
    """
    API endpoint that provides analytics data for shortened URLs.
    """

    def get(self, request, short_url):
        """
        Handle GET requests to retrieve analytics data for shortened URLs.

        Args:
            request (Request): The request object.

        Returns:
            Response: A response object containing analytics data.
        """

        # If the URL is not found, return a 400 response.
        if not short_url:
            return Response(
                {
                    "error": "This field is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the URL instance from the database.
        url_instance = get_object_or_404(
            URL, shortened_url=f"http://localhost:8000/{short_url}/"
        )

        # If the URL is password protected, check if the password is provided.
        if url_instance.is_password_protected:
            password = request.query_params.get("password")

            # If password is not provided, return a 401 response.
            if not password:
                return Response(
                    {
                        "error": "This URL is password protected. Please provide a password.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # If the password is incorrect, return a 401 response.
            if password != url_instance.password:
                return Response(
                    {
                        "error": "Incorrect password.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # Get the access logs for the URL.
        log_instance = list(Log.objects.filter(url=url_instance))
        log_data = [
            {
                "short_url": str(log.url),
                "access_timestamp": log.access_timestamp,
                "ip_address": log.ip_address,
            }
            for log in log_instance
        ]

        # Return the analytics data in the response.
        return Response(
            {"access_count": url_instance.access_count, "logs": log_data},
            status=status.HTTP_200_OK,
        )
