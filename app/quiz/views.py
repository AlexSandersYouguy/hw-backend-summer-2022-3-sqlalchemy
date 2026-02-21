from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import request_schema, response_schema
from sqlalchemy.exc import IntegrityError

from app.quiz.schemes import (
    ThemeSchema,
    ThemeListSchema,
    QuestionSchema,
    ListQuestionSchema,
    ThemeIdSchema,
    AnswerSchema
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response, auth_required
from app.quiz.models import AnswerModel


class ThemeAddView(View, AuthRequiredMixin):
    @auth_required
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema, 200)
    async def post(self):
        """Добавление новой темы"""
        data = self.request["data"]
        title = data["title"]
        
        # Проверяем, существует ли тема
        existing_theme = await self.store.quizzes.get_theme_by_title(title)
        if existing_theme:
            raise HTTPConflict(reason=f"Theme '{title}' already exists")
        
        # Создаем тему
        theme = await self.store.quizzes.create_theme(title=title)
        
        return json_response(data={
            "id": theme.id,
            "title": theme.title
        })


class ThemeListView(View, AuthRequiredMixin):
    @auth_required
    @response_schema(ThemeListSchema, 200)
    async def get(self):
        """Получение списка всех тем"""
        themes = await self.store.quizzes.list_themes()
        
        return json_response(data={
            "themes": [
                {"id": theme.id, "title": theme.title}
                for theme in themes
            ]
        })

class QuestionAddView(View, AuthRequiredMixin):
    @auth_required
    @request_schema(QuestionSchema)
    async def post(self):
        """Добавление нового вопроса"""
        data = self.request["data"]
        title = data["title"]
        theme_id = data["theme_id"]
        answers_data = data["answers"]
        
        # Проверяем существование темы
        theme = await self.store.quizzes.get_theme_by_id(theme_id)
        if not theme:
            raise HTTPNotFound(reason=f"Theme with id={theme_id} not found")
        
        # Валидация ответов
        if len(answers_data) < 2:
            raise HTTPBadRequest(reason="Question must have at least 2 answers")
        
        correct_answers = sum(1 for a in answers_data if a.get("is_correct", False))
        
        if correct_answers == 0:
            raise HTTPBadRequest(reason="Question must have one correct answer")
        if correct_answers > 1:
            raise HTTPBadRequest(reason="Question must have only one correct answer")
        
        # Создаем объекты AnswerModel из данных запроса
        answer_models = [
            AnswerModel(
                title=a["title"],
                is_correct=a.get("is_correct", False)
            )
            for a in answers_data
        ]
        
        try:
            # Создаем вопрос
            question = await self.store.quizzes.create_question(
                title=title,
                theme_id=theme_id,
                answers=answer_models
            )
        except IntegrityError as e:
            # Обрабатываем ошибки БД
            if "foreign key" in str(e).lower() or "23503" in str(e):
                raise HTTPNotFound(reason=f"Theme with id={theme_id} not found")
            elif "unique" in str(e).lower() or "23505" in str(e):
                raise HTTPConflict(reason=f"Question '{title}' already exists")
            elif "not null" in str(e).lower() or "23502" in str(e):
                raise HTTPBadRequest(reason="Invalid data provided")
            else:
                raise HTTPBadRequest(reason="Database error")
        
        # Формируем ответ
        return json_response(data={
            "id": question.id,
            "title": question.title,
            "theme_id": question.theme_id,
            "answers": [
                {
                    "title": answer.title,
                    "is_correct": answer.is_correct,
                }
                for answer in question.answers
            ]
        })

class QuestionListView(View, AuthRequiredMixin):
    @auth_required
    @response_schema(ListQuestionSchema, 200)
    async def get(self):
        """Получение списка вопросов"""
        # Получаем theme_id из query параметров
        theme_id = self.request.query.get("theme_id")
        
        if theme_id:
            try:
                theme_id = int(theme_id)
                # Проверяем существование темы
                theme = await self.store.quizzes.get_theme_by_id(theme_id)
                if not theme:
                    raise HTTPNotFound(reason=f"Theme with id={theme_id} not found")
            except ValueError:
                raise HTTPBadRequest(reason="Invalid theme_id format")
        
        questions = await self.store.quizzes.list_questions(theme_id)
        
        return json_response(data={
            "questions": [
                {
                    "id": q.id,
                    "title": q.title,
                    "theme_id": q.theme_id,
                    "answers": [
                        {
                            "title": a.title,
                            "is_correct": a.is_correct
                        }
                        for a in q.answers
                    ]
                }
                for q in questions
            ]
        })