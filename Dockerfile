# Use the official Apache Airflow image as the base.
FROM apache/airflow:2.9.3-python3.12

# Switch to the root user to install system-level packages.
USER root

# Install a comprehensive list of system dependencies required by Google Chrome.
RUN apt-get update -y && \
    apt-get install -y \
    gnupg \
    wget \
    libnss3-dev \
    libgconf-2-4 \
    libappindicator1 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxi6 \
    libsm6 \
    libice6 \
    libgstreamer-plugins-base1.0-0 \
    libgstreamer1.0-0 \
    libharfbuzz-icu0 \
    libharfbuzz0b \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpng16-16 \
    libstdc++6 \
    libxkbcommon0 \
    libxrender1 \
    libxshmfence1 \
    xz-utils \
    zlib1g \
    && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && \
    apt-get update -y && \
    apt-get install -y google-chrome-stable \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Correctly switch to the non-root 'airflow' user.
# All subsequent commands will be run as this user.
USER airflow

# Copy your Python requirements file and install them.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .

# Expose the Airflow port (optional, but good practice).
EXPOSE 8080

# This is the default command that the Airflow image runs.
CMD ["airflow", "webserver"]