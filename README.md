# AI Student Assistant Agent 🎓

A complete, production-grade AI Student Assistant Agent demonstrating all seven core components of modern AI Agent architecture:
1. **User Interface**: Intuitive Streamlit multi-tab interface with responsive navigation.
2. **Prompt Processing**: Pedagogical intent classification, academic context injection, and sliding context memory.
3. **Large Language Model**: Google Gemini API powered by the official `google-genai` SDK with retry logic and rate limit management.
4. **Memory Module**: Dual-layer architecture combining short-term session state with persistent Supabase PostgreSQL database tables.
5. **Tool Integration**: 11 internal Python tools for profile retrieval, conversational memory, PyMuPDF extraction, grounded document QA, notes generation, automated quiz grading, and study planning.
6. **Response Generation**: Structured formatting (2-mark, 5-mark, 10-mark answers, comparison tables, step-by-step algorithms, and cited document quotes).
7. **Deployment Platform**: Deployable on Streamlit Community Cloud, Cloud Run, or any Docker/container platform.

---

## 🚀 Key Features

- **Secure Authentication & Registration**:
  - Sign in with registered **username** or **email** and password.
  - Mandatory student academic profile (Full Name, Course, Branch, Semester, College, Graduation Year, Language Preferences).
  - Central authentication guard with Row-Level Security (RLS) enforcement.
- **AI Academic Chatbot**:
  - Answers academic questions tailored to the student's degree and semester.
  - Multi-format response styles: *Simple / Beginner*, *2-Mark Short Answer*, *5-Mark Exam Answer with Diagrams*, *10-Mark Comprehensive Exam Answer*, *Comparison Table*, and *Step-by-Step Solutions*.
  - Sliding context window for conversational memory.
- **PDF Study Assistant**:
  - Upload textbook chapters, syllabus, or lecture slides up to 15MB.
  - Extracts text page-by-page via PyMuPDF (`fitz`).
  - Detects scanned/image-only PDFs and provides friendly guidance.
  - Grounded question-answering with exact `[Page X]` source citations.
- **Exam Notes Generator**:
  - High-yield unit revision guides with definitions, core principles, tables, and exam tips.
  - One-click Markdown export / download.
- **Quiz Generator & Auto-Evaluator**:
  - Multiple Choice (MCQ), True/False, and Short Answer question generation.
  - Configurable difficulty (Easy, Medium, Hard).
  - **Deterministic scoring in Python** (no LLM arithmetic errors).
  - Detailed answer explanations and persistent attempt logging in Supabase.
- **Personalized Study Planner**:
  - AI schedule distribution across subjects and target exam deadlines.
  - Interactive task checklist with completion toggles and real progress bar.
- **True Stored Progress Dashboard**:
  - Real metrics calculated from Supabase: Active Plans, Completed Tasks, Completion Rate, and Average Quiz Score.

---

## 🛠️ Technology Stack

- **Language**: Python 3.10+ / 3.11+
- **Frontend**: Streamlit
- **LLM Provider**: Google Gemini API (`gemini-2.5-flash`) via `google-genai`
- **Database & Auth**: Supabase PostgreSQL with Row-Level Security (RLS)
- **PDF Processing**: PyMuPDF (`fitz`)
- **Data & Validation**: Pydantic v2, Pandas
- **Testing**: Pytest

---

## 📂 Project Structure

```text
├── app.py                     # Main Streamlit application entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore file
├── README.md                  # Comprehensive documentation
│
├── auth/                      # Authentication & Session Security
│   ├── __init__.py
│   ├── auth_service.py        # Supabase Auth, username resolution & validation
│   ├── login.py               # Streamlit Login UI component
│   ├── register.py            # Registration & Profile Completion UI
│   └── session.py             # Central AuthState Guard
│
├── agent/                     # AI Agent Core Engine
│   ├── __init__.py
│   ├── gemini_client.py       # Official google-genai wrapper with retry logic
│   ├── prompts.py             # Pedagogical system instructions & templates
│   ├── prompt_processor.py    # Intent classifier & context assembler
│   ├── response_formatter.py  # Markdown polisher & citation formatter
│   └── academic_agent.py      # Core agent coordinating 11 tools
│
├── database/                  # Supabase PostgreSQL Integration
│   ├── __init__.py
│   ├── supabase_client.py     # Client initialization & connection verification
│   ├── repositories.py        # DAOs for profiles, convos, notes, plans, quizzes
│   └── schema.sql             # Full database schema with Row-Level Security
│
├── services/                  # Business Logic Services
│   ├── __init__.py
│   ├── pdf_service.py         # PyMuPDF extraction, chunking & retrieval
│   ├── memory_service.py      # Short-term session & persistent sync
│   ├── quiz_service.py        # Schema validation & Python scoring
│   └── study_plan_service.py  # Scheduling & task timeline validation
│
├── components/                # Streamlit Page Views
│   ├── __init__.py
│   ├── dashboard.py           # Student Dashboard with real metrics
│   ├── chat.py                # Academic Chat with format selector
│   ├── pdf_assistant.py       # Grounded PDF Q&A with page citations
│   ├── notes_generator.py     # Exam revision notes generator
│   ├── quiz_generator.py      # Interactive practice test with grading
│   ├── study_planner.py       # Multi-subject task checklist & progress
│   └── profile.py             # Student profile management
│
└── tests/                     # Automated Test Suite (32 Passing Tests)
    ├── __init__.py
    ├── test_auth_validation.py
    ├── test_prompt_processing.py
    ├── test_pdf_service.py
    ├── test_quiz_service.py
    └── test_memory.py
```

---

## ⚙️ Setup & Installation Instructions

### 1. Clone the repository and install dependencies

```bash
# Clone the repository
git clone <repository_url>
cd ai-student-assistant

# (Recommended) Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Supabase PostgreSQL & Auth

1. Create a free project at [supabase.com](https://supabase.com).
2. Navigate to **SQL Editor** in the Supabase Dashboard.
3. Open `database/schema.sql` from this repository, paste the entire contents into the SQL Editor, and click **Run**.
   - This sets up `profiles`, `conversations`, `messages`, `study_plans`, `study_tasks`, and `quiz_attempts` with strict Row-Level Security (RLS) policies and the secure `get_email_by_username` RPC function.
4. Go to **Project Settings** > **API**:
   - Copy the **Project URL**.
   - Copy the **anon / public key**.

### 3. Configure Gemini AI API Key

1. Generate a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 4. Create your `.env` file

Copy the provided `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```ini
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Supabase Database & Auth
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

---

## 🏃 Running the Application

Launch the Streamlit application using the local run command:

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full automated test suite using `pytest`:

```bash
python3 -m pytest tests/ -v
```

All 32 test cases test:
- Email, username, password complexity, and registration validation
- Pedagogical prompt construction and intent classification
- PyMuPDF extraction, chunking, and lexical passage retrieval
- Deterministic quiz scoring arithmetic and schema validation
- Conversational sliding memory window and database mock isolation

---

## 🛡️ Security & Privacy Architecture

- **Row-Level Security (RLS)**: Enforced on all tables; students can strictly read and write only records where `auth.uid() = user_id`.
- **Encrypted Authentication**: Passwords are encrypted and handled exclusively by Supabase Auth (Argon2/bcrypt); no passwords are stored in application tables.
- **Secure Username Login**: A PostgreSQL `SECURITY DEFINER` function translates usernames into emails without exposing public directories.
- **Untrusted Document Defense**: Text extracted from user-uploaded PDFs is encapsulated within untrusted document boundaries to prevent prompt-injection attacks.
- **Zero Hallucination Citations**: The PDF assistant is instructed to state lack of information rather than inventing page numbers.
