from django import forms
from .models import Quiz, Question, Choice


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'max_attempts']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quiz title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter quiz description'
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 180,
                'placeholder': 'Time limit in minutes'
            }),
            'max_attempts': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': 'Maximum attempts allowed'
            })
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your question'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'question-type-select'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'value': 1
            })
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']
        widgets = {
            'choice_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter choice text'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


# For handling multiple choices in a single form
ChoiceFormSet = forms.modelformset_factory(
    Choice,
    form=ChoiceForm,
    extra=4,
    can_delete=True
)
