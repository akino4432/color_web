from django import forms

from color.models import Color, Lang


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ('name', 'code', 'lang', 'note',)


class SearchForm(forms.Form):
    name = forms.CharField(label='色名', required=False)
    lang = forms.ModelChoiceField(queryset=Lang.objects.all(), label='言語', required=False)


class QuestionConditions(forms.Form):
    number = forms.IntegerField(label='問題数', max_value=30, min_value=1, initial=5, required=True)
    difficulty = forms.ChoiceField(label='難易度', choices=[(1, '難'), (2, '中'), (3, '易')], initial=2, required=True)
