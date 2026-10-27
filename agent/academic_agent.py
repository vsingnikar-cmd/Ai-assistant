"""Academic Agent Core Coordinator.

Demonstrates all seven core components of an AI Agent:
1. User Interface (Streamlit components)
2. Prompt Processing (agent.prompt_processor)
3. Large Language Model (agent.gemini_client)
4. Memory Module (services.memory_service)
5. Tool Integration (11 required Python agent tools)
6. Response Generation (agent.response_formatter)
7. Deployment Platform (Streamlit Community Cloud / Server)
"""

from typing import Any, Dict, List, Optional, Tuple
from agent.gemini_client import GeminiClient
from agent.prompt_processor import PromptProcessor, classify_intent
from agent.prompts import (
    PDF_QA_PROMPT_TEMPLATE,
    EXAM_NOTES_PROMPT_TEMPLATE,
    QUIZ_GENERATOR_PROMPT_TEMPLATE,
    STUDY_PLANNER_PROMPT_TEMPLATE,
)
from database.repositories import (
    ProfileRepository,
    ConversationRepository,
    MessageRepository,
    StudyPlanRepository,
    StudyTaskRepository,
    QuizAttemptRepository,
)


class AcademicAgent:
    """The central AI Student Assistant Agent orchestrating tools, memory, and LLM reasoning."""

    def __init__(self, user_id: Optional[str] = None, gemini_client: Optional[GeminiClient] = None):
        self.user_id = user_id
        self.llm = gemini_client or GeminiClient()
        self.prompt_processor = PromptProcessor()

        # Database repositories
        self.profile_repo = ProfileRepository()
        self.conv_repo = ConversationRepository()
        self.msg_repo = MessageRepository()
        self.plan_repo = StudyPlanRepository()
        self.task_repo = StudyTaskRepository()
        self.quiz_repo = QuizAttemptRepository()

        # Load student profile if user_id is provided
        if self.user_id:
            profile = self.get_student_profile(self.user_id)
            if profile:
                self.prompt_processor.set_student_profile(profile)

    # -------------------------------------------------------------------------
    # REQUIRED AGENT TOOLS (Section 15 of Specifications)
    # -------------------------------------------------------------------------

    def get_student_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Tool 1: Retrieve student academic profile."""
        if not user_id:
            return None
        return self.profile_repo.get_profile(user_id)

    def get_conversation_history(self, user_id: str, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Tool 2: Retrieve recent conversation messages for conversational memory."""
        if not user_id or not conversation_id:
            return []
        return self.msg_repo.get_conversation_messages(user_id, conversation_id, limit=limit)

    def save_conversation_message(
        self, user_id: str, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Tool 3: Persist message into conversation memory."""
        if not user_id or not conversation_id or not content:
            return False
        return self.msg_repo.save_message(user_id, conversation_id, role, content, metadata)

    def extract_pdf_text(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Tool 4: Extract text and metadata from uploaded study PDF using PyMuPDF."""
        from services.pdf_service import extract_text_from_pdf_bytes
        return extract_text_from_pdf_bytes(pdf_bytes, filename)

    def retrieve_document_context(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 3) -> str:
        """Tool 5: Retrieve most relevant document passages based on student query."""
        from services.pdf_service import retrieve_relevant_chunks
        return retrieve_relevant_chunks(query, chunks, top_k=top_k)

    def generate_exam_notes(
        self,
        subject: str,
        unit: str,
        topic: str,
        format_type: str = "5-Mark & 10-Mark Notes",
        detail_level: str = "High",
        syllabus_text: str = "",
    ) -> Tuple[bool, str]:
        """Tool 6: Generate high-yield exam preparation notes and practice questions."""
        syllabus_context = f"Syllabus Excerpt:\n{syllabus_text}" if syllabus_text else ""
        prompt = EXAM_NOTES_PROMPT_TEMPLATE.format(
            subject=subject,
            unit=unit or "General",
            topic=topic,
            format_type=format_type,
            detail_level=detail_level,
            syllabus_context=syllabus_context,
        )
        system_instruction = self.prompt_processor.build_system_context(style_key="detailed")
        return self.llm.generate_response(prompt=prompt, system_instruction=system_instruction)

    def generate_quiz(
        self, subject: str, topic: str, difficulty: str = "Medium", num_questions: int = 5, quiz_format: str = "mcq"
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Tool 7: Generate structured practice quiz adhering to JSON schema."""
        prompt = QUIZ_GENERATOR_PROMPT_TEMPLATE.format(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            quiz_format=quiz_format,
        )
        system_instruction = (
            "You are an academic test engineer. Output pure, valid JSON with no markdown wrapping."
        )
        return self.llm.generate_structured_json(prompt=prompt, system_instruction=system_instruction)

    def evaluate_quiz(
        self,
        questions: List[Dict[str, Any]],
        user_answers: Dict[int, str],
        user_id: Optional[str] = None,
        subject: str = "",
        topic: str = "",
        difficulty: str = "Medium",
    ) -> Dict[str, Any]:
        """Tool 8: Evaluate submitted quiz answers strictly in Python without asking LLM for arithmetic.

        Saves attempt record if user_id is provided.
        """
        from services.quiz_service import score_quiz_submission

        result = score_quiz_submission(questions, user_answers)

        # Persist attempt to database
        target_user = user_id or self.user_id
        if target_user:
            attempt_id = self.quiz_repo.save_quiz_attempt(
                user_id=target_user,
                subject=subject or "General",
                topic=topic or "General",
                difficulty=difficulty,
                questions_and_answers=result.get("breakdown", []),
                score=result.get("percentage", 0.0),
                total_questions=result.get("total_questions", len(questions)),
            )
            result["attempt_id"] = attempt_id

        return result

    def create_study_plan(
        self,
        subjects: str,
        topics: str,
        exam_date: str,
        daily_hours: float,
        start_date: str,
        end_date: str,
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Tool 9: Generate structured personalized study plan with task breakdown."""
        profile = self.prompt_processor.profile
        prompt = STUDY_PLANNER_PROMPT_TEMPLATE.format(
            course=profile.get("course", "College Course"),
            branch=profile.get("branch", "General"),
            semester=profile.get("semester", "Semester"),
            subjects=subjects,
            topics=topics,
            exam_date=exam_date,
            daily_hours=daily_hours,
            start_date=start_date,
            end_date=end_date,
        )
        system_instruction = (
            "You are an expert academic counselor. Output a realistic, structured study plan in pure JSON."
        )
        success, plan_json, err = self.llm.generate_structured_json(prompt=prompt, system_instruction=system_instruction)
        if success and plan_json and self.user_id:
            # Persist plan to database
            plan_id = self.plan_repo.create_plan(
                user_id=self.user_id,
                title=plan_json.get("plan_title", f"{subjects} Exam Plan"),
                subject=subjects,
                start_date=start_date,
                end_date=end_date,
                plan_data=plan_json,
            )
            if plan_id:
                plan_json["id"] = plan_id
                # Insert individual tasks
                for task in plan_json.get("tasks", []):
                    self.task_repo.create_task(
                        user_id=self.user_id,
                        plan_id=plan_id,
                        task_title=task.get("task_title", "Task"),
                        due_date=task.get("due_date", start_date),
                        description=task.get("description", ""),
                        duration=task.get("estimated_duration_minutes", 60),
                        priority=task.get("priority", "Medium"),
                    )

        return success, plan_json, err

    def update_study_task(self, user_id: str, task_id: str, status: str) -> bool:
        """Tool 10: Update completion status of an individual study task."""
        if not user_id or not task_id:
            return False
        return self.task_repo.update_task_status(user_id, task_id, status)

    def get_study_progress(self, user_id: str) -> Dict[str, Any]:
        """Tool 11: Compute true study progress metrics from stored database records."""
        if not user_id:
            return {
                "total_plans": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0.0,
                "total_quizzes": 0,
                "average_quiz_score": 0.0,
            }

        plans = self.plan_repo.get_user_plans(user_id)
        tasks = self.task_repo.get_plan_tasks(user_id)
        quizzes = self.quiz_repo.get_user_attempts(user_id)

        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        completion_rate = (completed_tasks / len(tasks) * 100) if tasks else 0.0

        avg_score = (sum(float(q.get("score", 0)) for q in quizzes) / len(quizzes)) if quizzes else 0.0

        return {
            "total_plans": len(plans),
            "total_tasks": len(tasks),
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 1),
            "total_quizzes": len(quizzes),
            "average_quiz_score": round(avg_score, 1),
            "recent_quizzes": quizzes[:5],
            "active_plans": plans[:3],
        }

    # -------------------------------------------------------------------------
    # CHAT AND ASSISTANT REASONING
    # -------------------------------------------------------------------------

    def answer_academic_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        document_context: Optional[str] = None,
        document_name: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Coordinate reasoning pipeline to produce a verified pedagogical response."""
        has_doc = bool(document_context)
        intent = classify_intent(query, has_active_document=has_doc)

        if has_doc and (intent == "document_question" or "[DOCUMENT CONTENT START]" in query):
            # Grounded QA
            prompt = PDF_QA_PROMPT_TEMPLATE.format(
                document_name=document_name or "Uploaded Study Document",
                document_context=document_context,
                user_query=query,
            )
            system_instruction = self.prompt_processor.build_system_context(style_key="detailed")
            return self.llm.generate_response(prompt=prompt, system_instruction=system_instruction)

        # Standard academic question
        prompt, system_instruction = self.prompt_processor.build_chat_prompt(
            user_message=query,
            conversation_history=conversation_history,
            document_context=document_context,
        )

        return self.llm.generate_response(prompt=prompt, system_instruction=system_instruction)
