FROM joyzoursky/python-chromedriver:3.6-selenium
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
ADD ./docker/account/requirements.txt .
RUN pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple