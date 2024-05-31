#!/bin/bash
set -e

# Set up environment variables
cd /opt/via/deployment/docker_compose
touch .env
touch .env.nginx

cat <<EOT > .env
WEB_DOMAIN=ec2-03-135-194-173.us-east-2.compute.amazonaws.com
VALID_EMAIL_DOMAINS=vicivisionamerica.com
AUTH_TYPE=basic
# Uncomment the following lines if you need email verification
# REQUIRE_EMAIL_VERIFICATION=true
# SMTP_USER=<GMAIL_ACCOUNT_EMAIL_YOU_WANT_TO_SEND_VERIFICATION_EMAILS_WITH>
# SMTP_PASS=<GMAIL_ACCOUNT_PW_YOU_WANT_TO_SEND_VERIFICATION_EMAILS_WITH>
# Uncomment the following lines if using Google OAuth
# AUTH_TYPE=google_oauth
# GOOGLE_OAUTH_CLIENT_ID=
# GOOGLE_OAUTH_CLIENT_SECRET=
# SECRET=<RANDOMLY_GENERATED_UUID>
GEN_AI_MODEL_PROVIDER=openai
GEN_AI_MODEL_VERSION=gpt-4
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
EOT

cat <<EOT > .env.nginx
DOMAIN=ec2-3-135-194-173.us-east-2.compute.amazonaws.com
EOT

