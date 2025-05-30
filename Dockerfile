FROM python:3.12-slim-bookworm

RUN apt update -y && apt install librdkit1 -y
RUN pip install uv supervisor --no-cache

WORKDIR /app
COPY . /app
RUN mv supervisord.conf /etc/supervisord.conf

RUN uv sync --no-cache && \
    pip cache purge && \
    uv cache clean

# Streamlit default port
EXPOSE 8501

ENTRYPOINT ["supervisord"]
