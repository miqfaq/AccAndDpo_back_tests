from src.testEngine.schemas import QuestionShcema, AnswerSchema



class Test:
    """Parent Class for all tests"""
    NUMBER_OF_QUESTION_FOR_SKILL = 5
    def __init__(self, questions: list[QuestionShcema], is_first: bool) -> None: #Начал класс конструктора тестов. Нужно продумать как он будет подбирать вопросы исходя из уровня пользователя. Также понять как он должен миксовать вопросы разной сложности.
        pass
