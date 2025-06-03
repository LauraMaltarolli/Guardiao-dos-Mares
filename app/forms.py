from django import forms
from .models import Denuncia, Evento

class DenunciaForm(forms.ModelForm):
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        label='Data da Ocorrência'
    )
    imagem = forms.ImageField(
        required=False,
        label='Imagem (Opcional)',
        widget=forms.FileInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    )
    
    descricao = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        label='Descrição da Denúncia'
    )
    local = forms.CharField(
        max_length=100,
        label='Local da Ocorrência',
        widget=forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    )

    class Meta:
        model = Denuncia
        fields = ['descricao', 'data', 'local', 'imagem']

class EventoForm(forms.ModelForm):
    titulo = forms.CharField(
        max_length=100,
        label='Título do Evento',
        widget=forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    )
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        label='Data do Evento'
    )

    descricao = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        label='Descrição do Evento'
    )

    local = forms.CharField(
        max_length=100,
        label='Local do Evento',
        widget=forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    )

    class Meta:
        model = Evento
        fields = ['titulo', 'descricao', 'data', 'local']