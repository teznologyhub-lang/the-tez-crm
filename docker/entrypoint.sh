#!/bin/bash
set -e

# Wait for MariaDB & Redis to be ready
echo "Waiting for MariaDB ($DB_HOST:$DB_PORT)..."
while ! nc -z $DB_HOST $DB_PORT; do sleep 2; done

echo "Waiting for Redis ($REDIS_HOST:$REDIS_PORT)..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do sleep 2; done

cd /home/frappe/frappe-bench

# Configure Redis hosts
bench set-redis-cache-host "redis://${REDIS_HOST}:${REDIS_PORT}"
bench set-redis-queue-host "redis://${REDIS_HOST}:${REDIS_PORT}"
bench set-redis-socketio-host "redis://${REDIS_HOST}:${REDIS_PORT}"

# Setup site if it doesn't exist
SITE_NAME=${SITE_NAME:-"tezcrm.onrender.com"}

if [ ! -d "sites/$SITE_NAME" ]; then
    echo "Creating new site: $SITE_NAME..."
    bench new-site $SITE_NAME \
        --db-host $DB_HOST \
        --db-port $DB_PORT \
        --mariadb-root-password $DB_ROOT_PASSWORD \
        --admin-password $ADMIN_PASSWORD \
        --no-mariadb-socket
    
    bench --site $SITE_NAME install-app crm
    bench use $SITE_NAME
else
    echo "Site exists, running migrations..."
    bench --site $SITE_NAME migrate
fi

# Start web process or worker depending on PROCESS_TYPE environment variable
if [ "$PROCESS_TYPE" = "worker" ]; then
    echo "Starting Background Worker & Scheduler..."
    exec bench worker
elif [ "$PROCESS_TYPE" = "schedule" ]; then
    echo "Starting Scheduler..."
    exec bench schedule
else
    echo "Starting Web Server..."
    exec bench start
fi