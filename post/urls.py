from django.urls import path

from .views import PostListCreateView, PostRetrieveUpdateDestroyView, PostSearchView, UserPostStatisticsView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post_list_create'),
    path('/<int:pk>', PostRetrieveUpdateDestroyView.as_view(), name='post_detail'),
    path('/search/<str:search_term>', PostSearchView.as_view(), name='post_search'),
    path('/statistics/<int:user_id>', UserPostStatisticsView.as_view(), name='user-post-statistics'),

]
