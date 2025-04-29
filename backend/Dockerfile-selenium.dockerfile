# Use a slim Python image
FROM python:3.12-slim

# install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# add Google’s signing key & repo
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
    | apt-key add - \
  && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# install Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
  && rm -rf /var/lib/apt/lists/*

# check Chrome version
RUN google-chrome --version


# copy your scraper requirements & install
# Set working directory
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# by default run your scraper
CMD ["python", "-m", "app.services.selenium_scraper"]
