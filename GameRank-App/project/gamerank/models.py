# gamerank/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Game(models.Model):
    """
    Modelo que representa un juego.
    Contiene información básica y campos para seguimiento y valoración.
    """
    title = models.CharField(max_length=200, unique=True)  # Título del juego (único)
    xml_id = models.PositiveIntegerField(unique=True, null=True, blank=True)  # ID externo del XML, puede ser nulo
    platform = models.CharField(max_length=100)  # Plataforma (PC, Xbox, etc.)
    genre = models.CharField(max_length=100)     # Género del juego
    developer = models.CharField(max_length=100) # Desarrollador
    publisher = models.CharField(max_length=100) # Editor/Publisher
    release_date = models.DateField()             # Fecha de lanzamiento
    description = models.TextField()               # Descripción del juego
    thumbnail = models.URLField(null=True, blank=True)  # URL de la imagen miniatura
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0
    )  # Valoración media del juego

    # Relación muchos a muchos para usuarios que siguen este juego
    followers = models.ManyToManyField(
        User, related_name='followed_games', blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-average_rating']  # Orden por defecto: valoración media descendente


class Comment(models.Model):
    """
    Modelo que representa un comentario realizado por un usuario a un juego.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que comenta
    content = models.TextField()                              # Texto del comentario
    created_at = models.DateTimeField(auto_now_add=True)     # Fecha de creación

    def __str__(self):
        return f"Comentario de {self.user.username} sobre {self.game.title}"

    class Meta:
        ordering = ['-created_at']  # Orden por defecto: más recientes primero


class Vote(models.Model):
    """
    Modelo para almacenar la puntuación que un usuario da a un juego.
    Un usuario solo puede votar una vez por juego.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='votes')
    score = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(6)],  # Puntuación entre 0 y 5
        help_text="Puntuación de 0 (peor) a 5 (mejor)"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha creación voto
    updated_at = models.DateTimeField(auto_now=True)      # Fecha última actualización voto

    class Meta:
        unique_together = ('user', 'game')  # Restricción: un voto por usuario y juego
        ordering = ['-updated_at']           # Orden por defecto: último actualizado primero

    def __str__(self):
        return f"{self.user.username} votó {self.score} a {self.game.title}"
