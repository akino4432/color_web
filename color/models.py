from django.db import models


class Lang(models.Model):
    name = models.CharField('色名', max_length=10)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField('名前', unique=True, max_length=20)
    code = models.CharField('コード', max_length=10)
    lang = models.ForeignKey(Lang, verbose_name='言語', on_delete=models.CASCADE)
    note = models.TextField('ノート', blank=True)

    class Meta:
        db_table = 'color'
        verbose_name = verbose_name_plural = '色'
