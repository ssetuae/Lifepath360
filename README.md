# Learning Compass: AI-Driven Diagnostic Program for K-12 Students

## Overview

Learning Compass is a comprehensive web application developed for Shining Star Education Training LLC that evaluates K-12 students' learning styles and provides personalized recommendations. The system uses AI to generate grade-specific questions, analyze responses, and create detailed reports that help students, parents, and educators understand individual learning preferences and strengths.

## Features

- **User Authentication**: Secure registration and login for students, parents, teachers, and administrators
- **Grade-Specific Assessments**: Tailored diagnostic questionnaires for each grade level (K-12)
- **AI-Driven Questions**: Dynamic question generation using OpenAI's API for relevance and freshness
- **Learning Style Analysis**: Comprehensive evaluation of visual, auditory, kinesthetic, logical, social, and solitary learning preferences
- **Cognitive Strength Assessment**: Analysis of analytical, creative, practical, memory, and attention abilities
- **NLP Response Analysis**: Natural language processing for open-ended question responses
- **Dual Report System**: 
  - Free summary report available immediately after assessment
  - Detailed 20-30 page report available after payment
- **Course Recommendations**: Personalized suggestions based on learning style and cognitive strengths
- **Admin Dashboard**: Comprehensive management of questions, users, reports, and courses
- **Data Security**: Role-based access control, encryption, and audit logging

## Technical Architecture

### Backend

- **Framework**: Django with Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT-based authentication with role-based access control
- **AI Integration**: OpenAI API for question generation and NLP analysis
- **PDF Generation**: WeasyPrint for creating colorful, detailed reports
- **Payment Processing**: Stripe integration for report purchases

### Frontend

- **Framework**: React with TypeScript
- **UI Components**: Material-UI for responsive design
- **State Management**: React Context API
- **Data Visualization**: Chart.js for learning style profiles and cognitive strength analysis
- **Routing**: React Router for navigation

### Deployment

- **Platform**: Render
- **CI/CD**: GitHub integration for continuous deployment
- **Database**: Render PostgreSQL service
- **Static Files**: Whitenoise for static file serving

## User Roles

1. **Students**: Take assessments, view results, purchase detailed reports
2. **Parents**: View their children's assessments and results
3. **Teachers**: View student results, manage assessments
4. **Administrators**: Full system access, manage questions, users, and courses

## Assessment Process

1. User registers and logs in
2. User selects their grade level
3. System presents AI-generated questions specific to the grade level
4. User completes the assessment
5. System analyzes responses using AI and NLP
6. Free summary report is generated immediately
7. User can purchase the detailed report for comprehensive insights

## Security Measures

- JWT authentication with token rotation
- Role-based access control
- Data encryption for sensitive information
- Comprehensive audit logging
- HTTPS enforcement
- Password strength validation
- Rate limiting to prevent brute force attacks

## Installation and Setup

### Prerequisites

- Python 3.10+
- Node.js 20+
- Git

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/shiningstar/learning-compass.git
   cd learning-compass
   ```

2. Create and activate a virtual environment:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.sample .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd ../frontend/learning-compass-ui
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   ```
   cp .env.sample .env
   # Edit .env with your configuration
   ```

4. Start the development server:
   ```
   npm start
   ```

## Deployment

The application is configured for deployment on Render. See the DEPLOYMENT.md file for detailed instructions.

## Testing

Run the automated test suite:

```
./test.sh
```

This will test both backend and frontend functionality.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Contact

For support or inquiries, please contact Shining Star Education Training LLC.

---

© 2025 Shining Star Education Training LLC. All rights reserved.
