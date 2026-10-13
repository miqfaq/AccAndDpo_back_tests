from fastapi import APIRouter, Depends
from src.security.security import security
from authx import TokenPayload
from src.authorisation.login import require_role
from src.tests.schemas import TestUpdateSchema, TestCreateSchema, QuestionCreateSchema, AnswerCreateSchema
from src.tests.databaseWork import  get_tests, get_test_TestId, get_tests_UserId, update_test_TestId, delete_test, add_test


router = APIRouter(
    prefix="/tests",
    tags=["testPage"]
    )



@router.get('/', dependencies=[Depends(security.access_token_required)]) #
def get_test_list():
    """все тесты"""
    return get_tests()

@router.get('/get_list_uid', dependencies=[Depends(security.access_token_required)])#
def get_test_list_uid(uid: str):
    """тесты по юид"""
    return get_tests_UserId(user_id = uid)

@router.patch('/patchtest')#
def patch_test_uid(test_id:str, data:TestUpdateSchema, payload: TokenPayload = Depends(require_role('admin'))):
    """Обновление конкретного теста"""
    update_test_TestId(test_id=test_id, data=data)

@router.post("/addTestuid")#
def add_tests(test:TestCreateSchema, useruid: str = 'd95bec53-62c2-40df-a005-29f717d88a30' ,payload: TokenPayload = Depends(require_role('admin'))):
    """Добавление Теста по юид 
      Default_user это пользователь на которм висят все тесты"""
    add_test(test=test, questions=test.questions, useruid = useruid)

@router.delete("/deletetestfromlist")#
def delete_post_list(testId, userId, payload: TokenPayload = Depends(require_role('admin'))):
    """Удалить тест по пользователю и айди теста"""
    delete_test(userId=userId, testId=testId)

@router.post("/addTest")
def add_test_global():
    """Глобально добавляет тест, ни для какого пользователя, просто создает тест который можно добавить по uid и test_id """
