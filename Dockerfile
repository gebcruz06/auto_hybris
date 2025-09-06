# Use the official Apache Airflow image as the base.
FROM apache/airflow:2.9.3-python3.12

# Switch to the root user to install system-level packages.
USER root

# Install Firefox and Geckodriver dependencies
RUN apt-get update -y && \
    apt-get install -y \
    wget \
    gnupg \
    curl \
    bzip2 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libpci3 \
    libasound2 \
    libx11-xcb1 \
    libnss3 \
    libxrandr2 \
    libxss1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    fonts-liberation \
    xz-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox ESR (stable for Debian-based distros)
RUN apt-get update -y && \
    apt-get install -y firefox-esr && \
    rm -rf /var/lib/apt/lists/*

# Install latest Geckodriver
RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep "tag_name" | cut -d '"' -f 4) && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar -xzf "geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" -C /usr/local/bin && \
    rm "geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz"

# Correctly switch to the non-root 'airflow' user.
USER airflow

# Copy your Python requirements file and install them.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .

# Expose the Airflow port (optional, but good practice).
EXPOSE 8080

# This is the default command that the Airflow image runs.
CMD ["airflow", "webserver"]
