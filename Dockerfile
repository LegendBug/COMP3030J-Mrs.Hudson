# 使用官方 Python 镜像作为基础镜像
FROM python:3.11

# 设置工作目录
WORKDIR /app

# 将本地代码复制到容器中
COPY . /app

# 安装 pip 依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


RUN python manage.py collectstatic --noinput

# 设置 entrypoint
ENTRYPOINT ["/app/wait-for-it.sh", "db:3306", "--"]