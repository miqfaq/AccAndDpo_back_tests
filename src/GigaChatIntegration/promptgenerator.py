import json
from src.testEngine.models import AttemptAnswer
from gigachat import GigaChat
from src.security.security import settings
from gigachat.models import Chat, Messages, MessagesRole

def prompt_generator(acc_context, att_context: list[AttemptAnswer]):
    # 1. Ваши уже полученные ответы (пример структуры)
    SYSTEM_PROMPT = """Ты — эксперт по педагогическому тестированию и анализу результатов. Твоя задача — проанализировать ответы пользователя на тест и выдать структурированное заключение.

    ### ВХОДНЫЕ ДАННЫЕ
    Пользователь передаёт JSON-объект следующей структуры:
    {
    "answers": [
        {
        "position": 027c2a35-245f-4a40-86e4-bc708147bbee,
        "answer_text": "Текст вопроса",
        "question_text": "Ответ пользователя",
        "is_correct": true/false,
        "is_selected": true/false,
        }
    ]
    "accreditation_context":{
        "skill":"Навык который проверяется в аккредитации",
        "self_rating": "Как пользователь сам себя оценил перед аккредитацией(Необязательное поле не делай акцент на нем)",
        "rating": "Объективная оценка навыков пользователя от 1 до 100",
        "direction": "В каком направлении развивается пользователь"
        }
    }

    ### ТВОЯ ЗАДАЧА
    1. Определить стал ли пользователь сильнее относительно rating и указать на это
    2. Выяви темы, в которых пользователь допустил ошибки, и сгруппируй ошибки по темам.
    3. Для каждой проблемной темы кратко объясни, в чём вероятная причина ошибки (например: незнание определения, путаница в терминах, невнимательность).
    4. Дай 1–2 конкретные рекомендации по повторению материала для каждой слабой темы.
    5. Если ошибок нет — подтверди успешное освоение и предложи тему для углублённого изучения (на основе самого сложного вопроса).

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
    - Если пользователь ответил правильно на все вопросы, массив weak_topics оставь пустым, а в general_feedback напиши похвалу и одно направление для роста.
    - Отвечай на русском языке.
    """
    print(att_context[0])
    user_results = {
        "answers": [f"position: {answer.position} answer_text: {answer.answer_text} is_correct: {answer.is_true} is_selected: {answer.is_selected}" for answer in att_context],
        "accreditation_context": [f"skill: {accred.skill} self_rating: {accred.self_rating} rating: {accred.rating} direction: {accred.direction}"for accred in acc_context]
    }

    # 2. Инициализация клиента (ключ авторизации берите из переменной окружения)
    client = GigaChat(
        credentials=settings.GIGACHAT_API_KEY,  # или os.environ["GIGACHAT_CREDENTIALS"]
        scope="GIGACHAT_API_PERS",
        model="GigaChat-2",  # для сложного анализа лучше Max/Pro [citation:6]
        verify_ssl_certs=False,   # только для разработки
    )

    # 3. Формирование запроса
    user_content = f"Проанализируй результаты теста:\n{json.dumps(user_results, ensure_ascii=False)}"

    chat = Chat(
        messages=[
            Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
            Messages(role=MessagesRole.USER, content=user_content),
        ]
    )

    # 4. Отправка и разбор ответа
    response = client.chat(chat)
    raw_answer = response.choices[0].message.content

    # 5. Парсинг JSON (GigaChat может вернуть в строке)
    try:
        analysis = json.loads(raw_answer)
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        return analysis
    except json.JSONDecodeError:
        print("Модель вернула не-JSON, вывод сырого ответа:")
        print(raw_answer)
        return raw_answer