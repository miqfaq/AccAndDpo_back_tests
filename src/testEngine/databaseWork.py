from src.database.databaseUse import session_factory
from src.profile.models import Accreditation
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from src.testEngine.schemas import Direction, QuestionShcema, AttemptSchema, KeyByCompetencies
from src.testEngine.models import Question, Answer, Attempt, AttemptQuestion, AttemptAnswer
from src.testEngine.testconstructor import FirstTest, RepeatTest
from datetime import datetime, timezone
import uuid


async def get_direction(acc_id, user_id) -> str:
    async with session_factory() as session:
        stmt = (
            select(Accreditation.direction)
            .where(Accreditation.user_id == user_id and Accreditation.uid == acc_id)
        )
        res = await session.execute(stmt)
        direction = res.scalars().one_or_none()
        if direction is None:
            raise ValueError("Accreditation not found")
        return direction

async def get_questions_by_direction(direction: Direction) -> list[Question]:
    direction = Direction(direction)
    async with session_factory() as session:
        stmt = (
            select(Question)
            .where(Question.direction == direction)
        )
        res = await session.execute(stmt)
        questions = list(res.scalars().all())
        if questions is None:
            raise ValueError("Questions not found")
        return questions

async def getTest(userId: uuid.UUID, acc_id: uuid.UUID):
    async with session_factory() as session:
        type_test = session.scalars(select(Attempt).where(Attempt.user_id == userId, Attempt.accreditation_id == acc_id))
        resAcc = await session.execute(select(Accreditation).where(Accreditation.user_id == userId, Accreditation.uid == acc_id))
        acc = resAcc.scalar()
        if acc is not None:
            if type_test is not None:
                test = RepeatTest(session=session, user_id=userId, direction=acc.direction, skill=acc.skill, target=acc.target, level=acc.rating)
            else:
                test = FirstTest(session=session, user_id=userId, direction=acc.direction, skill=acc.skill, target=acc.target, self_rating=acc.self_rating)

        return test.build()

async def addQuestion(question: QuestionShcema):
    async with session_factory() as session:
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
        await session.commit()

async def getAccList_uid(uid:uuid.UUID) -> list[Accreditation]:
    async with session_factory() as session:
        resAccList = await session.execute(select(Accreditation).where(Accreditation.user_id == uid))
        accList = resAccList.scalars().all()
        return accList # pyright: ignore[reportReturnType]


class AttemptError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

async def save_attempt(
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

    async with session_factory() as session:
        if session.get(Attempt, attempt_uuid) is not None:
            raise AttemptError(409, "Эта попытка уже сохранена")

        # Сложность берём из банка, а не от клиента
        difficulty: dict[uuid.UUID, int] = {
            qid: diff
            for qid, diff in await session.execute(
            select(Question.question_id, Question.difficulty)
            .where(Question.question_id.in_(question_ids))
            )
        }
        if len(difficulty) != len(question_ids):
            raise AttemptError(422, "Часть вопросов не найдена в банке")

        # Правильность вариантов тоже берём из банка
        truth = {
            row.answer_id: row
            for row in await session.execute(
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
            await session.commit()
        except IntegrityError as exc:
            raise AttemptError(
                409, f"Не удалось сохранить попытку: {exc.orig}"
            )

    return attempt_uuid

async def score_count(user_id, acc_id):
    async with session_factory() as session:
        att_id_res = await session.execute(select(Attempt.attempt_id)
                    .where(Attempt.user_id == user_id,
                           Attempt.accreditation_id == acc_id,
                           Attempt.score == None)
                    .limit(1))
        attempt_id = att_id_res.scalars().first()
        if attempt_id is None:
            raise ValueError("attempt not found")

        que_res = await session.execute(
            select(AttemptQuestion)
            .where(AttemptQuestion.attempt_id == attempt_id))
        questions = que_res.scalars().all()

        corr_id_res = await session.execute(
            select(AttemptAnswer.attempt_question_id)
            .where(AttemptAnswer.attempt_id == attempt_id,
                   AttemptAnswer.is_selected == True,
                   AttemptAnswer.is_true == True))
        # id вопросов, на которые дан правильный ответ
        correct_ids = set(corr_id_res.scalars().all())

        weights_sum = sum(q.difficulty for q in questions if q.id in correct_ids)
        all_weights_sum = sum(q.difficulty for q in questions)

        score = round(100 * weights_sum / all_weights_sum, 2) if all_weights_sum else 0
        await session.execute(
            update(Attempt)
            .where(Attempt.attempt_id == attempt_id)
            .values(score=score)
        )
        await session.commit()
    return score

async def rating_count(user_id, skill):
    async with session_factory() as session:
        print(skill)
        acc_id_res = await session.execute(
            select(Accreditation.uid)
            .where(Accreditation.user_id == user_id,
                   Accreditation.skill == skill
                   )
            .limit(1))
        acc_id = acc_id_res.scalars().first()
        if acc_id is None:
            raise ValueError("Accreditation not found")

        att_res = await session.execute(
            select(Attempt)
            .where(Attempt.user_id == user_id,
                    Attempt.accreditation_id == acc_id)
        )
        
        attempts = att_res.scalars().all()
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
        await session.execute(
            update(Accreditation)
            .where(Accreditation.user_id == user_id,
                   Accreditation.skill == skill)
            .values(rating = rating)
        )
        await session.commit()
    return rating


        
