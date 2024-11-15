FROM node:14

# Install dependencies
WORKDIR /app
COPY package.json /app/
COPY package-lock.json /app/
RUN npm install

# Copy project files and build the app
COPY . /app
RUN npm run build

# Install `serve` globally to serve the built app
RUN npm install -g serve

# Expose the correct port for the production build
EXPOSE 3000

# Start the app using `serve` on port 3030
CMD ["npm", "start"]