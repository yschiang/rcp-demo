/**
 * API client for strategy management system.
 */
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  StrategyDefinition,
  StrategyListItem,
  StrategyVersion,
  CreateStrategyRequest,
  UpdateStrategyRequest,
  SimulationRequest,
  SimulationResult,
  ApiResponse,
  StrategyLifecycle
} from '../types/strategy';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
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