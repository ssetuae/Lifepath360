# API Documentation: Learning Compass

This document provides detailed information about the Learning Compass API endpoints, request/response formats, and authentication requirements.

## Base URL

Production: `https://learning-compass-api.render.com/api`
Development: `http://localhost:8000/api`

## Authentication

All API endpoints (except registration and login) require authentication using JWT tokens.

### Headers

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User

```
POST /users/register/
```

Request Body:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "student", // "student", "parent", "teacher"
  "grade": "G6" // Required only for students
}
```

Response (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "student",
  "grade": "G6"
}
```

#### Login

```
POST /users/login/
```

Request Body:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

Response (200 OK):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "student",
    "is_admin": false,
    "grade": "G6"
  }
}
```

#### Refresh Token

```
POST /users/token/refresh/
```

Request Body:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response (200 OK):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### User Management

#### Get Current User

```
GET /users/me/
```

Response (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "student",
  "is_admin": false,
  "grade": "G6",
  "date_joined": "2025-04-25T08:10:30Z"
}
```

#### Update User

```
PUT /users/me/
```

Request Body:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "grade": "G7" // Only for students
}
```

Response (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "user_type": "student",
  "is_admin": false,
  "grade": "G7",
  "date_joined": "2025-04-25T08:10:30Z"
}
```

### Assessment

#### Get Questions for Assessment

```
GET /questions/?grade=G6
```

Response (200 OK):
```json
[
  {
    "id": 1,
    "text": "How do you prefer to learn new information?",
    "category": "learning_style",
    "question_type": "MULTIPLE_CHOICE",
    "grade": "G6",
    "options": [
      {
        "id": 1,
        "text": "By reading books or articles"
      },
      {
        "id": 2,
        "text": "By listening to lectures or podcasts"
      },
      {
        "id": 3,
        "text": "By hands-on activities or experiments"
      },
      {
        "id": 4,
        "text": "By discussing with others"
      }
    ]
  },
  // More questions...
]
```

#### Submit Assessment

```
POST /assessments/
```

Request Body:
```json
{
  "grade": "G6",
  "responses": [
    {
      "question_id": 1,
      "selected_option_id": 3,
      "text_response": null
    },
    {
      "question_id": 2,
      "selected_option_id": null,
      "text_response": "I learn best when I can see visual diagrams and read explanations."
    },
    // More responses...
  ]
}
```

Response (201 Created):
```json
{
  "id": 1,
  "student": {
    "id": 1,
    "name": "John Doe"
  },
  "grade": "G6",
  "completion_date": "2025-04-25T09:30:45Z",
  "status": "COMPLETED"
}
```

### Results and Analysis

#### Get Assessment Results

```
GET /assessments/1/results/
```

Response (200 OK):
```json
{
  "assessment_id": 1,
  "student_name": "John Doe",
  "grade": "G6",
  "assessment_date": "2025-04-25T09:30:45Z",
  "learning_styles": {
    "primary": "visual",
    "secondary": "logical",
    "scores": {
      "visual": 8.5,
      "auditory": 6.2,
      "kinesthetic": 5.8,
      "logical": 7.9,
      "social": 6.5,
      "solitary": 5.1
    }
  },
  "cognitive_strengths": {
    "primary": "analytical",
    "secondary": "creative",
    "scores": {
      "analytical": 8.7,
      "creative": 7.8,
      "practical": 6.5,
      "memory": 7.2,
      "attention": 6.9
    }
  },
  "ideal_learning_environment": {
    "structure": "Structured environment with clear goals and visual aids",
    "social": "Mix of independent study and small group discussions",
    "pace": "Moderate pace with time for reflection",
    "feedback": "Regular, detailed feedback with visual examples"
  }
}
```

#### Get Recommendations

```
GET /recommendations/1/
```

Response (200 OK):
```json
{
  "assessment_id": 1,
  "student_name": "John Doe",
  "grade": "G6",
  "primary_learning_style": "visual",
  "recommended_courses": [
    {
      "id": 1,
      "title": "Visual Science Learning",
      "category": "Science",
      "description": "A course designed for visual learners focusing on scientific concepts through diagrams, videos, and visual experiments."
    },
    {
      "id": 2,
      "title": "Analytical Mathematics",
      "category": "Mathematics",
      "description": "Develops analytical thinking through problem-solving and visual mathematical concepts."
    },
    // More courses...
  ],
  "learning_path": "Focus on visual learning materials and analytical exercises...",
  "career_affinities": "Science, Engineering, Data Analysis...",
  "college_recommendations": "Programs with strong visual and analytical components...",
  "global_exams": "SAT, AP Physics, AP Calculus..."
}
```

### Reports

#### Get Summary Report

```
GET /reports/1/summary/
```

Response (200 OK):
```
Binary PDF data
```

Headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="summary_report_1.pdf"
```

#### Get Detailed Report

```
GET /reports/1/detailed/
```

Response (200 OK if payment completed, 402 Payment Required if not):
```
Binary PDF data
```

Headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="detailed_report_1.pdf"
```

### Payments

#### Create Payment Intent

```
POST /payments/create-intent/
```

Request Body:
```json
{
  "assessment_id": 1,
  "report_type": "detailed"
}
```

Response (200 OK):
```json
{
  "client_secret": "pi_3NkM7QHVu5i5JUTp1bPjgXnW_secret_vgMExQV4Wb9B9qs6SQysLOtZI",
  "amount": 2500, // $25.00
  "currency": "usd"
}
```

#### Confirm Payment

```
POST /payments/confirm/
```

Request Body:
```json
{
  "assessment_id": 1,
  "payment_intent_id": "pi_3NkM7QHVu5i5JUTp1bPjgXnW"
}
```

Response (200 OK):
```json
{
  "success": true,
  "report_url": "/api/reports/1/detailed/"
}
```

### AI Generation

#### Generate AI Questions (Admin Only)

```
POST /ai/generate_questions/
```

Request Body:
```json
{
  "count": 5,
  "grade": "G6",
  "categories": ["visual", "auditory", "kinesthetic", "logical", "social"]
}
```

Response (200 OK):
```json
{
  "success": true,
  "questions_generated": 5,
  "questions": [
    {
      "id": 10,
      "text": "When trying to remember information for a test, what helps you most?",
      "category": "visual",
      "question_type": "MULTIPLE_CHOICE",
      "grade": "G6",
      "options": [
        {"id": 40, "text": "Reading my notes and textbook"},
        {"id": 41, "text": "Listening to recordings of the lessons"},
        {"id": 42, "text": "Creating flashcards and diagrams"},
        {"id": 43, "text": "Teaching the material to someone else"}
      ]
    },
    // More questions...
  ]
}
```

### Admin Endpoints

#### Get All Users (Admin Only)

```
GET /admin/users/
```

Response (200 OK):
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "student",
    "is_active": true,
    "is_admin": false,
    "date_joined": "2025-04-25T08:10:30Z",
    "grade": "G6"
  },
  // More users...
]
```

#### Get All Assessments (Admin Only)

```
GET /admin/assessments/
```

Response (200 OK):
```json
[
  {
    "id": 1,
    "student": {
      "id": 1,
      "name": "John Doe"
    },
    "grade": "G6",
    "completion_date": "2025-04-25T09:30:45Z",
    "status": "COMPLETED",
    "payment_status": "COMPLETED"
  },
  // More assessments...
]
```

#### Get All Reports (Admin Only)

```
GET /admin/reports/
```

Response (200 OK):
```json
[
  {
    "assessment_id": 1,
    "student_name": "John Doe",
    "grade": "G6",
    "completion_date": "2025-04-25T09:30:45Z",
    "primary_learning_style": "visual",
    "payment_status": "COMPLETED"
  },
  // More reports...
]
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid request parameters",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized

```json
{
  "error": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
  "error": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
  "error": "Resource not found."
}
```

### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred."
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. The current limits are:

- Anonymous users: 20 requests per hour
- Authenticated users: 1000 requests per day
- Login attempts: 5 per 15-minute window

When a rate limit is exceeded, the API will respond with a 429 Too Many Requests status code.

## Webhooks

### Payment Webhook

```
POST /webhooks/stripe/
```

This endpoint receives webhook events from Stripe to process payment status updates.

## Data Models

### User

- id: Integer
- email: String
- password: String (hashed)
- first_name: String
- last_name: String
- user_type: String (student, parent, teacher)
- is_active: Boolean
- is_admin: Boolean
- date_joined: DateTime
- grade: String (for students only)

### Question

- id: Integer
- text: String
- category: String
- question_type: String (MULTIPLE_CHOICE, OPEN_ENDED)
- grade: String
- options: Array of Option objects (for MULTIPLE_CHOICE)

### Option

- id: Integer
- question_id: Integer
- text: String

### Assessment

- id: Integer
- student_id: Integer
- grade: String
- completion_date: DateTime
- status: String (IN_PROGRESS, COMPLETED)

### Response

- id: Integer
- assessment_id: Integer
- question_id: Integer
- selected_option_id: Integer (for MULTIPLE_CHOICE)
- text_response: String (for OPEN_ENDED)

### Analysis

- id: Integer
- assessment_id: Integer
- learning_styles: JSON
- cognitive_strengths: JSON
- ideal_learning_environment: JSON

### Recommendation

- id: Integer
- assessment_id: Integer
- recommended_courses: Array of Course IDs
- learning_path: String
- career_affinities: String
- college_recommendations: String
- global_exams: String

### Course

- id: Integer
- title: String
- description: String
- category: String
- grade_level: String
- learning_style: String
- duration: String
- price: Decimal

### Payment

- id: Integer
- assessment_id: Integer
- user_id: Integer
- amount: Decimal
- currency: String
- payment_intent_id: String
- status: String
- created_at: DateTime
- updated_at: DateTime
