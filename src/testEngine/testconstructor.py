from src.testEngine.schemas import Direction
from src.testEngine.models import Question, Attempt, AttemptQuestion

import math
import uuid
import random
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func


class WrongClassError(Exception):
    def __init__(self, *args: object, is_first, meassage="Выбран не верный конструктор теста") -> None:
        self.is_first = is_first
        self.message = self.message
        super().__init__(*args, self.message)

    def __str__(self) -> str:
        return f"{self.is_first} -> {self.message}"

class QuestionListEmptyError(Exception):
    def __str__(self) -> str:
        return "Question list empty"


class BaseTest(ABC):
    """Общая логика подбора вопросов. Наследники задают только difficulty_weights()."""

    LEVELS = 3
    SIGMA = 0.7
    NUMBER_OF_QUESTIONS = 20
    TARGET_WEIGHT = 0.2   # вклад целевого уровня в центр теста
    SELF_WEIGHT = 0.8     # вклад второго параметра (самооценка или прошлый результат)
    LEVEL_WEIGHT = 0.7
    TARGET_WEIGHT_2 = 0.3

    def __init__(
        self,
        session: Session,
        user_id: uuid.UUID | None,
        direction: str,
        skill: str,
        target: int,
    ) -> None:
        self.session = session
        self.user_id = user_id
        self.direction = Direction(direction).value  # ValueError, если направления нет в Enum
        self.skill = skill
        self.target = target

    # ---------- то, что различается у типов тестов ----------

    @abstractmethod
    def difficulty_weights(self) -> dict[int, float]:
        """Доля вопросов для каждой сложности (сумма долей равна 1)."""

    # ---------- общая логика ----------

    def _weights_from_mix(self, mix: float) -> dict[int, float]:
        """mix (0..100) -> центр на шкале сложности -> колокол весов."""
        mix = min(max(mix, 0), 100)
        center = 1 + (mix / 100) * (self.LEVELS - 1)
        raw = {
            d: math.exp(-((d - center) ** 2) / (2 * self.SIGMA**2))
            for d in range(1, self.LEVELS + 1)
        }
        total = sum(raw.values())
        return {d: w / total for d, w in raw.items()}

    @staticmethod
    def to_quotas(weights: dict[int, float], total: int) -> dict[int, int]:
        """Доли -> целые количества вопросов, сумма равна ровно total."""
        raw = {d: w * total for d, w in weights.items()}
        quotas = {d: int(v) for d, v in raw.items()}
        left = total - sum(quotas.values())
        by_remainder = sorted(raw, key=lambda d: raw[d] - quotas[d], reverse=True)
        for d in by_remainder[:left]:
            quotas[d] += 1
        return quotas

    def get_seen_question_ids(self) -> set[uuid.UUID]:
        if self.user_id is None:
            return set()
        stmt = (
            select(AttemptQuestion.question_id)
            .join(Attempt, Attempt.attempt_id == AttemptQuestion.attempt_id)
            .where(
                Attempt.user_id == self.user_id,
                AttemptQuestion.question_id.is_not(None),
            )
            .distinct()
        )
        return {qid for qid in self.session.scalars(stmt) if qid is not None}

    def _fetch(
        self, difficulty: int, limit: int, exclude_ids: set[uuid.UUID]
    ) -> list[Question]:
        """До `limit` случайных вопросов одной сложности, кроме exclude_ids."""
        if limit <= 0:
            return []
        stmt = (
            select(Question)
            .where(
                Question.direction == self.direction,
                Question.skill == self.skill,
                Question.difficulty == difficulty,
            )
            .options(selectinload(Question.answers))
        )
        if exclude_ids:
            stmt = stmt.where(Question.question_id.not_in(list(exclude_ids)))
        stmt = stmt.order_by(func.random()).limit(limit)
        return list(self.session.scalars(stmt).all())

    def pick_questions(
        self, quotas: dict[int, int], seen_ids: set[uuid.UUID]
    ) -> list[Question]:
        total = sum(quotas.values())
        chosen: list[Question] = []
        chosen_ids: set[uuid.UUID] = set()

        def take(difficulty: int, limit: int, exclude: set[uuid.UUID]) -> None:
            for q in self._fetch(difficulty, limit, exclude | chosen_ids):
                chosen.append(q)
                chosen_ids.add(q.question_id)

        # Этап 1: по квотам, только новые вопросы
        for difficulty, n in quotas.items():
            take(difficulty, n, seen_ids)

        # Порядок добора: сначала сложности, ближайшие к центру теста
        center = sum(d * n for d, n in quotas.items()) / total if total else 0
        by_distance = sorted(quotas, key=lambda d: abs(d - center))

        # Этап 2: добор недостающего, всё ещё только новые
        for difficulty in by_distance:
            take(difficulty, total - len(chosen), seen_ids)

        # Этап 3: если не хватило, разрешаем повторы
        for difficulty in by_distance:
            take(difficulty, total - len(chosen), set())

        random.shuffle(chosen)
        return chosen

    def build(self) -> list[Question]:
        quotas = self.to_quotas(self.difficulty_weights(), self.NUMBER_OF_QUESTIONS)
        return self.pick_questions(quotas, self.get_seen_question_ids())


class FirstTest(BaseTest):
    """Первый тест: центр сложности зависит от цели и самооценки."""

    def __init__(
        self,
        session: Session,
        user_id: uuid.UUID | None,
        direction: str,
        skill: str,
        target: int,
        self_rating: int,
    ) -> None:
        super().__init__(session, user_id, direction, skill, target)
        self.self_rating = self_rating

    def difficulty_weights(self) -> dict[int, float]:
        mix = self.TARGET_WEIGHT * self.target + self.SELF_WEIGHT * self.self_rating
        return self._weights_from_mix(mix)

class RepeatTest(BaseTest):
    def __init__(self, session, user_id, direction, skill, target, level: float):
        super().__init__(session, user_id, direction, skill, target)
        self.level = level

    def difficulty_weights(self) -> dict[int, float]:
        mix = self.TARGET_WEIGHT_2 * self.target + self.LEVEL_WEIGHT * self.level
        return self._weights_from_mix(mix)


        
