-- ====================================================================
-- AI STUDENT ASSISTANT AGENT - SUPABASE POSTGRESQL SCHEMA WITH RLS
-- ====================================================================

-- 1. PROFILES TABLE
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    course TEXT NOT NULL,
    branch TEXT NOT NULL,
    college TEXT,
    semester TEXT NOT NULL,
    graduation_year INTEGER,
    subjects_of_interest TEXT[] DEFAULT '{}',
    preferred_language TEXT DEFAULT 'English',
    profile_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    CONSTRAINT username_length_check CHECK (char_length(username) >= 3 AND char_length(username) <= 30),
    CONSTRAINT username_alphanumeric CHECK (username ~* '^[a-zA-Z0-9_]+$')
);

-- 2. CONVERSATIONS TABLE
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    subject TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 3. MESSAGES TABLE
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 4. STUDY PLANS TABLE
CREATE TABLE IF NOT EXISTS public.study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    plan_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 5. STUDY TASKS TABLE
CREATE TABLE IF NOT EXISTS public.study_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES public.study_plans(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    task_title TEXT NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    estimated_duration INTEGER DEFAULT 60, -- duration in minutes
    priority TEXT DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 6. QUIZ ATTEMPTS TABLE
CREATE TABLE IF NOT EXISTS public.quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty TEXT DEFAULT 'Medium' CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    questions_and_answers JSONB NOT NULL DEFAULT '[]'::jsonb,
    score NUMERIC(5, 2) NOT NULL,
    total_questions INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- ====================================================================
-- INDEXES FOR PERFORMANCE
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(LOWER(username));
CREATE INDEX IF NOT EXISTS idx_conversations_user ON public.conversations(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON public.messages(conversation_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_messages_user ON public.messages(user_id);
CREATE INDEX IF NOT EXISTS idx_study_plans_user ON public.study_plans(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_study_tasks_plan ON public.study_tasks(plan_id, due_date ASC);
CREATE INDEX IF NOT EXISTS idx_study_tasks_user ON public.study_tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user ON public.quiz_attempts(user_id, created_at DESC);

-- ====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ====================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_attempts ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Conversations Policies
DROP POLICY IF EXISTS "Users can view own conversations" ON public.conversations;
CREATE POLICY "Users can view own conversations"
    ON public.conversations FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create own conversations" ON public.conversations;
CREATE POLICY "Users can create own conversations"
    ON public.conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own conversations" ON public.conversations;
CREATE POLICY "Users can update own conversations"
    ON public.conversations FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own conversations" ON public.conversations;
CREATE POLICY "Users can delete own conversations"
    ON public.conversations FOR DELETE
    USING (auth.uid() = user_id);

-- Messages Policies
DROP POLICY IF EXISTS "Users can view own messages" ON public.messages;
CREATE POLICY "Users can view own messages"
    ON public.messages FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own messages" ON public.messages;
CREATE POLICY "Users can insert own messages"
    ON public.messages FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own messages" ON public.messages;
CREATE POLICY "Users can delete own messages"
    ON public.messages FOR DELETE
    USING (auth.uid() = user_id);

-- Study Plans Policies
DROP POLICY IF EXISTS "Users can view own study plans" ON public.study_plans;
CREATE POLICY "Users can view own study plans"
    ON public.study_plans FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own study plans" ON public.study_plans;
CREATE POLICY "Users can insert own study plans"
    ON public.study_plans FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own study plans" ON public.study_plans;
CREATE POLICY "Users can update own study plans"
    ON public.study_plans FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own study plans" ON public.study_plans;
CREATE POLICY "Users can delete own study plans"
    ON public.study_plans FOR DELETE
    USING (auth.uid() = user_id);

-- Study Tasks Policies
DROP POLICY IF EXISTS "Users can view own study tasks" ON public.study_tasks;
CREATE POLICY "Users can view own study tasks"
    ON public.study_tasks FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own study tasks" ON public.study_tasks;
CREATE POLICY "Users can insert own study tasks"
    ON public.study_tasks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own study tasks" ON public.study_tasks;
CREATE POLICY "Users can update own study tasks"
    ON public.study_tasks FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own study tasks" ON public.study_tasks;
CREATE POLICY "Users can delete own study tasks"
    ON public.study_tasks FOR DELETE
    USING (auth.uid() = user_id);

-- Quiz Attempts Policies
DROP POLICY IF EXISTS "Users can view own quiz attempts" ON public.quiz_attempts;
CREATE POLICY "Users can view own quiz attempts"
    ON public.quiz_attempts FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own quiz attempts" ON public.quiz_attempts;
CREATE POLICY "Users can insert own quiz attempts"
    ON public.quiz_attempts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own quiz attempts" ON public.quiz_attempts;
CREATE POLICY "Users can delete own quiz attempts"
    ON public.quiz_attempts FOR DELETE
    USING (auth.uid() = user_id);

-- ====================================================================
-- SECURE USERNAME-TO-EMAIL RESOLUTION FUNCTION
-- ====================================================================
-- This SECURITY DEFINER function securely resolves a lowercase username
-- to the corresponding registered email for authentication, without
-- giving client sessions broad access to query other users' profiles.
CREATE OR REPLACE FUNCTION public.get_email_by_username(p_username TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_email TEXT;
BEGIN
    SELECT email INTO v_email
    FROM public.profiles
    WHERE LOWER(username) = LOWER(TRIM(p_username))
    LIMIT 1;

    RETURN v_email;
END;
$$;

-- Grant execution to anon and authenticated roles
GRANT EXECUTE ON FUNCTION public.get_email_by_username(TEXT) TO anon, authenticated;

-- ====================================================================
-- TRIGGER: AUTOMATIC UPDATED_AT TIMESTAMP
-- ====================================================================
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_profiles_updated_at ON public.profiles;
CREATE TRIGGER trigger_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS trigger_conversations_updated_at ON public.conversations;
CREATE TRIGGER trigger_conversations_updated_at
    BEFORE UPDATE ON public.conversations
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS trigger_study_plans_updated_at ON public.study_plans;
CREATE TRIGGER trigger_study_plans_updated_at
    BEFORE UPDATE ON public.study_plans
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS trigger_study_tasks_updated_at ON public.study_tasks;
CREATE TRIGGER trigger_study_tasks_updated_at
    BEFORE UPDATE ON public.study_tasks
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
