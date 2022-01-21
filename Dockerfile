FROM python:3.9-slim
ARG app_name
ARG app_version
WORKDIR /usr/src/app
COPY . .
RUN printf '{"package_name":"%s","package_version":"%s"}' "$app_name" "$app_version" > "package_info.json" && \
    pip install -r requirements.txt
