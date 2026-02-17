# gamerank/context_processors.py

from .models import Comment, Vote
from .views import fetch_games, filter_valid_release_date, unique_by_title

XML_URL = 'https://gitlab.eif.urjc.es/cursosweb/2024-2025/final-gamerank/-/raw/main/listado1.xml'

def site_metrics(request):
    # 1) Total de juegos en el feed XML
    raw = fetch_games(XML_URL)
    valid = filter_valid_release_date(raw)
    unique = unique_by_title(valid)
    total_games = len(unique)

    # 2) Total de comentarios en la BD
    total_comments = Comment.objects.count()

    # 3) Métricas de usuario
    user = request.user
    if user.is_authenticated:
        user_games_voted    = Vote.objects.filter(user=user).count()
        user_comments_count = Comment.objects.filter(user=user).count()
    else:
        user_games_voted    = 0
        user_comments_count = 0

    return {
        'total_games'        : total_games,
        'total_comments'     : total_comments,
        'user_games_voted'   : user_games_voted,
        'user_comments_count': user_comments_count,
    }
