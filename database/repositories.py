"""Database Repositories for Student Data.

Provides strongly typed data access operations for profiles, conversations,
messages, study plans, study tasks, and quiz attempts.
All database access is strictly scoped to the authenticated user ID.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from database.supabase_client import get_supabase_client


class ProfileRepository:
    """Repository for student profile data."""

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        return self._client or get_supabase_client()

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve student profile by user ID."""
        if not self.client:
            return None
        try:
            res = self.client.table("profiles").select("*").eq("id", user_id).limit(1).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"[ProfileRepo] Error fetching profile: {e}")
            return None

    def create_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Create student profile record."""
        if not self.client:
            return False
        try:
            payload = {
                "id": user_id,
                "username": profile_data.get("username", "").strip(),
                "email": profile_data.get("email", "").strip().lower(),
                "full_name": profile_data.get("full_name", "").strip(),
                "course": profile_data.get("course", "").strip(),
                "branch": profile_data.get("branch", "").strip(),
                "college": profile_data.get("college", "").strip(),
                "semester": str(profile_data.get("semester", "")).strip(),
                "graduation_year": profile_data.get("graduation_year"),
                "subjects_of_interest": profile_data.get("subjects_of_interest", []),
                "preferred_language": profile_data.get("preferred_language", "English"),
                "profile_completed": True,
            }
            res = self.client.table("profiles").insert(payload).execute()
            return bool(res.data)
        except Exception as e:
            print(f"[ProfileRepo] Error creating profile: {e}")
            return False

    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update existing profile."""
        if not self.client:
            return False
        try:
            res = self.client.table("profiles").update(profile_data).eq("id", user_id).execute()
            return bool(res.data)
        except Exception as e:
            print(f"[ProfileRepo] Error updating profile: {e}")
            return False

    def resolve_username_to_email(self, username: str) -> Optional[str]:
        """Securely resolve username to email via Supabase RPC function."""
        if not self.client or not username:
            return None
        try:
            # Calls the SECURITY DEFINER get_email_by_username function
            res = self.client.rpc("get_email_by_username", {"p_username": username.strip()}).execute()
            return res.data if res.data else None
        except Exception as e:
            print(f"[ProfileRepo] Error resolving username: {e}")
            return None


class ConversationRepository:
    """Repository for student AI chat conversations."""

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        return self._client or get_supabase_client()

    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent conversations for the user."""
        if not self.client:
            return []
        try:
            res = (
                self.client.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .limit(limit)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"[ConvRepo] Error fetching conversations: {e}")
            return []

    def create_conversation(self, user_id: str, title: str, subject: Optional[str] = None) -> Optional[str]:
        """Create a new conversation session and return its ID."""
        if not self.client:
            return None
        try:
            res = (
                self.client.table("conversations")
                .insert({
                    "user_id": user_id,
                    "title": title[:100],
                    "subject": subject,
                })
                .execute()
            )
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            print(f"[ConvRepo] Error creating conversation: {e}")
            return None

    def delete_conversation(self, user_id: str, conv_id: str) -> bool:
        """Delete conversation and cascaded messages."""
        if not self.client:
            return False
        try:
            res = self.client.table("conversations").delete().eq("id", conv_id).eq("user_id", user_id).execute()
            return bool(res.data)
        except Exception as e:
            print(f"[ConvRepo] Error deleting conversation: {e}")
            return False


class MessageRepository:
    """Repository for conversation messages."""

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        return self._client or get_supabase_client()

    def get_conversation_messages(self, user_id: str, conv_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch messages in chronological order."""
        if not self.client:
            return []
        try:
            res = (
                self.client.table("messages")
                .select("*")
                .eq("conversation_id", conv_id)
                .eq("user_id", user_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"[MessageRepo] Error fetching messages: {e}")
            return []

    def save_message(
        self, user_id: str, conv_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save a new chat message."""
        if not self.client:
            return False
        try:
            payload = {
                "conversation_id": conv_id,
                "user_id": user_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
            }
            res = self.client.table("messages").insert(payload).execute()
            return bool(res.data)
        except Exception as e:
            print(f"[MessageRepo] Error saving message: {e}")
            return False


class StudyPlanRepository:
    """Repository for study plans."""

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        return self._client or get_supabase_client()

    def get_user_plans(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch all study plans for the user."""
        if not self.client:
            return []
        try:
            res = (
                self.client.table("study_plans")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"[StudyPlanRepo] Error fetching plans: {e}")
            return []

    def create_plan(
        self, user_id: str, title: str, subject: str, start_date: str, end_date: str, plan_data: Dict[str, Any]
    ) -> Optional[str]:
        """Create a new study plan and return its ID."""
        if not self.client:
            return None
        try:
            res = (
                self.client.table("study_plans")
                .insert({
                    "user_id": user_id,
                    "title": title,
                    "subject": subject,
                    "start_date": start_date,
                    "end_date": end_date,
                    "plan_data": plan_data,
                })
                .execute()
            )
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            print(f"[StudyPlanRepo] Error creating plan: {e}")
            return None

    def delete_plan(self, user_id: str, plan_id: str) -> bool:
        """Delete a study plan."""
        if not self.client:
            return False
        try:
            res = self.client.table("study_plans").delete().eq("id", plan_id).eq("user_id", user_id).execute()
            return bool(res.data)
        except Exception as e:
            print(f"[StudyPlanRepo] Error deleting plan: {e}")
            return False


class StudyTaskRepository:
    """Repository for individual study tasks within plans."""

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        return self._client or get_supabase_client()

    def get_plan_tasks(self, user_id: str, plan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch tasks, optionally filtered by plan."""
        if not self.client:
            return []
        try:
            query = self.client.table("study_tasks").select("*").eq("user_id", user_id)
            if plan_id:
                query = query.eq("plan_id", plan_id)
            res = query.order("due_date", desc=False).execute()
            return res.data or []
        except Exception as e:
            print(f"[StudyTaskRepo] Error fetching tasks: {e}")
            return []

    def create_task(
        self,
        user_id: str,
        plan_id: str,
        task_title: str,
        due_date: str,
        description: str = "",
        duration: int = 60,
        priority: str = "Medium",
    ) -> Optional[str]:
        """Create a new study task."""
        if not self.client:
            return None
        try:
            res = (
                self.client.table("study_tasks")
                .insert({
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "task_title": task_title,
                    "description": description,
                    "due_date": due_date,
                    "estimated_duration": duration,
                    "priority": priority,
                    "status": "pending",
                })
                .execute()
            )
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            print(f"[StudyTaskRepo] Error creating task: {e}")
            return None

    def update_task_status(self, user_id: str, task_id: str, status: str) -> bool:
        """Update task completion status."""
        if not self.client:
            return False
        try:
            res = (
                self.client.table("study_tasks")
                .update({"status": status})
                .eq("id", task_id)
                .eq("user_id", user_id)
                .execute()
            )
            return bool(res.data)
        except Exception as e:
            print(f"[StudyTaskRepo] Error updating task status: {e}")
            return False


class QuizAttemptRepository:
    """Repository for student quiz attempts and scores."""

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        return self._client or get_supabase_client()

    def get_user_attempts(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch user's recent quiz attempts."""
        if not self.client:
            return []
        try:
            res = (
                self.client.table("quiz_attempts")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"[QuizAttemptRepo] Error fetching quiz attempts: {e}")
            return []

    def save_quiz_attempt(
        self,
        user_id: str,
        subject: str,
        topic: str,
        difficulty: str,
        questions_and_answers: List[Dict[str, Any]],
        score: float,
        total_questions: int,
    ) -> Optional[str]:
        """Save a completed quiz attempt with score."""
        if not self.client:
            return None
        try:
            res = (
                self.client.table("quiz_attempts")
                .insert({
                    "user_id": user_id,
                    "subject": subject,
                    "topic": topic,
                    "difficulty": difficulty,
                    "questions_and_answers": questions_and_answers,
                    "score": round(score, 2),
                    "total_questions": total_questions,
                })
                .execute()
            )
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            print(f"[QuizAttemptRepo] Error saving quiz attempt: {e}")
            return None
