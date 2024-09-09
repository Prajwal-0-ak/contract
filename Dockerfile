# Use an official Python runtime as a parent image
FROM python:3.9-slim as backend

# Set the working directory in the container
WORKDIR /app/backend

# Copy the backend requirements file into the container
COPY backend/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY backend/ .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the backend when the container launches
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Use an official Node runtime as a parent image
FROM node:14 as frontend

# Set the working directory in the container
WORKDIR /app/frontend

# Copy the frontend package.json and package-lock.json
COPY frontend/package*.json .

# Install any needed packages specified in package.json
RUN npm install

# Copy the frontend code into the container
COPY frontend/ .

# Build the Next.js app
RUN npm run build

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the frontend when the container launches
CMD ["npm", "start"]

# Final stage
FROM nginx:alpine

# Copy the built frontend from the frontend stage
COPY --from=frontend /app/frontend/.next /usr/share/nginx/html

# Copy the backend from the backend stage
COPY --from=backend /app/backend /app/backend

# Copy a custom nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]