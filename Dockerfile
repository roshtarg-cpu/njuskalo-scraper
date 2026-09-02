FROM apify/actor-python:3.11

# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-xcb1 \
    libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libxcursor1 libxi6 libxtst6 libgbm1 libpango-1.0-0 \
    libcairo2 libnss3 libxss1 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 && \
    rm -rf /var/lib/apt/lists/*

ENV MOZ_DISABLE_CONTENT_SANDBOX=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only for smaller image)
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy source code
COPY . ./

# Run the scraper
CMD ["python", "-m", "src"]
