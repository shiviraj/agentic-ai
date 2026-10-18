export { HealthCheckController } from './healthcheck.controller';

export class HealthCheckController {
    @Get('/healthcheck')
    async healthCheck(): Promise<boolean> {
        return true;
    }
}
