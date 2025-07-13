/**
 * API client for strategy management system.
 */
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  StrategyDefinition,
  StrategyListItem,
  StrategyVersion,
  CreateStrategyRequest,
  UpdateStrategyRequest,
  SimulationRequest,
  SimulationResult,
  ApiResponse,
  StrategyLifecycle,
  ApplicationError
} from '../types/strategy';
import { handleApiError } from './errorHandler';
import { showApplicationError } from './toastService';

class ApiClient {
  private client: AxiosInstance;
  private retryAttempts: Map<string, number> = new Map();

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for adding request metadata
    this.client.interceptors.request.use(
      (config) => {
        // Add request timestamp for timeout tracking
        (config as any).metadata = { startTime: Date.now() };
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for global error handling
    this.client.interceptors.response.use(
      (response) => {
        // Clear retry attempts on success
        const requestKey = this.getRequestKey(response.config);
        this.retryAttempts.delete(requestKey);
        return response;
      },
      async (error: AxiosError) => {
        const applicationError = handleApiError(error, 'API Request');
        
        // Handle retryable errors
        if (this.shouldRetry(error, applicationError)) {
          const retryResult = await this.handleRetry(error);
          if (retryResult) {
            return retryResult;
          }
        }

        // Show toast notification for non-retried errors
        this.showErrorToast(applicationError, error);
        
        return Promise.reject(applicationError);
      }
    );
  }

  private shouldRetry(axiosError: AxiosError, appError: ApplicationError): boolean {
    const requestKey = this.getRequestKey(axiosError.config);
    const attempts = this.retryAttempts.get(requestKey) || 0;
    const maxRetries = 2;
    
    // Don't retry if we've exceeded max attempts
    if (attempts >= maxRetries) {
      return false;
    }
    
    // Only retry specific error types
    return appError.type === 'network' || 
           (appError.type === 'server' && appError.status >= 500) ||
           (appError.type === 'client' && appError.status === 429);
  }

  private async handleRetry(error: AxiosError): Promise<AxiosResponse | null> {
    const requestKey = this.getRequestKey(error.config);
    const attempts = this.retryAttempts.get(requestKey) || 0;
    
    this.retryAttempts.set(requestKey, attempts + 1);
    
    // Exponential backoff: 1s, 2s, 4s
    const delay = Math.pow(2, attempts) * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
    
    try {
      return await this.client.request(error.config!);
    } catch (retryError) {
      // If retry fails, continue with normal error handling
      return null;
    }
  }

  private getRequestKey(config: any): string {
    return `${config?.method?.toUpperCase()}_${config?.url}`;
  }

  private showErrorToast(error: ApplicationError, axiosError: AxiosError): void {
    // Don't show toast for certain scenarios
    if (this.shouldSuppressToast(error, axiosError)) {
      return;
    }
    
    // Create retry function for retryable errors
    const retryAction = this.shouldRetry(axiosError, error) 
      ? () => this.client.request(axiosError.config!)
      : undefined;
    
    showApplicationError(error, retryAction);
  }

  private shouldSuppressToast(error: ApplicationError, axiosError: AxiosError): boolean {
    // Suppress toasts for validation endpoints (they handle their own error display)
    if (axiosError.config?.url?.includes('/validate')) {
      return true;
    }
    
    // Suppress toasts for 404s on optional resource fetches
    if (error.type === 'client' && error.status === 404) {
      return true;
    }
    
    return false;
  }

  // Strategy CRUD operations
  async createStrategy(request: CreateStrategyRequest): Promise<StrategyListItem> {
    const response: AxiosResponse<StrategyListItem> = await this.client.post(
      '/api/v1/strategies/',
      request
    );
    return response.data;
  }

  async getStrategies(params?: {
    process_step?: string;
    tool_type?: string;
    lifecycle_state?: string;
  }): Promise<StrategyListItem[]> {
    const response: AxiosResponse<StrategyListItem[]> = await this.client.get(
      '/api/v1/strategies/',
      { params }
    );
    return response.data;
  }

  async getStrategy(id: string, version?: string): Promise<StrategyDefinition> {
    const response: AxiosResponse<StrategyDefinition> = await this.client.get(
      `/api/v1/strategies/${id}`,
      { params: { version } }
    );
    return response.data;
  }

  async updateStrategy(id: string, request: UpdateStrategyRequest): Promise<StrategyListItem> {
    const response: AxiosResponse<StrategyListItem> = await this.client.put(
      `/api/v1/strategies/${id}`,
      request
    );
    return response.data;
  }

  async cloneStrategy(id: string, newName: string, author: string): Promise<StrategyListItem> {
    const response: AxiosResponse<StrategyListItem> = await this.client.post(
      `/api/v1/strategies/${id}/clone`,
      null,
      { params: { new_name: newName, author } }
    );
    return response.data;
  }

  async promoteStrategy(id: string, user: string): Promise<void> {
    await this.client.post(`/api/v1/strategies/${id}/promote`, null, {
      params: { user }
    });
  }

  async deleteStrategy(id: string): Promise<void> {
    await this.client.delete(`/api/v1/strategies/${id}`);
  }

  async getStrategyVersions(id: string): Promise<StrategyVersion[]> {
    const response: AxiosResponse<StrategyVersion[]> = await this.client.get(
      `/api/v1/strategies/${id}/versions`
    );
    return response.data;
  }

  // Simulation operations
  async simulateStrategy(request: SimulationRequest): Promise<SimulationResult> {
    const response: AxiosResponse<SimulationResult> = await this.client.post(
      `/api/v1/strategies/${request.strategy_id}/simulate`,
      request
    );
    return response.data;
  }

  // Utility methods
  async validateStrategy(definition: Partial<StrategyDefinition>): Promise<{
    valid: boolean;
    errors: string[];
  }> {
    try {
      const response = await this.client.post('/api/v1/strategies/validate', definition);
      return response.data;
    } catch (error) {
      return {
        valid: false,
        errors: ['Validation request failed']
      };
    }
  }

  async getAvailableRuleTypes(): Promise<string[]> {
    const response = await this.client.get('/api/v1/strategies/rule-types');
    return response.data;
  }

  async getAvailableVendors(): Promise<string[]> {
    const response = await this.client.get('/api/v1/strategies/vendors');
    return response.data;
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Export individual API functions for easier use in components
export const strategyApi = {
  create: (request: CreateStrategyRequest) => apiClient.createStrategy(request),
  list: (filters?: {process_step?: string; tool_type?: string; lifecycle_state?: string}) => 
    apiClient.getStrategies(filters),
  get: (id: string, version?: string) => apiClient.getStrategy(id, version),
  update: (id: string, request: UpdateStrategyRequest) => apiClient.updateStrategy(id, request),
  clone: (id: string, newName: string, author: string) => apiClient.cloneStrategy(id, newName, author),
  promote: (id: string, user: string) => apiClient.promoteStrategy(id, user),
  delete: (id: string) => apiClient.deleteStrategy(id),
  getVersions: (id: string) => apiClient.getStrategyVersions(id),
  simulate: (request: SimulationRequest) => apiClient.simulateStrategy(request),
  validate: (definition: Partial<StrategyDefinition>) => apiClient.validateStrategy(definition),
  getRuleTypes: () => apiClient.getAvailableRuleTypes(),
  getVendors: () => apiClient.getAvailableVendors(),
};

export default apiClient;