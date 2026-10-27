# AI Student Assistant Agent

A web-based AI Student Assistant designed to help students with academic questions, exam preparation, PDF analysis, notes generation, quizzes, and study planning.

## Key Features

- **Authentication and Registration:** Student login using username or email and password, with academic profile management.
- **AI Academic Chatbot:** Academic answers in simple, 2-mark, 5-mark, and 10-mark formats, along with comparison tables and step-by-step solutions.
- **PDF Study Assistant:** Upload and analyze study materials, extract text, and answer questions with page references.
- **Exam Notes Generator:** Generate revision notes organized around important concepts and topics.
- **Quiz Generator:** Generate MCQs, true/false questions, and short-answer questions with automatic evaluation.
- **Personalized Study Planner:** Organize subjects, deadlines, and tasks with progress tracking.
- **Student Dashboard:** Display study plans, task completion, and quiz performance.
- **Conversational Memory:** Maintain relevant context during academic conversations.

## Technology Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** Node.js, TypeScript (`server.ts`)
- **AI:** Google Gemini API
- **Database and Authentication:** Supabase
- **Additional Python Components:** Python services for academic assistance, PDF processing, quizzes, and study planning
- **Testing:** Pytest and TypeScript tooling

## Project Structure

```text
Ai-assistant/
├── agent/
├── auth/
├── components/
├── data/
├── database/
├── public/
├── services/
├── src/
├── tests/
├── app.py
├── index.html
├── package.json
├── requirements.txt
├── server.ts
├── tsconfig.json
└── vite.config.ts
```

## Prerequisites

Install the following before running the application:

- Node.js and npm
- Python, if you use the Python components
- Google Gemini API key
- Supabase project credentials, if required by your configured services

## Setup and Installation

### 1. Install frontend dependencies

```bash
npm install
```

### 2. Configure environment variables

Create a local `.env` file based on `.env.example`. Add your required Gemini and Supabase credentials using the variable names expected by your application.

**Security:** Never commit `.env` or publish API keys. Keep `.env.example` limited to placeholder values.

### 3. Run the frontend development server

```bash
npm run dev
```

### 4. Build the frontend for production

```bash
npm run build
```

Vite generates the production frontend in the `dist/` directory.

### 5. Run the Node.js server

The project defines the following scripts:

```bash
npm start
```

Use this command when you need to run `server.ts`. Configure the required environment variables before starting the server.

### 6. Run the Python application

If you use the Streamlit application and its Python components, install the dependencies from `requirements.txt` and run:

```bash
streamlit run app.py
```

## Running Tests

Run the Python tests with:

```bash
python -m pytest tests/ -v
```

Run the TypeScript check with:

```bash
npm run lint
```

## Deployment

The React frontend can be built with Vite and deployed to Vercel. Configure the Vercel project to use the correct project root, build command (`npm run build`), and output directory (`dist`).

The Node.js and Python components may require separate backend deployment and environment configuration. A successful frontend deployment does not automatically deploy these services.

## Security

- Keep API keys and credentials in environment variables.
- Do not commit `.env` files.
- Apply appropriate authentication and database access policies.
- Validate user inputs and uploaded documents.
- Protect backend endpoints and sensitive operations.
