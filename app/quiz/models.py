from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel


class ThemeModel(BaseModel):
    __tablename__ = "themes"
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)


class AnswerModel(BaseModel):
    __tablename__ = "answers"
    id = Column(BigInteger, primary_key=True, index=True)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, unique=True, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)


class QuestionModel(BaseModel):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True, index=True)
    theme_id = Column(BigInteger, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, unique=True, nullable=False)
    answers = relationship(AnswerModel, uselist=True)