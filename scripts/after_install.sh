#!/bin/bash
set -e

# Set up environment variables
cd /opt/via/deployment/docker_compose
touch .env
touch .env.nginx

cat <<EOT > .env
WEB_DOMAIN=https://via.vicivisionamerica.com
VALID_EMAIL_DOMAINS=vicivisionamerica.com
AUTH_TYPE=basic
# Uncomment the following lines if you need email verification
# REQUIRE_EMAIL_VERIFICATION=true
# SMTP_USER=<GMAIL_ACCOUNT_EMAIL_YOU_WANT_TO_SEND_VERIFICATION_EMAILS_WITH>
# SMTP_PASS=<GMAIL_ACCOUNT_PW_YOU_WANT_TO_SEND_VERIFICATION_EMAILS_WITH>
# Uncomment the following lines if using Google OAuth
# AUTH_TYPE=google_oauth
# GOOGLE_OAUTH_CLIENT_ID=809005354337-61c4mse4l4r75m9u6ukeh7rogm008sr0.apps.googleusercontent.com
# GOOGLE_OAUTH_CLIENT_SECRET=
# SECRET=<RANDOMLY_GENERATED_UUID>
GEN_AI_MODEL_PROVIDER=openai
GEN_AI_MODEL_VERSION=gpt-4
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
EOT

cat <<EOT > .env.nginx
DOMAIN=via.vicivisionamerica.com
EOT

