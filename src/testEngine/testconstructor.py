from src.testEngine.schemas import QuestionShcema, AnswerSchema, Direction
from src.testEngine.databaseWork import get_questions_by_direction


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


class Test:
    """Parent Class for all tests"""
    NUMBER_OF_QUESTIONS_FOR_ABILITY = 2
    def __init__(self, is_first: bool, direction: str) -> None: #Начал класс конструктора тестов. Нужно продумать как он будет подбирать вопросы исходя из уровня пользователя. Также понять как он должен миксовать вопросы разной сложности.
        self.direction = direction
        self.questions = get_questions_by_direction(Direction(self.direction))
        self.is_first = is_first

class FirstTest(Test):
    """Class constructor of first tests"""
    def __init__(self, is_first: bool, direction: str) -> None:
        super().__init__(is_first, direction)
        self.questions = get_questions_by_direction(Direction(self.direction))

    def create_test(self):
        if not self.is_first:
            raise WrongClassError(is_first=self.is_first)
        if len(self.questions) == 0:
            raise QuestionListEmptyError

        self.questions[0].

        
