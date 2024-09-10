FROM node:20 as frontend

# set working directory
WORKDIR /work_dir

# install frontend dependencies
WORKDIR /work_dir/frontend
COPY frontend/package*.json .
RUN npm install

COPY frontend/ .

RUN npm run build

# expose the necessary ports
EXPOSE 3000

# run the app
CMD ["sh", "-c", "npm start"]