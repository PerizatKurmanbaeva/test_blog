from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework import views
from django.db.models import Count

from test_Invest_Era.permissions import IsAuthenticatedOrReadOnly
from .models import Posts
from .serializers import PostSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from .pagination import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from django.db.models.functions import TruncMonth


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Создание нового поста (необходим токен)",
        security=[{'Token': []}],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostSerializer
    http_method_names = ['get', 'put', 'delete']
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostSearchView(generics.ListAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        search_term = self.kwargs.get('search_term', None)
        if search_term:
            return Posts.objects.filter(
                Q(title__icontains=search_term) | Q(content__icontains=search_term)
            )
        return Posts.objects.all()


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserPostStatisticsView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Группируем посты по месяцам и подсчитываем их количество
        posts_per_month = (
            Posts.objects.filter(author=user)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(post_count=Count('id'))
            .order_by('month')
        )

        # Рассчитываем среднее количество постов за месяц
        total_posts = sum([entry['post_count'] for entry in posts_per_month])
        total_months = len(posts_per_month)
        if total_months == 0:
            average_posts_per_month = 0
        else:
            average_posts_per_month = total_posts / total_months

        # Формируем JSON-ответ
        data = {
            "user_id": user.id,
            "username": user.username,
            "total_posts": total_posts,
            "total_months": total_months,
            "average_posts_per_month": average_posts_per_month,
            "posts_per_month": [
                {
                    "month": entry["month"].strftime("%Y-%m"),
                    "post_count": entry["post_count"]
                }
                for entry in posts_per_month
            ]
        }

        return Response(data, status=status.HTTP_200_OK)