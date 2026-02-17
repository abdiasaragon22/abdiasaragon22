# gamerank/admin.py
from django.contrib import admin
from .models import Game, Comment, Vote

admin.site.register(Game)
admin.site.register(Comment)
admin.site.register(Vote)

