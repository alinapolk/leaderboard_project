from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from django.contrib.auth.models import User

from LeaderBoard.models import UserConsent, Students
from LeaderBoard.serializers import (
    LoginSerializer,
    UserInfoSerializer,
    ConsentSerializer,
    MeSerializer,
    StudentLeaderBoardSerializer
)
from LeaderBoard.services import (
    get_tokens_for_user,
    authenticate_user,
    check_user_consent,
    complete_consent_flow
)
from LeaderBoard.common.utils import get_client_ip


class LoginView(APIView):
    """POST /api/auth/login/ - вход"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Аутентификация через сервис
        user, error = authenticate_user(username, password)
        
        if error:
            return Response({
                'error': error
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем согласие через сервис
        has_consent = check_user_consent(user)

        if not has_consent:
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

        # Получаем IP клиента через утилиту
        ip_address = get_client_ip(request)

        # Полный процесс обработки согласия через сервис
        result = complete_consent_flow(user, ip_address, consent_given)

        if result['success']:
            return Response({
                'message': result['message'],
                'access': result['tokens']['access'],
                'refresh': result['tokens']['refresh'],
                'user': UserInfoSerializer(user).data
            })
        else:
            return Response({
                'message': result['message'],
                'redirect': '/'
            })


class MeView(APIView):
    """GET /api/auth/me/ - возвращает данные текущего пользователя"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(MeSerializer(user).data)


class LogoutView(APIView):
    """POST /api/auth/logout/ - блокирует refresh token"""
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


class MyRatingView(APIView):
    """
    GET /api/auth/me/rating/
    Возвращает личный рейтинг текущего авторизованного студента
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Находим студента через related_name
        try:
            student = user.student_profile
        except Students.DoesNotExist:
            return Response(
                {'error': 'Студент не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Берём всех студентов для расчёта позиции
        all_students = list(Students.objects.filter(
            history_work_all__gt=0
        ))

        if not all_students:
            return Response(
                {'error': 'Нет данных для расчёта рейтинга'},
                status=status.HTTP_404_NOT_FOUND
            )

        # ИСПРАВЛЕНО: используем единую формулу из сервисов
        from LeaderBoard.services import calculate_rating_score
        
        my_rating = calculate_rating_score(student.study_score, student.history_work_all)

        # Сортируем всех по рейтингу
        ratings = [(s, calculate_rating_score(s.study_score, s.history_work_all)) for s in all_students]
        ratings.sort(key=lambda x: x[1], reverse=True)

        # Находим позицию студента
        position = next(
            (i + 1 for i, (s, r) in enumerate(ratings) if s.login == student.login),
            None
        )

        return Response({
            'position': position,
            'total_students': len(all_students),
            'rating_score': my_rating,
            'student': StudentLeaderBoardSerializer(student).data
        })