#!/bin/bash
set -e
# Set PYTHONPATH
#export PYTHONPATHY=/opt/via/backend

# Set up environment variables
#cd /opt/via/deployment/docker_compose
#touch .env
#touch .env.nginx

#cat <<EOT > .env
#WEB_DOMAIN=https://via.vicivisionamerica.com
#VALID_EMAIL_DOMAINS=vicivisionamerica.com
#AUTH_TYPE=basic
# Uncomment the following lines if you need email verification
# REQUIRE_EMAIL_VERIFICATION=true
# SMTP_USER=<GMAIL_ACCOUNT_EMAIL_YOU_WANT_TO_SEND_VERIFICATION_EMAILS_WITH>
# SMTP_PASS=<GMAIL_ACCOUNT_PW_YOU_WANT_TO_SEND_VERIFICATION_EMAILS_WITH>
# Uncomment the following lines if using Google OAuth
# AUTH_TYPE=google_oauth
# GOOGLE_OAUTH_CLIENT_ID=809005354337-61c4mse4l4r75m9u6ukeh7rogm008sr0.apps.googleusercontent.com
# GOOGLE_OAUTH_CLIENT_SECRET=
# SECRET=<RANDOMLY_GENERATED_UUID>
#GEN_AI_MODEL_PROVIDER=openai
#GEN_AI_MODEL_VERSION=gpt-4
#POSTGRES_USER=postgres
#POSTGRES_PASSWORD=password
#EOT

#cat <<EOT > .env.nginx
#DOMAIN=via.vicivisionamerica.com
#EOT

# Load the saved state
#python3 /opt/via/backend/scripts/save_load_state.py --load --postgres_container_name relational_db --checkpoint_dir /opt/via/checkpoints

#!/bin/bash
set -e

# Set PYTHONPATH
#export PYTHONPATH=/opt/via/backend

# Log the start of the script
echo "Starting after_install.sh script" | tee -a /tmp/after_install.log

# Set up environment variables
cd /opt/via/deployment/docker_compose
touch .env
touch .env.nginx

cat <<EOT > .env
WEB_DOMAIN=https://via.vicivisionamerica.com
VALID_EMAIL_DOMAINS=
AUTH_TYPE=basic
# Uncomment the following lines if you need email verification
REQUIRE_EMAIL_VERIFICATION=false
# SMTP_USER=forms@vicivisionamerica.com
# SMTP_PASS=$SMTP_PASS
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

# Log environment variables
env | tee -a /tmp/after_install.log

# Load the saved state
#echo "Loading saved state" | tee -a /tmp/after_install.log
#python3 /opt/via/backend/scripts/save_load_state.py --load --postgres_container_name relational_db --checkpoint_dir /opt/via/checkpoints 2>&1 | tee -a /tmp/after_install.log

# Make scripts executable
chmod +x /opt/via/scripts/backup_data.sh /opt/via/scripts/restore_data.sh

# Set up cron job for nightly backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/via/scripts/backup_data.sh") | crontab -

# Log the end of the script
echo "Completed after_install.sh script" | tee -a /tmp/after_install.log
