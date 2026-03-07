import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { PipelineController } from './pipeline.controller';
import { PipelineService } from './pipeline.service';

@Module({
  imports: [HttpModule],
  controllers: [PipelineController],
  providers: [PipelineService],
})
export class PipelineModule {}
