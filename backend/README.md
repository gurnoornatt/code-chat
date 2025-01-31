# AI Tutor Backend

This is the backend server for the AI Tutor application, built with FastAPI and Supabase.

## Features

- User Authentication (JWT-based)
- Chat System with AI Tutor
- File Management
- Educational Resources Management
- Role-Based Access Control
- Comprehensive Test Suite

## Prerequisites

- Python 3.8+
- Supabase Account
- (Optional) Sentry Account for error tracking

## Setup

1. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
- Add your Supabase URL and anonymous key
- Generate a secure JWT secret key
- (Optional) Add your Sentry DSN
- Configure other variables as needed

## Database Setup

1. Create the following tables in your Supabase database:

### Students Table
```sql
create table students (
  id uuid default uuid_generate_v4() primary key,
  email text unique not null,
  password text not null,
  name text not null,
  grade_level text not null,
  school text not null,
  created_at timestamp with time zone default timezone('utc'::text, now())
);
```

### Questions Table
```sql
create table questions (
  id uuid default uuid_generate_v4() primary key,
  student_id uuid references students(id),
  question_text text not null,
  code_context text,
  resolved boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now())
);
```

### Conversations Table
```sql
create table conversations (
  id uuid default uuid_generate_v4() primary key,
  student_id uuid references students(id),
  question_id uuid references questions(id),
  message_type text not null check (message_type in ('student', 'ai')),
  message_text text not null,
  created_at timestamp with time zone default timezone('utc'::text, now())
);
```

### Files Table
```sql
create table files (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  content_type text not null,
  size integer not null,
  student_id uuid references students(id),
  storage_path text not null,
  created_at timestamp with time zone default timezone('utc'::text, now())
);
```

### Resources Table
```sql
create table resources (
  id uuid default uuid_generate_v4() primary key,
  title text not null,
  description text not null,
  content text not null,
  file_type text not null,
  tags text[] default '{}',
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);
```

### Feedback Table
```sql
create table feedback (
  id uuid default uuid_generate_v4() primary key,
  student_id uuid references students(id),
  response_id uuid references conversations(id),
  rating integer not null check (rating between 1 and 5),
  comment text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);
```

## Running the Server

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Running Tests
```bash
pytest
```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- POST `/auth/register` - Register a new student
- POST `/auth/login` - Login and get JWT token

### Chat
- POST `/chat/questions` - Create a new question
- GET `/chat/questions` - Get all questions for current student
- GET `/chat/conversations/{question_id}` - Get conversation history
- POST `/chat/responses/{question_id}/feedback` - Submit feedback for AI response

### Files
- POST `/files/upload` - Upload a file
- GET `/files/list` - List student's files
- GET `/files/{file_id}/content` - Get file content
- DELETE `/files/{file_id}` - Delete a file

### Resources
- POST `/resources` - Create a resource (admin only)
- GET `/resources` - List resources
- GET `/resources/{resource_id}` - Get specific resource
- PUT `/resources/{resource_id}` - Update resource (admin only)
- DELETE `/resources/{resource_id}` - Delete resource (admin only)

## Security Considerations

1. Always use HTTPS in production
2. Keep your JWT secret key secure
3. Never commit the `.env` file
4. Regularly update dependencies
5. Monitor Sentry for errors
6. Implement rate limiting in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 