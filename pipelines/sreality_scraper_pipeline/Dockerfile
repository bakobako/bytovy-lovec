FROM prefecthq/prefect:3-latest

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

ENV DISPLAY=:99

RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    python3-dev


RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    libnss3 \
    libasound2 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libxi6 \
    libgtk-3-0 \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# Install Chromedriver
RUN CHROMEDRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip

COPY pipelines pipelines
COPY shared shared
COPY requirements.txt requirements.txt
COPY setup.py setup.py

ENV PREFECT_HOME="/opt/prefect/.prefect"
