from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import UserConsent, Students
from .serializers import LoginSerializer, UserInfoSerializer, ConsentSerializer, MeSerializer


def get_tokens_for_user(user):
    """Генерирует JWT токены"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }

# Вход
class LoginView(APIView):
    """POST /api/auth/login/ - вход"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # ЗАГЛУШКА!!!!!!
        # Когда ТПУ даст доступ - заменить на запрос к их API
        user = User.objects.filter(username=username).first()

        if not user:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f'{username}@tpu.ru',
                first_name="Иван",
                last_name="Иванов",
            )
        else:
            if not user.check_password(password):
                return Response({
                    'error': "Неверный логин и пароль"
                },status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем согласие
        consent = UserConsent.objects.filter(user=user, is_given=True).first()

        if not consent:
            temp_token = get_tokens_for_user(user)['access']
            return Response({
                'need_consent': True,
                'temp_token': temp_token,
                'message': 'Необходимо дать согласие на обработку персональных данных'
            })

        tokens = get_tokens_for_user(user)
        return Response({
            'need_consent': False,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserInfoSerializer(user).data,
        })


# Согласие
class ConsentView(APIView):
    """POST - /api/auth/consent/ - согласие"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConsentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        consent_given = serializer.validated_data['consent']
        temp_token = serializer.validated_data['temp_token']

        # Извлекаем пользователя из temp token
        try:
            token = AccessToken(temp_token)
            user_id = token['user_id']
            user = User.objects.get(id=user_id)
        except Exception:
            return Response({
                'error': 'Недействительный токен'
            }, status=status.HTTP_400_BAD_REQUEST)

        if consent_given:
            # Сохраняем согласие
            UserConsent.objects.update_or_create(
                user=user,
                defaults={
                    'ip_address': self.get_client_ip(request),
                    'is_given': True,
                }
            )

            # Присваиваем роль student
            student_group, _ = Group.objects.get_or_create(name='student')
            user.groups.add(student_group)

            # Связываем с моделью Students
            student = Students.objects.filter(
                someone_id=f'tpu-{user.username}'
            ).first()
            if student:
                student.user = user
                student.save()

            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'Согласие сохранено',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': UserInfoSerializer(user).data
            })
        else:
            # Отказ - удаляем запись о согласии
            UserConsent.objects.filter(user=user).delete()
            return Response({
                'message': 'Вы отказились от обработки данных. Для участия в рейтинге необходимо необходимо дать '
                           'согласие.',
                'redirect': '/'
            })

    def get_client_ip(self, request):
        """Получает IP-адрес пользователя"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Профиль
class MeView(APIView):
    """GET /api/auth/me/ - возвращает данные текущего пользователя. Требует авторизацию"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(MeSerializer(user).data)


# Выход
class LogoutView(APIView):
    """POST /api/auth/logout/ - блокирует refresh token (выход из системы)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response({'message': 'Выход выполнен'}, status=status.HTTP_200_OK)


# Обновление токена
class RefreshTokenView(APIView):
    """POST /api/auth/refresh/ - возвращает новую пару токенов"""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'Refresh token не предоставлен'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            return Response({
                'access': str(token.access_token),
                'refresh': str(token)
            })
        except Exception:
            return Response({
                'error': 'Недействительный refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)