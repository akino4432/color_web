from django.test import TestCase
from django.urls import reverse

from color.models import Color, Lang


class TestColorList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Lang.objects.create(name='和名')
        Color.objects.create(name='青色', code='#0000ff', lang=cls.lang)

    def test_get(self):
        res = self.client.get(reverse('color_list'))

        self.assertTemplateUsed(res, 'color/color_list.html')
        self.assertContains(res, '#0000ff')


class TestColorDetail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Lang.objects.create(name='和名')
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang=cls.lang)

    def test_get(self):
        color = self.color
        res = self.client.get(reverse('color_detail', args=(1,)))

        self.assertTemplateUsed(res, 'color/color_detail.html')
        self.assertContains(res, '#0000ff')
        self.assertEqual(res.context['color'], color)

    def test_404(self):
        res = self.client.get(reverse('color_detail', args=(2,)))

        self.assertEqual(res.status_code, 404)


class TestQuestionStart(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Lang.objects.create(name='和名')
        Color.objects.create(name='青色', code='#0000ff', lang=cls.lang)
        Color.objects.create(name='赤色', code='#ff0000', lang=cls.lang)
        Color.objects.create(name='緑色', code='#00ff00', lang=cls.lang)
        Color.objects.create(name='黒色', code='#000000', lang=cls.lang)
        Color.objects.create(name='白色', code='#ffffff', lang=cls.lang)
        Color.objects.create(name='紫色', code='#ff00ff', lang=cls.lang)
        Color.objects.create(name='黄色', code='#ffff00', lang=cls.lang)
        Color.objects.create(name='シアン', code='#00ffff', lang=cls.lang)

    def test_get(self):
        res = self.client.get(reverse('question_start'))

        self.assertTemplateUsed(res, 'color/question_start.html')
        self.assertFalse(res.context['interrupted_data'])

    def test_interrupted_data(self):
        session = self.client.session
        session['now'] = 1
        session.save()
        res = self.client.get(reverse('question_start'))

        self.assertTemplateUsed(res, 'color/question_start.html')
        self.assertTrue(res.context['interrupted_data'])

    def test_post(self):
        res = self.client.post(reverse('question_start'), data={'number': 1, 'difficulty': '1'})

        self.assertRedirects(res, reverse('question'))
        self.assertEqual(self.client.session['number'], 1)
        self.assertEqual(self.client.session['now'], 1)
        self.assertEqual(self.client.session['difficulty'], '1')


class TestQuestion(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Lang.objects.create(name='和名')
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang=cls.lang)

    def test_not_number(self):
        res = self.client.get(reverse('question'))
        self.assertRedirects(res, reverse('question_start'))

    def test_redirects_to_result(self):
        session = self.client.session
        session['number'] = 1
        session['now'] = 0
        session['difficulty'] = '1'
        session['results'] = [{'q_color': self.color, 'c_color': self.color, 'correct': True}]
        session.save()
        res = self.client.get(reverse('question'))
        self.assertRedirects(res, reverse('result'))

    def test_get(self):
        session = self.client.session
        session['number'] = 1
        session['now'] = 1
        session['q_colors'] = [self.color]
        session['choices'] = [self.color, self.color, self.color, self.color]
        session.save()
        res = self.client.get(reverse('question'))
        self.assertTemplateUsed(res, 'color/question.html')
        self.assertContains(res, '青色')
        self.assertContains(res, '#0000ff')


class TestProcessing(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Lang.objects.create(name='和名')
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang=cls.lang)

    def test_405(self):
        res = self.client.get(reverse('processing'))

        self.assertEqual(res.status_code, 405)

    def test_double_transmission(self):
        session = self.client.session
        session['number'] = 1
        session['now'] = 1
        session['results'] = [{'q_color': self.color, 'c_color': self.color, 'correct': True}]
        session.save()
        res = self.client.post(reverse('processing'), data={'check': 2, 'question': 1})
        self.assertRedirects(res, reverse('answer'))

    def test_post(self):
        session = self.client.session
        session['number'] = 1
        session['now'] = 1
        session['q_colors'] = [self.color]
        session['results'] = []
        session.save()
        res = self.client.post(reverse('processing'), data={'check': 1, 'question': 1})
        self.assertRedirects(res, reverse('answer'))
        self.assertEqual(self.client.session['now'], 2)
        self.assertEqual(self.client.session['results'], [{'q_color': self.color,
                                                           'c_color': self.color,
                                                           'correct': True}])


class TestAnswer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Lang.objects.create(name='和名')
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang=cls.lang)

    def test_not_number(self):
        res = self.client.get(reverse('answer'))
        self.assertRedirects(res, reverse('question_start'))

    def test_get(self):
        session = self.client.session
        session['number'] = 1
        session['now'] = 1
        session['results'] = [{'q_color': self.color, 'c_color': self.color, 'correct': True}]
        session.save()
        res = self.client.get(reverse('answer'))
        self.assertTemplateUsed(res, 'color/answer.html')
        self.assertContains(res, '青色')
        self.assertFalse(res.context['last_q'])

    def test_last_q(self):
        session = self.client.session
        session['number'] = 1
        session['now'] = 2
        session['results'] = [{'q_color': self.color, 'c_color': self.color, 'correct': True}]
        session.save()
        res = self.client.get(reverse('answer'))
        self.assertTemplateUsed(res, 'color/answer.html')
        self.assertContains(res, '青色')
        self.assertTrue(res.context['last_q'])


class TestResult(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Lang.objects.create(name='和名')
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang=cls.lang)

    def test_not_result(self):
        res = self.client.get(reverse('result'))
        self.assertRedirects(res, reverse('question_start'))

    def test_get(self):
        session = self.client.session
        session['difficulty'] = '1'
        session['results'] = [{'q_color': self.color, 'c_color': self.color, 'correct': True}]
        session.save()
        res = self.client.get(reverse('result'))
        self.assertTemplateUsed(res, 'color/result.html')
        self.assertContains(res, '青色')
        self.assertContains(res, '難')
        self.assertEqual(res.context['score'], 100)

    def test_zero_score(self):
        session = self.client.session
        session['difficulty'] = '1'
        session['results'] = [{'q_color': self.color, 'c_color': self.color, 'correct': False}]
        session.save()
        res = self.client.get(reverse('result'))
        self.assertTemplateUsed(res, 'color/result.html')
        self.assertContains(res, '青色')
        self.assertContains(res, '難')
        self.assertEqual(res.context['score'], 0)
