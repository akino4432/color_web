from django.test import TestCase
from django.urls import reverse

from color.models import Color


class TestColorList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang='和名')

    def test_get(self):
        res = self.client.get(reverse('color_list'))

        self.assertTemplateUsed(res, 'color/color_list.html')
        self.assertContains(res, '#0000ff')


class TestColorDetail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang='和名')

    def test_get(self):
        color = self.color
        res = self.client.get(reverse('color_detail', args=(1,)))

        self.assertTemplateUsed(res, 'color/color_detail.html')
        self.assertContains(res, '#0000ff')
        self.assertEqual(res.context['color'], color)

    def test_404(self):
        res = self.client.get(reverse('color_detail', args=(2,)))

        self.assertEqual(res.status_code, 404)


class TestNewColor(TestCase):
    def test_get(self):
        res = self.client.get(reverse('new_color'))

        self.assertTemplateUsed(res, 'color/new_color.html')

    def test_post(self):
        res = self.client.post(reverse('new_color'), data={'name': '青色', 'code': '#0000ff', 'lang': '和名'})
        color = Color.objects.get(id=1)

        self.assertRedirects(res, reverse('color_list'))
        self.assertEqual(color.name, '青色')

    def test_invalid(self):
        res = self.client.post(reverse('new_color'), data={'code': '#0000ff'})

        self.assertTemplateUsed(res, 'color/new_color.html')
        self.assertFalse(res.context['form'].is_valid())


class TestEditColor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang='和名')

    def test_get(self):
        res = self.client.get(reverse('edit_color', args=(1,)))

        self.assertTemplateUsed(res, 'color/edit_color.html')
        self.assertEqual(res.context['form'].instance, self.color)

    def test_404(self):
        res = self.client.get(reverse('edit_color', args=(2,)))

        self.assertEqual(res.status_code, 404)

    def test_post(self):
        color = self.color
        res = self.client.post(reverse('edit_color', args=(1,)), data={'name': '赤色', 'code': '#ff0000', 'lang': '和名'})

        self.assertRedirects(res, reverse('color_detail', args=(color.id,)))
        color.refresh_from_db()
        self.assertEqual(color.name, '赤色')
        self.assertEqual(color.code, '#ff0000')
        self.assertEqual(color.lang, '和名')

    def test_invalid(self):
        res = self.client.post(reverse('edit_color', args=(1,)), data={'name': '無色'})

        self.assertTemplateUsed(res, 'color/edit_color.html')
        self.assertFalse(res.context['form'].is_valid())


class TestDeleteColor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.color = Color.objects.create(name='青色', code='#0000ff', lang='和名')

    def test_get(self):
        color = self.color
        res = self.client.get(reverse('delete_color', args=(1,)))

        self.assertTemplateUsed(res, 'color/delete_color.html')
        self.assertEqual(res.context['color'], color)
        self.assertContains(res, '青色')

    def test_post(self):
        res = self.client.post(reverse('delete_color', args=(1,)))

        self.assertRedirects(res, reverse('color_list'))
        self.assertFalse(Color.objects.exists())
