const request = require('supertest');
const app = require('./index');

describe('GET /', () => {
  it('should return welcome message', async () => {
    const response = await request(app).get('/');
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('message');
    expect(response.body).toHaveProperty('version');
    expect(response.body).toHaveProperty('timestamp');
    expect(response.body.message).toContain('Hello');
  });
});

describe('GET /health', () => {
  it('should return health status', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status');
    expect(response.body).toHaveProperty('uptime');
    expect(response.body).toHaveProperty('timestamp');
    expect(response.body.status).toBe('healthy');
  });
});

describe('POST /echo', () => {
  it('should echo back the request body', async () => {
    const testData = { hello: 'world', number: 42 };
    const response = await request(app).post('/echo').send(testData);
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('received');
    expect(response.body).toHaveProperty('echoed');
    expect(response.body).toHaveProperty('timestamp');
    expect(response.body.echoed).toBe(true);
    expect(response.body.received).toEqual(testData);
  });
});

describe('404 handler', () => {
  it('should return 404 for unknown routes', async () => {
    const response = await request(app).get('/nonexistent');
    expect(response.status).toBe(404);
    expect(response.body).toHaveProperty('error');
    expect(response.body).toHaveProperty('path');
  });
});
