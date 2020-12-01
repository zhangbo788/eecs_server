from django.db import models
from django.contrib.auth.models import User as DjangoUser


# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=32, verbose_name="角色名")

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "角色表"
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class UserRole(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")
    user = models.ForeignKey(DjangoUser, on_delete=models.CASCADE, verbose_name="用户")

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "用户-角色表"
        verbose_name = verbose_name_plural
        unique_together = ('role', 'user',)


class Major(models.Model):
    manager = models.ForeignKey(DjangoUser, on_delete=models.CASCADE, verbose_name="专业负责人")
    code = models.CharField(max_length=32, unique=True, verbose_name="专业代码")
    name = models.CharField(max_length=32, unique=True, verbose_name="专业名称")
    create_time = models.DateTimeField(auto_now=True, verbose_name="创建时间")

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "专业表"
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name


class Point1(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, verbose_name="专业")
    index = models.IntegerField(unique=True, verbose_name="编号")
    content = models.TextField(verbose_name="内容")
    create_time = models.DateTimeField(auto_now=True, verbose_name="创建时间")

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "毕业要求表"
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.major.name + "-指标点" + str(self.index)


class Point2(models.Model):
    point1 = models.ForeignKey(Point1, verbose_name="所属毕业要求", on_delete=models.CASCADE)
    index = models.IntegerField(unique=True, verbose_name="编号")
    content = models.TextField(verbose_name="内容")
    create_time = models.DateTimeField(auto_now=True, verbose_name="创建时间")

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "指标点分解表"
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.point1.major.name + "-指标点%d.%d" % (self.point1.index, self.index)


class Major1(models.Model):
    manager = models.ForeignKey(DjangoUser, on_delete=models.CASCADE, verbose_name="专业负责人")
    code = models.CharField(max_length=32, unique=True, verbose_name="专业代码")
    name = models.CharField(max_length=32, unique=True, verbose_name="专业名称")
    create_time = models.DateTimeField(auto_now=True, verbose_name="创建时间")

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "专业表"
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.name
