import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { PipelineModule } from './pipeline/pipeline.module';

@Module({
  imports: [
    HttpModule,
    PipelineModule,
  ],
})
export class AppModule {}
