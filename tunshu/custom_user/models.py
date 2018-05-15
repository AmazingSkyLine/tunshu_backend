from django.db import models


class User(models.Model):
    nickname = models.CharField(max_length=50)
    phone = models.CharField(blank=True, max_length=11)
    qq = models.CharField(blank=True, max_length=20)
    weixin = models.CharField(blank=True, max_length=50)
    openid = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.ImageField(blank=True, null=True)
    gender = models.BooleanField(default=0)
    major = models.CharField(blank=True, max_length=100, null=True)

    def __str__(self):
        return self.nickname or self.phone
