FROM python:3.10-slim

# ========== 安裝系統工具 ==========
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    && rm -rf /var/lib/apt/lists/*

# ========== 安裝 Google Chrome ==========
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# ========== 安裝 ChromeDriver（自動對應版本）==========
RUN CHROME_VERSION=$(google-chrome --version | sed 's/Google Chrome //') \
    && CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" \
        | python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") \
    && wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver

# ========== 安裝 Python 套件 ==========
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ========== 複製程式 ==========
COPY app.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# ========== 預設執行 entrypoint.sh ==========
ENTRYPOINT ["./entrypoint.sh"]
