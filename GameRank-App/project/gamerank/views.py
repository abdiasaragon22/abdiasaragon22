# gamerank/views.py

from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.db.models import Avg, Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import requests
import xml.etree.ElementTree as ET
import json

from .models import Game, Comment, Vote
from .forms import RegistrationForm, SettingsForm, CommentForm, VoteForm

User = get_user_model()

# --------------------
# Utilidades XML / Datos
# --------------------

def fetch_games(xml_url):
    """
    Hace la petición al XML y parsea todos los <game> en una lista de dicts,
    capturando cada campo de forma case-insensitive y namespace-insensitive.
    """
    try:
        resp = requests.get(xml_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise Http404(f"Error obteniendo el listado de juegos: {e}")

    root = ET.fromstring(resp.content)

    def get_tag_text(el, tag_name):
        # busca child.tag terminando en tag_name (por ej: "id", "ID", "{ns}id")
        for child in el:
            if child.tag.lower().endswith(tag_name.lower()):
                return (child.text or '').strip()
        return ''

    games = []
    for game_el in root.findall('.//game'):
        games.append({
            'id':                    get_tag_text(game_el, 'id'),
            'title':                 get_tag_text(game_el, 'title'),
            'developer':             get_tag_text(game_el, 'developer'),
            'publisher':             get_tag_text(game_el, 'publisher'),
            'genre':                 get_tag_text(game_el, 'genre'),
            'platform':              get_tag_text(game_el, 'platform'),
            'release_date':          get_tag_text(game_el, 'release_date'),
            'short_description':     get_tag_text(game_el, 'short_description'),
            'thumbnail':             get_tag_text(game_el, 'thumbnail'),
            'freetogame_profile_url':get_tag_text(game_el, 'freetogame_profile_url'),
            'game_url':              get_tag_text(game_el, 'game_url'),
        })
    return games

def filter_valid_release_date(games):
    """Filtra juegos que tienen fecha de lanzamiento válida (día distinto de 00)."""
    valid = []
    for g in games:
        rd = g.get('release_date', '')
        parts = rd.split('-')
        if len(parts) == 3 and parts[2] != '00':
            valid.append(g)
    return valid

def unique_by_title(games):
    """Filtra juegos únicos por título, eliminando duplicados."""
    seen = set()
    unique = []
    for g in games:
        title = g.get('title')
        if title and title not in seen:
            seen.add(title)
            unique.append(g)
    return unique


# --------------------
# Vistas principales de juegos
# --------------------

def all_games(request):
    """
    Vista que muestra el listado de juegos desde XML + datos BD,
    con información de si el usuario los sigue o no.
    """
    xml_url     = 'https://gitlab.eif.urjc.es/cursosweb/2024-2025/final-gamerank/-/raw/main/listado1.xml'
    raw_games   = fetch_games(xml_url)
    valid_games = filter_valid_release_date(raw_games)
    games       = unique_by_title(valid_games)

    # Juegos seguidos por el usuario autenticado
    user_followed_ids = []
    if request.user.is_authenticated:
        user_followed_ids = [str(x) for x in request.user.followed_games.values_list('xml_id', flat=True)]

    # Carga info BD (número votos y media) para todos los juegos
    db_games = Game.objects.filter(xml_id__in=[g['id'] for g in games]).annotate(
        num_votes=Count('votes'),
        avg_rating=Avg('votes__score')
    )
    db_games_dict = {str(g.xml_id): g for g in db_games}

    # Añade datos BD al dict de juegos
    for g in games:
        game_db = db_games_dict.get(str(g['id']))
        if game_db:
            g['average_rating'] = round(game_db.avg_rating or 0, 2)
            g['num_votes'] = game_db.num_votes
        else:
            g['average_rating'] = 0
            g['num_votes'] = 0

    # Ordenar juegos por rating descendente
    games.sort(key=lambda x: x['average_rating'], reverse=True)

    return render(request, 'gamerank/all_games.html', {
        'games': games,
        'user_followed_ids': user_followed_ids,
    })


def home(request):
    """Vista simple home con juegos."""
    games = Game.objects.all()
    return render(request, 'gamerank/home.html', {'games': games})

def game_detail(request, xml_id):
    """
    Vista detallada de un juego con comentarios y votaciones.
    Procesa envío de comentarios y votos.
    """
    game = get_object_or_404(Game, xml_id=xml_id)

    # Procesar envío comentario
    if request.method == 'POST' and 'comment_submit' in request.POST:
        if not request.user.is_authenticated:
            return redirect('gamerank:login')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            Comment.objects.create(
                game=game,
                user=request.user,
                content=comment_form.cleaned_data['content'],
            )
            return redirect('gamerank:game_detail', xml_id=xml_id)
    else:
        comment_form = CommentForm()

    # Procesar votos usuario
    user_vote = None
    vote_form = None
    if request.user.is_authenticated:
        try:
            existing_vote = Vote.objects.get(user=request.user, game=game)
            user_vote = existing_vote.score
        except Vote.DoesNotExist:
            existing_vote = None

        if request.method == 'POST' and 'vote_submit' in request.POST:
            if existing_vote:
                return redirect('gamerank:game_detail', xml_id=xml_id)
            vote_form = VoteForm(request.POST)
            if vote_form.is_valid():
                sc = vote_form.cleaned_data['score']
                Vote.objects.create(user=request.user, game=game, score=sc)
                avg = game.votes.aggregate(avg_score=Avg('score'))['avg_score'] or 0
                game.average_rating = round(avg, 2)
                game.save(update_fields=['average_rating'])
                return redirect('gamerank:game_detail', xml_id=xml_id)

        if not existing_vote:
            vote_form = VoteForm()

    # Obtener comentarios ordenados
    comments = game.comments.order_by('-created_at')

    # Saber si usuario sigue el juego
    is_following = False
    if request.user.is_authenticated:
        is_following = game.followers.filter(id=request.user.id).exists()

    # Renderizar plantilla con datos
    return render(request, 'gamerank/game_detail.html', {
        'game': game,
        'comments': comments,
        'comment_form': comment_form,
        'vote_form': vote_form,
        'user_vote': user_vote,
        'is_following': is_following,
    })


def game_detail_json(request, xml_id):
    """Descarga datos JSON del juego."""
    try:
        game = Game.objects.get(xml_id=xml_id)
    except Game.DoesNotExist:
        raise Http404("Juego no encontrado")

    num_comments = game.comments.count()
    num_votes = game.votes.count()

    data = {
        'xml_id': game.xml_id,
        'title': game.title,
        'developer': game.developer,
        'publisher': game.publisher,
        'genre': game.genre,
        'platform': game.platform,
        'release_date': game.release_date.isoformat() if game.release_date else None,
        'description': game.description,
        'thumbnail': game.thumbnail,
        'average_rating': float(game.average_rating) if game.average_rating is not None else None,
        'num_votes': num_votes,
        'num_comments': num_comments,
    }

    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="game_{game.xml_id}.json"'
    return response


# --------------------
# Funciones y vistas de usuarios
# --------------------

@login_required
def follow_game(request, xml_id):
    """
    Alterna follow/unfollow para un juego. Si no existe, lo crea desde XML.
    """
    xml_url = 'https://gitlab.eif.urjc.es/cursosweb/2024-2025/final-gamerank/-/raw/main/listado1.xml'
    raw = fetch_games(xml_url)
    valid = filter_valid_release_date(raw)
    games = unique_by_title(valid)

    data = next((g for g in games if g['id'] == str(xml_id)), None)
    if not data:
        raise Http404(f"Juego {xml_id} no encontrado en el feed XML.")

    game_obj, created = Game.objects.get_or_create(
        xml_id=xml_id,
        defaults={
            'title': data['title'],
            'platform': data['platform'],
            'genre': data['genre'],
            'developer': data['developer'],
            'publisher': data['publisher'],
            'release_date': data['release_date'],
            'description': data['short_description'],
            'thumbnail': data['thumbnail'],
        }
    )

    if request.user in game_obj.followers.all():
        game_obj.followers.remove(request.user)
    else:
        game_obj.followers.add(request.user)

    return redirect(request.POST.get('next') or 'gamerank:all_games')


@login_required
def user_votes(request):
    """Listado de votos del usuario autenticado."""
    user_votes = request.user.votes.select_related('game').order_by('-score')
    user_followed_ids = Game.objects.filter(followers=request.user).values_list('xml_id', flat=True)
    context = {
        'user_votes': user_votes,
        'user_followed_ids': list(user_followed_ids),
    }
    return render(request, 'gamerank/user_votes.html', context)


@login_required
def user_followed(request):
    """Listado de juegos seguidos por el usuario con su voto si existe."""
    games = list(request.user.followed_games.all())
    votes = Vote.objects.filter(user=request.user, game__in=games)
    user_votes = {v.game_id: v.score for v in votes}
    for g in games:
        g.user_vote = user_votes.get(g.id, None)
    return render(request, 'gamerank/user_followed.html', {'games': games})


@login_required
def user_profile(request):
    """Perfil de usuario con estadísticas de votos y juegos seguidos."""
    user = request.user
    votes_qs = Vote.objects.filter(user=user)
    total_votes = votes_qs.count()
    avg_score = votes_qs.aggregate(avg=Avg('score'))['avg'] or 0
    voted_games = votes_qs.select_related('game')
    followed_games = user.followed_games.all()

    return render(request, 'gamerank/user_profile.html', {
        'total_votes': total_votes,
        'avg_score': round(avg_score, 2),
        'voted_games': voted_games,
        'followed_games': followed_games,
    })


@login_required
def settings_view(request):
    """Configuración del usuario guardada en sesión."""
    initial = {
        'alias': request.session.get('alias', request.user.username),
        'font_family': request.session.get('font_family', 'Arial, sans-serif'),
        'font_size': request.session.get('font_size', '16px'),
    }

    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            request.session['alias'] = form.cleaned_data['alias']
            request.session['font_family'] = form.cleaned_data['font_family']
            request.session['font_size'] = form.cleaned_data['font_size']
            messages.success(request, "Configuración guardada.")
            return redirect('gamerank:settings')
    else:
        form = SettingsForm(initial=initial)

    return render(request, 'gamerank/settings.html', {'form': form})


# --------------------
# Comentarios - vistas
# --------------------

def comments_list(request, xml_id):
    """Carga la lista de comentarios para un juego."""
    game = get_object_or_404(Game, xml_id=xml_id)
    comments = game.comments.order_by('-created_at')
    return render(request, 'gamerank/comments_list.html', {'comments': comments})


@login_required
@require_http_methods(["GET", "POST"])
def comments_post(request, xml_id):
    """Añade un comentario al juego (Ajax o POST normal)."""
    game = get_object_or_404(Game, xml_id=xml_id)

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = Comment.objects.create(
                game=game,
                user=request.user,
                content=comment_form.cleaned_data['content'],
            )
            # Retorna solo el nuevo comentario para añadir a la lista
            return render(request, 'gamerank/comment.html', {'comment': comment})
        else:
            return render(request, 'gamerank/comment_form.html', {'comment_form': comment_form, 'game': game})
    else:
        comment_form = CommentForm()
        return render(request, 'gamerank/comment_form.html', {'comment_form': comment_form, 'game': game})


def game_detail_dynamic(request, xml_id):
    """Vista dinámica con menos datos para actualización asíncrona."""
    game = get_object_or_404(Game, xml_id=xml_id)
    is_following = False
    if request.user.is_authenticated:
        is_following = game.followers.filter(id=request.user.id).exists()

    return render(request, 'gamerank/game_detail_dynamic.html', {
        'game': game,
        'is_following': is_following,
    })


# --------------------
# Autenticación y Registro
# --------------------

def register(request):
    """Registro de usuario con login automático."""
    if request.user.is_authenticated:
        return redirect('gamerank:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada.")
            return redirect('gamerank:home')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """Logout, redirige a home."""
    if request.user.is_authenticated:
        logout(request)
    return redirect('gamerank:home')


# --------------------
# Vista de ayuda
# --------------------

def help_view(request):
    """Página de ayuda estática."""
    return render(request, 'gamerank/help.html')
