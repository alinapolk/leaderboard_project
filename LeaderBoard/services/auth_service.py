from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from LeaderBoard.models import UserConsent, Students


def get_tokens_for_user(user: User) -> dict:
    """Генерирует JWT токены для пользователя"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def authenticate_user(username: str, password: str) -> tuple:
    """
    Аутентифицирует пользователя.
    
    Возвращает:
        (user, error_message) - если ошибка, user будет None
        (user, None) - если успех
    """
    user = User.objects.filter(username=username).first()

    if not user:
        # !!! ЗАГЛУШКА !!!: создаём пользователя, если его нет
        # Когда ТПУ даст доступ - заменить на запрос к их API
        user = User.objects.create_user(
            username=username,
            password=password,
            email=f'{username}@tpu.ru',
            first_name="Иван",
            last_name="Иванов",
        )
    else:
        if not user.check_password(password):
            return None, "Неверный логин и пароль"

    return user, None


def check_user_consent(user: User) -> bool:
    """Проверяет, дал ли пользователь согласие на обработку данных"""
    return UserConsent.objects.filter(user=user, is_given=True).exists()


def create_or_update_consent(user: User, ip_address: str, is_given: bool) -> UserConsent:
    """Создаёт или обновляет согласие пользователя"""
    consent, created = UserConsent.objects.update_or_create(
        user=user,
        defaults={
            'ip_address': ip_address,
            'is_given': is_given,
        }
    )
    return consent


def link_student_to_user(user: User) -> Students:
    """
    Связывает студента с пользователем.
    
    Ищет студента по someone_id = 'tpu-{username}'
    """
    student = Students.objects.filter(
        someone_id=f'tpu-{user.username}'
    ).first()
    
    if student:
        student.user = user
        student.save(update_fields=['user'])
    
    return student


def assign_student_role(user: User) -> None:
    """Присваивает пользователю роль студента"""
    student_group, _ = Group.objects.get_or_create(name='student')
    user.groups.add(student_group)


@transaction.atomic
def complete_consent_flow(user: User, ip_address: str, consent_given: bool) -> dict:
    """
    Полный процесс обработки согласия.
    
    Возвращает:
        {
            'success': bool,
            'tokens': dict или None,
            'message': str
        }
    """
    if consent_given:
        # Сохраняем согласие
        create_or_update_consent(user, ip_address, is_given=True)
        
        # Присваиваем роль
        assign_student_role(user)
        
        # Связываем со студентом
        link_student_to_user(user)
        
        # Генерируем токены
        tokens = get_tokens_for_user(user)
        
        return {
            'success': True,
            'tokens': tokens,
            'message': 'Согласие сохранено'
        }
    else:
        # Отказ - удаляем запись о согласии
        UserConsent.objects.filter(user=user).delete()
        
        return {
            'success': False,
            'tokens': None,
            'message': 'Вы отказались от обработки данных. Для участия в рейтинге необходимо дать согласие.'
        }