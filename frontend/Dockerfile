# Step 1: Build the application
FROM node:18 AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Next.js app
RUN npm run build

# Step 2: Serve the application
FROM node:18 AS runner

# Set the working directory
WORKDIR /app

# Copy the built app from the builder stage
COPY --from=builder /app .

# Install serve to serve the application
RUN npm install -g serve

# Expose the desired port
EXPOSE 3000

# Command to run the application
CMD ["serve", "-s", "out", "-l", "3000"]
