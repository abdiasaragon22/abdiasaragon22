# gamerank/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'gamerank'

urlpatterns = [

    # ----- Autenticación -----
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='gamerank:home'), name='logout'),
    path('register/', views.register, name='register'),

    # ----- Páginas principales -----
    path('', views.home, name='home'),
    path('all-games/', views.all_games, name='all_games'),
    path('all-games/<int:xml_id>/', views.game_detail, name='game_detail'),

    # ----- Acciones sobre juegos -----
    path('game/<int:xml_id>/follow/', views.follow_game, name='follow_game'),
    path('game/<int:xml_id>/json/', views.game_detail_json, name='game_detail_json'),

    # ----- Comentarios -----
    path('game/<int:xml_id>/comments/', views.comments_list, name='comments_list'),
    path('game/<int:xml_id>/comments/post/', views.comments_post, name='comments_post'),

    # ----- Vista dinámica de juego -----
    path('game/<int:xml_id>/dynamic/', views.game_detail_dynamic, name='game_detail_dynamic'),

    # ----- Perfil y configuraciones del usuario -----
    path('user/votes/', views.user_votes, name='user_votes'),
    path('user/followed/', views.user_followed, name='user_followed'),
    path('profile/', views.user_profile, name='user_profile'),
    path('settings/', views.settings_view, name='settings'),

    # ----- Página de ayuda -----
    path('help/', views.help_view, name='help'),
]
