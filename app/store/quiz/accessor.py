from collections.abc import Iterable, Sequence
from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import AnswerModel, QuestionModel, ThemeModel


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        """Создание новой темы"""
        query = insert(ThemeModel).values(title=title).returning(ThemeModel)
        
        async with self.app.database.session() as session:
            try:
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
                # Пробрасываем IntegrityError дальше для тестов
                raise

    async def get_theme_by_title(self, title: str) -> Optional[ThemeModel]:
        """Получение темы по названию"""
        query = select(ThemeModel).where(ThemeModel.title == title)
        
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_theme_by_id(self, id_: int) -> Optional[ThemeModel]:
        """Получение темы по ID"""
        query = select(ThemeModel).where(ThemeModel.id == id_)
        
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def list_themes(self) -> Sequence[ThemeModel]:
        """Получение списка всех тем"""
        query = select(ThemeModel).order_by(ThemeModel.id)
        
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def create_question(
        self, title: str, theme_id: int, answers: Iterable[AnswerModel]
    ) -> QuestionModel:
        """Создание нового вопроса с ответами"""
        async with self.app.database.session() as session:
            try:
                # Создаем вопрос
                question = QuestionModel(
                    title=title,
                    theme_id=theme_id
                )
                session.add(question)
                await session.flush()  # чтобы получить id вопроса
                
                # Создаем ответы для вопроса
                for answer in answers:
                    answer.question_id = question.id
                    session.add(answer)
                
                await session.commit()
                
                # Получаем вопрос с ответами
                result = await session.execute(
                    select(QuestionModel)
                    .where(QuestionModel.id == question.id)
                    .options(joinedload(QuestionModel.answers))
                )
                return result.unique().scalar_one()
                
            except IntegrityError:
                await session.rollback()
                # Пробрасываем IntegrityError дальше для тестов
                raise

    async def get_question_by_title(self, title: str) -> Optional[QuestionModel]:
        """Получение вопроса по названию"""
        query = select(QuestionModel).where(QuestionModel.title == title)
        
        async with self.app.database.session() as session:
            result = await session.execute(query)
            question = result.scalar_one_or_none()
            
            if question:
                # Загружаем ответы
                result = await session.execute(
                    select(QuestionModel)
                    .where(QuestionModel.id == question.id)
                    .options(joinedload(QuestionModel.answers))
                )
                return result.unique().scalar_one()
            
            return None

    async def list_questions(
        self, theme_id: Optional[int] = None
    ) -> Sequence[QuestionModel]:
        """Получение списка вопросов"""
        query = select(QuestionModel).options(joinedload(QuestionModel.answers))
        
        if theme_id is not None:
            query = query.where(QuestionModel.theme_id == theme_id)
        
        query = query.order_by(QuestionModel.id)
        
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.unique().scalars().all()