#!/bin/bash

# enter frontend directory
cd lpm_frontend

# start frontend service
echo "Starting frontend service on port ${LOCAL_FRONTEND_PORT}..."
npm run dev
