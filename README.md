# EECS

## 1.部署步骤

### 1.1 安装所需环境
```shell script
pip install -r requirements.txt
```

### 1.2 创建数据库表
```shell script
python django_manage.py makemigrations
python django_manage.py migrate
```
### 1.2.1 （可选）初始化数据
```shell script
python -m data_script.init_data
```
### 1.3 收集静态文件
```shell script
python django_manage.py collectstatic
```

### 1.4 启动服务
```shell script
uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```

### 1.5 访问Django admin
账号为eecs，密码为eecs1234
```
127.0.0.1/django/admin/
```

### 1.5 访问后端接口文档
```
127.0.0.1/docs
```