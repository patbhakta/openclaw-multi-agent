# Example Node.js Application in Docker

A simple Node.js/Express application demonstrating Docker development workflow.

## Features

- RESTful API with 3 endpoints
- Health check endpoint
- Echo endpoint for testing
- Unit tests with Jest
- Multi-stage Docker setup
- docker-compose configuration

## Running Locally

```bash
npm install
npm start
```

## Running with Docker

### Build the image

```bash
docker build -t example-nodejs-app .
```

### Run the container

```bash
docker run -p 3000:3000 example-nodejs-app
```

### Using Docker Compose

```bash
# Start the application
docker-compose up -d app

# Run tests
docker-compose run --rm test

# View logs
docker-compose logs -f app

# Stop everything
docker-compose down
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /echo` - Echo back request body

## Testing

```bash
# Run tests locally
npm test

# Run tests in Docker
docker-compose run --rm test
```

## Docker Best Practices Demonstrated

1. **Multi-stage builds** - Separate build and runtime
2. **Alpine images** - Smaller image size
3. **Non-root user** - Security best practice
4. **.dockerignore** - Exclude unnecessary files
5. **Health checks** - Container health monitoring
6. **Proper caching** - Copy package files first
