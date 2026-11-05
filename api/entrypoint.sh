#!/bin/sh

: "${PORT:=80}"

# Azure App Service establece WEBSITES_ENABLE_APP_SERVICE_STORAGE automaticamente.
# Para on-premise, puedes forzar SSH con AZURE_ENV=true.
if [ "${WEBSITES_ENABLE_APP_SERVICE_STORAGE}" = "true" ] || [ "${AZURE_ENV}" = "true" ]; then
    /usr/sbin/sshd
fi

exec uvicorn api.__main__:app --host 0.0.0.0 --port "$PORT"
