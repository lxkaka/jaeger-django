# jaeger-django
This python package can be used in django project to  tracing service with jaeger. Enjoy!

## Install
`pip install jaeger-django`

## Usage
* Using middleware for inbound request
  settings.py in django
  ```python
    MIDDLEWARE = [
        'huipy.tracer.middleware.TraceMiddleware',
        # 其他中间件
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    # service name
    SERVICE_NAME = 'service name'
    # other conf
    ...
  ```
* Using **httpclient** for outbound request
   ```python
    from tracer.httpclient import HttpClient
    HttpClient(url='http://httpbin.org/get').get()
   ```

