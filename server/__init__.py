import os
import django

# 激活Django的环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djadmin.djadmin.settings')
django.setup()
