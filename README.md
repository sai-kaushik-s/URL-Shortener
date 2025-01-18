# Python Task - SODIO

## Project Description

A Python-based URL shortener system that creates shortened URLs with expiration functionality and usage analytics tracking. The system uses SQLite for data storage and provides REST API interfaces.

## Installation

1. Navigate to the project directory:
   ```sh
   cd ShortenURL
   ```
2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

To run the server, use the following command:

1. Make migrations
   ```sh
   ./setup.sh
   ```
2. Run the Django server
   ```sh
   python manage.py runserver
   ```

## Features

- URL shortening with unique identifiers
- Customizable URL expiration (default: 24 hours)
- Usage analytics tracking (access count, timestamps, IP addresses)
- Password protection for sensitive URLs (optional)
- SQLite database for persistent storage
- RESTful API endpoints for all operations

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Create Shortened URL

Create a new shortened URL with optional expiration and password protection.

**Endpoint:** `/shorten/`  
**Method:** `POST`  
**Content-Type:** `application/json`

#### Request Body

| Field                | Type   | Required | Description                                          |
| -------------------- | ------ | -------- | ---------------------------------------------------- |
| url                  | string | Yes      | The original URL to be shortened                     |
| expiration_timestamp | string | No       | Expiration timestamp in format "YYYY-MM-DD HH:MM:SS" |
| password             | string | No       | Optional password protection for the URL             |

#### Example Request

```json
{
  "url": "https://example.com",
  "expiration_timestamp": "2025-01-19 10:00:00",
  "password": "optional_password"
}
```

#### Responses

##### 201 Created

```json
{
  "shortened_url": "http://localhost:8000/abcd1234/",
  "expiration_timestamp": "2025-01-19 10:00:00"
}
```

##### 400 Bad Request

```json
{
  "error": "This field is required."
}
```

```json
{
  "error": "Expiration timestamp must be in the future."
}
```

### 2. Access Shortened URL

Redirect to the original URL associated with a shortened URL.

**Endpoint:** `/<str:short_url>/`  
**Method:** `GET`

#### Request Parameters

| Parameter | Type   | Required | Description                           |
| --------- | ------ | -------- | ------------------------------------- |
| short_url | string | Yes      | The shortened URL identifier          |
| password  | string | No       | Required if URL is password protected |

#### Responses

##### 302 Found

Redirects to the original URL

##### 400 Bad Request

```json
{
  "error": "This field is required."
}
```

##### 401 Unauthorized

```json
{
  "error": "This URL is password protected. Please provide a password."
}
```

```json
{
  "error": "Incorrect password."
}
```

##### 410 Gone

```json
{
  "error": "This URL has expired."
}
```

### 3. Get URL Analytics

Retrieve analytics data for a specific shortened URL.

**Endpoint:** `/analytics/<str:short_url>/`  
**Method:** `GET`

#### Request Parameters

| Parameter | Type   | Required | Description                           |
| --------- | ------ | -------- | ------------------------------------- |
| short_url | string | Yes      | The shortened URL identifier          |
| password  | string | No       | Required if URL is password protected |

#### Example Response

##### 200 OK

```json
{
  "access_count": 10,
  "logs": [
    {
      "short_url": "http://localhost:8000/abcd1234/",
      "access_timestamp": "2025-01-18T10:00:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

##### 400 Bad Request

```json
{
  "error": "This field is required."
}
```

##### 401 Unauthorized

```json
{
  "error": "This URL is password protected. Please provide a password."
}
```

```json
{
  "error": "Incorrect password."
}
```

## Contact

For any questions or inquiries, please contact:

- Name: Sai Kaushik S
- Email: saikaushik609@gmail.com
