from django import forms

class ChatbotForm(forms.Form):
    user_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label='Enter your query'
    )