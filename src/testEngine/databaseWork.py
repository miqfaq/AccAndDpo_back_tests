from src.database.databaseUse import session_factory
from src.profile.models import Accreditation
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from src.testEngine.schemas import Direction, QuestionShcema, AttemptSchema, KeyByCompetencies
from src.testEngine.models import Question, Answer, Attempt, AttemptQuestion, AttemptAnswer
from src.testEngine.testconstructor import FirstTest, RepeatTest
from datetime import datetime, timezone
import uuid


def get_direction(acc_id, user_id) -> str:
    with session_factory() as session:
        stmt = (
            select(Accreditation.direction)
            .where(Accreditation.user_id == user_id and Accreditation.uid == acc_id)
        )
        direction = session.scalars(stmt).one_or_none()
        if direction is None:
            raise ValueError("Accreditation not found")
        return direction

def get_questions_by_direction(direction: Direction) -> list[Question]:
    direction = Direction(direction)
    with session_factory() as session:
        stmt = (
            select(Question)
            .where(Question.direction == direction)
        )
        questions = list(session.scalars(stmt).all())
        if questions is None:
            raise ValueError("Questions not found")
        return questions

def getTest(userId: uuid.UUID, acc_id: uuid.UUID):
    with session_factory() as session:
        type_test = session.scalars(select(Attempt).where(Attempt.user_id == userId, Attempt.accreditation_id == acc_id) )

        target = session.scalars(select(Accreditation.target).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
        skill = session.scalars(select(Accreditation.skill).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
        direction = session.scalars(select(Accreditation.direction).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
        if type_test is not None:
            level = session.scalars(select(Accreditation.rating).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
            test = RepeatTest(session=session, user_id=userId, direction=direction, skill=skill, target=target, level=level)
        else:
            self_rating = session.scalars(select(Accreditation.self_rating).where(Accreditation.user_id == userId, Accreditation.uid == acc_id)).one()
            test = FirstTest(session=session, user_id=userId, direction=direction, skill=skill, target=target, self_rating=self_rating)

        return test.build()

def addQuestion(question: QuestionShcema):
    with session_factory() as session:
        session.add(Question(
            question_text = question.question_text,
            difficulty = question.difficulty,
            direction = question.direction,
            skill = question.skill,
            ability = question.ability,
            answers = [
                Answer(answer_text = answer.answer_text.strip(), is_true = answer.is_true)
                for answer in question.answer_list
            ],
        ))
        session.commit()

def getAccList_uid(uid:uuid.UUID) -> list[Accreditation]:
    with session_factory() as session:
        accList = session.scalars(select(Accreditation).where(Accreditation.user_id == uid)).all()
        return accList # pyright: ignore[reportReturnType]


class AttemptError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

def save_attempt(
    attempt: AttemptSchema,
    user_id: uuid.UUID,
    accreditation_id: uuid.UUID | None = None,
) -> uuid.UUID:
    try:
        attempt_uuid = uuid.UUID(attempt.attempt_id)
    except ValueError:
        raise AttemptError(422, "attempt_id должен быть UUID")

    questions = sorted(attempt.questions, key=lambda q: q.position)
    if not questions:
        raise AttemptError(422, "В тесте нет вопросов")
    if len({q.position for q in questions}) != len(questions):
        raise AttemptError(422, "Позиции вопросов повторяются")
    if len({q.question_id for q in questions}) != len(questions):
        raise AttemptError(422, "Вопросы повторяются")
    for q in questions:
        if len({a.answer_id for a in q.answers}) != len(q.answers):
            raise AttemptError(422, f"У вопроса {q.question_id} повторяются варианты ответа")

    question_ids = [q.question_id for q in questions]
    answer_ids = [a.answer_id for q in questions for a in q.answers]

    with session_factory() as session:
        if session.get(Attempt, attempt_uuid) is not None:
            raise AttemptError(409, "Эта попытка уже сохранена")

        # Сложность берём из банка, а не от клиента
        difficulty: dict[uuid.UUID, int] = {
            qid: diff
            for qid, diff in session.execute(
            select(Question.question_id, Question.difficulty)
            .where(Question.question_id.in_(question_ids))
            )
        }
        if len(difficulty) != len(question_ids):
            raise AttemptError(422, "Часть вопросов не найдена в банке")

        # Правильность вариантов тоже берём из банка
        truth = {
            row.answer_id: row
            for row in session.execute(
                select(Answer.answer_id, Answer.question_id, Answer.is_true)
                .where(Answer.answer_id.in_(answer_ids))
            )
        }
        for q in questions:
            for a in q.answers:
                row = truth.get(a.answer_id)
                if row is None or row.question_id != q.question_id:
                    raise AttemptError(
                        422, f"Вариант {a.answer_id} не относится к вопросу {q.question_id}"
                    )

        session.add(
            Attempt(
                attempt_id=attempt_uuid,
                user_id=user_id,
                accreditation_id=accreditation_id,
                direction=attempt.direction,
                skill=attempt.skill,
                target=attempt.target,
                self_rating=attempt.self_rating,
                questions=[
                    AttemptQuestion(
                        question_id=q.question_id,
                        position=q.position,
                        question_text=q.question_text.strip(),
                        difficulty=difficulty[q.question_id],
                        direction=q.direction,
                        skill=q.skill,
                        answers=[
                            AttemptAnswer(
                                answer_id=a.answer_id,
                                attempt_id=attempt_uuid,
                                position=i,
                                answer_text=a.answer_text.strip(),
                                is_true=truth[a.answer_id].is_true,
                                is_selected = a.is_selected,
                            )
                            for i, a in enumerate(q.answers, start=1)
                        ],
                    )
                    for q in questions
                ],
            )
        )
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise AttemptError(
                409, f"Не удалось сохранить попытку: {exc.orig}"
            )

    return attempt_uuid

def score_count(user_id, acc_id):
    with session_factory() as session:
        attempt_id = session.scalars(
            select(Attempt.attempt_id)
            .where(Attempt.user_id == user_id,
                   Attempt.accreditation_id == acc_id,
                   Attempt.score == None)
            .limit(1)
        ).first()
        if attempt_id is None:
            raise ValueError("attempt not found")

        questions = session.scalars(
            select(AttemptQuestion)
            .where(AttemptQuestion.attempt_id == attempt_id)
        ).all()

        # id вопросов, на которые дан правильный ответ
        correct_ids = set(session.scalars(
            select(AttemptAnswer.attempt_question_id)
            .where(AttemptAnswer.attempt_id == attempt_id,
                   AttemptAnswer.is_selected == True,
                   AttemptAnswer.is_true == True)
        ).all())

        weights_sum = sum(q.difficulty for q in questions if q.id in correct_ids)
        all_weights_sum = sum(q.difficulty for q in questions)

        score = round(100 * weights_sum / all_weights_sum, 2) if all_weights_sum else 0
        session.execute(
            update(Attempt)
            .where(Attempt.attempt_id == attempt_id)
            .values(score=score)
        )
        session.commit()
    return score

def rating_count(user_id, skill):
    with session_factory() as session:
        print(skill)
        acc_id = session.scalars(
            select(Accreditation.uid)
            .where(Accreditation.user_id == user_id,
                   Accreditation.skill == skill
                   )
            .limit(1)
        ).first()
        if acc_id is None:
            raise ValueError("Accreditation not found")

        attempts = session.scalars(
            select(Attempt)
            .where(Attempt.user_id == user_id,
                   Attempt.accreditation_id == acc_id)
        ).all()
        if not attempts:
            raise ValueError("Attempts not found")

        sum_rating = 0
        for attempt in attempts:
            if attempt.score is not None:
                if (datetime.now(timezone.utc) - attempt.started_at).total_seconds() > 2592000: #2 592 000 - месяц
                    sum_rating += attempt.score/2
                else:
                    sum_rating += attempt.score
        rating = round(sum_rating/len(attempts))
        session.execute(
            update(Accreditation)
            .where(Accreditation.user_id == user_id,
                   Accreditation.skill == skill)
            .values(rating = rating)
        )
        session.commit()
    return rating


        
