import json
import logging
from gigachat import GigaChatAsyncClient  # Явно используем асинхронный клиент
from gigachat.models import Chat, Messages, MessagesRole
from src.testEngine.models import AttemptAnswer
from src.security.security import settings

logger = logging.getLogger(__name__)


async def prompt_generator(acc_context, att_context: list[AttemptAnswer]) -> dict:
    SYSTEM_PROMPT = """Ты — эксперт по педагогическому тестированию и анализу результатов. Твоя задача — проанализировать ответы пользователя на тест и выдать структурированное заключение.

    ### ВХОДНЫЕ ДАННЫЕ
    Пользователь передаёт JSON-объект следующей структуры:
    {
    "answers": [
        {
        "position": "027c2a35-245f-4a40-86e4-bc708147bbee",
        "answer_text": "Ответ пользователя",
        "question_text": "Текст вопроса",
        "is_correct": true/false,
        "is_selected": true/false
        }
    ],
    "accreditation_context": {
        "skill": "Навык который проверяется в аккредитации",
        "self_rating": "Как пользователь сам себя оценил перед аккредитацией",
        "rating": "Объективная оценка навыков пользователя от 1 до 100",
        "direction": "В каком направлении развивается пользователь"
        }
    }

    ### ТВОЯ ЗАДАЧА
    1. Определить стал ли пользователь сильнее относительно rating и указать на это
    2. Выяви темы, в которых пользователь допустил ошибки, и сгруппируй ошибки по темам.
    3. Для каждой проблемной темы кратко объясни, в чём вероятная причина ошибки.
    4. Дай 1–2 конкретные рекомендации по повторению материала для каждой слабой темы.
    5. Если ошибок нет — подтверди успешное освоение и предложи тему для углублённого изучения.

    ### ФОРМАТ ОТВЕТА (СТРОГО)
    Верни только валидный JSON без markdown-обёрток и комментариев:
    {
    "total_score_percent": 85,
    "weak_topics": [
        {
        "topic": "Название темы",
        "error_count": 2,
        "reasoning": "Краткое объяснение вероятной причины ошибок",
        "recommendation": "Что повторить или сделать"
        }
    ],
    "general_feedback": "Общее заключение (1–3 предложения)"
    }

    ### ПРАВИЛА
    - Не выдумывай вопросы, которых нет во входных данных.
    - Если поле topic отсутствует, используй текст вопроса как тему.
    - Если пользователь ответил правильно на все вопросы, массив weak_topics оставь пустым.
    - Отвечай на русском языке.
    """

    # Собираем данные в строгом соответствии с JSON-структурой в SYSTEM_PROMPT
    user_results = {
        "answers": [f"position: {answer.position} answer_text: {answer.answer_text} is_correct: {answer.is_true} is_selected: {answer.is_selected}" for answer in att_context],
        "accreditation_context": [f"skill: {accred.skill} self_rating: {accred.self_rating} rating: {accred.rating} direction: {accred.direction}"for accred in acc_context]
    }

    user_content = f"Проанализируй результаты теста:\n{json.dumps(user_results, ensure_ascii=False)}"

    # Используем асинхронный клиент, асинхронный контекстный менеджер, асинхронные методы
    async with GigaChatAsyncClient(
        credentials=settings.GIGACHAT_API_KEY,
        scope="GIGACHAT_API_PERS",
        model="GigaChat-2",
        verify_ssl_certs=False,
    ) as client:
        chat = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                Messages(role=MessagesRole.USER, content=user_content),
            ]
        )
        response = await client.achat(chat)  # Метод асинхронного клиента — achat
        raw_answer = response.choices[0].message.content

    # Парсинг с обработкой возможных markdown-обёрток
    raw_answer = raw_answer.strip()
    if raw_answer.startswith("```"):
        lines = raw_answer.splitlines()
        raw_answer = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        analysis = json.loads(raw_answer)
        logger.debug("GigaChat analysis: %s", json.dumps(analysis, ensure_ascii=False, indent=2))
        return analysis
    except json.JSONDecodeError:
        logger.exception("GigaChat вернул не-JSON: %s", raw_answer)
        raise ValueError("GigaChat returned non-JSON response") from None