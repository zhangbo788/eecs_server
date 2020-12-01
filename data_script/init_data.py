from djadmin.eecs.models import *
import sys

try:
    DjangoUser.objects.create_superuser(
        username="eecs",
        password="eecs1234"
    )
except:
    sys.stderr.write("创建超级用户失败")

try:
    Role.objects.create(
        name="专业负责人",
    )
    Role.objects.create(
        name="课程负责人",
    )
    Role.objects.create(
        name="专业班负责人",
    )
except:
    sys.stderr.write("创建角色失败")
