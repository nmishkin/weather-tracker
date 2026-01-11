#!/bin/bash

# Florida Weather Tracker Remote Deployment Script
# Usage: ./deploy.sh <hostname>

set -e

if [ -z "$1" ]; then
    echo "Error: Hostname is required."
    echo "Usage: ./deploy.sh <hostname>"
    exit 1
fi

HOSTNAME=$1
REMOTE_DIR="/var/www/weather-tracker"
SSH_USER="mishkin" # Assuming same user, adjust if needed

echo "🚀 Starting deployment to ${HOSTNAME}..."

# 1. Build Frontend
echo "📦 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Prepare Remote Directory
echo "📁 Preparing remote directory..."
ssh ${HOSTNAME} "sudo mkdir -p ${REMOTE_DIR}/dist/weather-tracker && sudo chown -R \$USER:\$USER ${REMOTE_DIR}"

# 3. Transfer Files
echo "📨 Transferring files..."
# Sync frontend dist contents into the subpath directory on remote
rsync -avz --delete frontend/dist/ ${HOSTNAME}:${REMOTE_DIR}/dist/weather-tracker/
# Sync other components
rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '__pycache__' \
    backend \
    deployment \
    requirements.txt \
    ${HOSTNAME}:${REMOTE_DIR}/

# 4. Setup Backend on Remote
echo "⚙️ Setting up backend on remote..."
ssh ${HOSTNAME} << EOF
    cd ${REMOTE_DIR}
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt fastapi uvicorn requests
EOF

# 5. Install Systemd and Nginx Configs
echo "📋 Installing system configurations..."

ssh ${HOSTNAME} << EOF
    sudo cp ${REMOTE_DIR}/deployment/weather-tracker.service /etc/systemd/system/
    sudo cp ${REMOTE_DIR}/deployment/nginx.conf /etc/nginx/conf.d/weather-tracker.conf
    
    # Disable the default site if it exists to prevent 404 conflicts
    if [ -f "/etc/nginx/sites-enabled/default" ]; then
        echo "🚫 Disabling default Nginx site..."
        sudo rm /etc/nginx/sites-enabled/default
    fi

    echo "🔒 Fixing permissions..."
    sudo chown -R www-data:www-data ${REMOTE_DIR}
    sudo chmod -R 755 ${REMOTE_DIR}

    echo "🔄 Reloading services..."
    sudo systemctl daemon-reload
    sudo systemctl enable weather-tracker.service
    sudo systemctl restart weather-tracker.service
    sudo nginx -t && sudo systemctl reload nginx
EOF

echo "✅ Deployment complete!"
echo "📍 App available at: http://${HOSTNAME}/weather-tracker"
