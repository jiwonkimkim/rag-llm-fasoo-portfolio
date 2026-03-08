import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { json, urlencoded, Request, Response, NextFunction } from 'express';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const apiAuthKey = process.env.API_AUTH_KEY;
  const requireApiAuth = (process.env.REQUIRE_API_AUTH ?? 'true').toLowerCase();
  const isApiAuthRequired = ['1', 'true', 'yes', 'on'].includes(requireApiAuth);
  const corsOrigins = (process.env.CORS_ALLOW_ORIGINS || 'http://localhost:5173,http://localhost:3000')
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);
  const allowAllOrigins = corsOrigins.length === 1 && corsOrigins[0] === '*';

  if (isApiAuthRequired && !apiAuthKey) {
    throw new Error(
      'API auth is required but API_AUTH_KEY is missing. ' +
      'Set API_AUTH_KEY or disable REQUIRE_API_AUTH explicitly.'
    );
  }

  // Increase body size limit for large text and embeddings data
  app.use(json({ limit: '100mb' }));
  app.use(urlencoded({ extended: true, limit: '100mb' }));

  // Optional API key auth for all API routes except health checks.
  app.use('/api', (req: Request, res: Response, next: NextFunction) => {
    if (!isApiAuthRequired || req.path === '/health') {
      return next();
    }
    const incomingKey = req.header('x-api-key');
    if (incomingKey !== apiAuthKey) {
      return res.status(401).json({ detail: 'Unauthorized' });
    }
    return next();
  });

  // Enable CORS for React frontend
  app.enableCors({
    origin: corsOrigins,
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    credentials: !allowAllOrigins,
  });

  await app.listen(3001);
  console.log('🚀 NestJS server running on http://localhost:3001');
}
bootstrap();
