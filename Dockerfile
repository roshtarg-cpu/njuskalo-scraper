FROM apify/actor-python:3.11

# Install system dependencies for browser automation
RUN apt-get update && apt-get install -y \
    libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-xcb1 \
    libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libxcursor1 libxi6 libxtst6 \
    && rm -rf /var/lib/apt/lists/*

ENV MOZ_DISABLE_CONTENT_SANDBOX=1

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Run the scraper
CMD ["python", "-m", "src"]
