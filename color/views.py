from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.views.decorators.http import require_POST

from color.models import Color
from color.forms import SearchForm, QuestionConditions
from color.modules import RGBColor, OrderColor, get_random_colors, create_choices


def color_list(request):
    colors = Color.objects.all()

    form = SearchForm(request.GET)
    if form.is_valid():
        name = form.cleaned_data.get('name')
        if name:
            colors = colors.filter(name__contains=name)
        name_lang = form.cleaned_data.get('lang')
        if name_lang:
            colors = colors.filter(lang=name_lang)

    colors = OrderColor.order_by_category(colors, True)

    return TemplateResponse(request, 'color/color_list.html', {'colors': colors, 'form': form})


def color_detail(request, color_id):
    try:
        color = Color.objects.get(id=color_id)
    except Color.DoesNotExist:
        raise Http404
    rgb = RGBColor(code=color.code)

    colors = Color.objects.all()

    similar_color_list = OrderColor.order_by_similar(colors, color)
    similar = similar_color_list[1:11]  # 0は同色

    return TemplateResponse(request, 'color/color_detail.html', {'color': color, 'rgb': str(rgb), 'similar': similar})


def question_start(request):
    if request.method == 'POST':
        form = QuestionConditions(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get('number')
            difficulty = form.cleaned_data.get('difficulty')
            request.session['number'] = number
            request.session['now'] = 1

            q_colors = get_random_colors(number)
            request.session['q_colors'] = q_colors

            choices = create_choices(q_colors[0], difficulty)
            request.session['choices'] = choices

            request.session['difficulty'] = difficulty
            request.session['results'] = []
            return HttpResponseRedirect(reverse('question'))
    else:
        form = QuestionConditions()
        interrupted_data = False
        if request.session.get('now'):
            interrupted_data = True
        context = {'form': form, 'interrupted_data': interrupted_data}
        return TemplateResponse(request, 'color/question_start.html', context)


def question(request):
    number = request.session.get('number')
    if not number:  # 一度もスタートせずにアクセスした場合
        return HttpResponseRedirect(reverse('question_start'))

    now = request.session.get('now', 0)

    if now > number or now == 0:  # 最終問題の解答で中断して復帰した場合or結果後にアクセスした場合
        return HttpResponseRedirect(reverse('result'))

    q_color = request.session['q_colors'][now-1]

    choices = request.session['choices']

    context = {'now': now, 'q_color': q_color, 'choices': choices}
    return TemplateResponse(request, 'color/question.html', context)


@require_POST
def processing(request):
    now = request.session.get('now')

    # 二重送信のチェック
    check = int(request.POST['check'])
    if check != now:
        return HttpResponseRedirect(reverse('answer'))

    chosen_id = request.POST['question']
    c_color = Color.objects.get(id=chosen_id)

    last_q = False
    if now >= request.session['number']:
        last_q = True

    q_color = request.session['q_colors'][now - 1]

    correct = False
    if q_color.id == c_color.id:
        correct = True

    # 次の問題の準備
    if not last_q:
        next_q_color = request.session['q_colors'][now]
        next_choices = create_choices(next_q_color)
        request.session['choices'] = next_choices

    # 結果追加
    result_dict = {
        'q_color': q_color,
        'c_color': c_color,
        'correct': correct
    }
    results = request.session['results']
    results.append(result_dict)
    request.session['results'] = results
    request.session['now'] = now + 1
    return HttpResponseRedirect(reverse('answer'))


def answer(request):
    number = request.session.get('number')
    if not number:  # 一度もスタートせずにアクセスした場合
        return HttpResponseRedirect(reverse('question_start'))

    now = request.session.get('now', number+1)
    now -= 1

    last_q = False
    if now >= request.session['number']:
        last_q = True

    result = request.session['results'][-1]
    q_color = result['q_color']
    c_color = result['c_color']
    correct = result['correct']

    context = {'now': now, 'last_q': last_q, 'q_color': q_color, 'c_color': c_color, 'correct': correct}
    return TemplateResponse(request, 'color/answer.html', context)


def result(request):
    if not request.session.get('results'):
        return HttpResponseRedirect(reverse('question_start'))

    if request.session.get('now'):
        del request.session['now']

    difficulty = request.session['difficulty']
    difficulty_dict = {'1': '難', '2': '中', '3': '易'}
    difficulty = difficulty_dict[difficulty]

    results = request.session['results']
    number = len(results)

    # 点数計算
    correct_count = 0
    for result in results:
        if result['correct']:
            correct_count += 1
    score = round((correct_count / number) * 100)

    context = {'results': results, 'difficulty': difficulty, 'score': score}
    return TemplateResponse(request, 'color/result.html', context)



