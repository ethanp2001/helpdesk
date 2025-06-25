#!/bin/bash

mkdir -p /data
chmod 777 /data

# Generate a random secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create the .env file
cat <<EOF > /app/.env
SECRET_KEY=$SECRET_KEY
DATABASE_URL=${DATABASE_URL}
EOF

# Run the Flask app
exec "$@"