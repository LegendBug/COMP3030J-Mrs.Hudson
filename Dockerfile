# 使用官方 Python 镜像作为基础镜像
FROM python:3.11

# 设置工作目录
WORKDIR /app

# 将本地代码复制到容器中
COPY . /app

# 安装 pip 依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 收集静态文件（如果你的项目中有）
RUN python manage.py collectstatic --noinput

# 运行 Gunicorn 服务器
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "COMP3030J_Hudson.wsgi:application"]
