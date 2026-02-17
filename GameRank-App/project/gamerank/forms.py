from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Formulario de registro extendiendo UserCreationForm
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Obligatorio. Introduce una dirección de correo válida."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email


# ——— Formularios embebidos para votaciones y comentarios ———

class VoteForm(forms.Form):
    score = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(6)],
        widget=forms.RadioSelect,
        label="Tu puntuación"
    )

class CommentForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows':3, 'placeholder':'Escribe tu comentario…'}),
        label="Comentario"
    )


# Opciones para personalización visual en SettingsForm
FONT_CHOICES = [
    ('Arial, sans-serif', 'Arial'),
    ('"Times New Roman", serif', 'Times New Roman'),
    ('"Courier New", monospace', 'Courier New'),
    ('Georgia, serif', 'Georgia'),
    ('Verdana, sans-serif', 'Verdana'),
]

SIZE_CHOICES = [
    ('14px', 'Pequeño'),
    ('16px', 'Mediano'),
    ('18px', 'Grande'),
    ('20px', 'Muy grande'),
]

class SettingsForm(forms.Form):
    alias = forms.CharField(
        label="Nombre visible",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Tu alias…'})
    )
    font_family = forms.ChoiceField(
        label="Tipo de letra",
        choices=FONT_CHOICES
    )
    font_size = forms.ChoiceField(
        label="Tamaño de texto",
        choices=SIZE_CHOICES
    )
