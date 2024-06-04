import multiprocessing

# 绑定的 IP 和端口
bind = '127.0.0.1:5000'

# 工作模式，如同步工作模式或异步工作模式（如 gevent）
worker_class = 'sync'  # 可以改为 'gevent' 以提高并发性能

# 启动的工作进程数量,根据服务器的 CPU 核心数来调整
workers = multiprocessing.cpu_count() * 2 + 1

# 最大请求量，超过此数量后将重启一个工作进程
max_requests = 1000
max_requests_jitter = 50  # 为 max_requests 添加抖动，防止所有工作进程同时重启

# 超时配置（秒）
timeout = 30  # 超过此时间后 Gunicorn 会杀掉工作进程

# 日志文件配置
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# 安全相关配置
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
