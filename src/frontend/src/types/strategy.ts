/**
 * Frontend type definitions for strategy management system.
 */

export enum StrategyType {
  FIXED_POINT = 'fixed_point',
  CENTER_EDGE = 'center_edge', 
  UNIFORM_GRID = 'uniform_grid',
  HOTSPOT_PRIORITY = 'hotspot_priority',
  ADAPTIVE = 'adaptive',
  CUSTOM = 'custom'
}

export enum StrategyLifecycle {
  DRAFT = 'draft',
  REVIEW = 'review',
  APPROVED = 'approved',
  ACTIVE = 'active',
  DEPRECATED = 'deprecated'
}

export interface Die {
  x: number;
  y: number;
  available: boolean;
}

export interface WaferMap {
  dies: Die[];
  metadata?: {
    wafer_size?: string;
    product_type?: string;
    lot_id?: string;
  };
}

export interface ConditionalLogic {
  wafer_size?: string;
  product_type?: string;
  process_layer?: string;
  defect_density_threshold?: number;
  custom_conditions?: Record<string, any>;
}

export interface TransformationConfig {
  rotation_angle: number;
  scale_factor: number;
  offset_x: number;
  offset_y: number;
  flip_x: boolean;
  flip_y: boolean;
  custom_transforms?: Array<Record<string, any>>;
}

export interface RuleConfig {
  rule_type: string;
  parameters: Record<string, any>;
  weight: number;
  conditions?: ConditionalLogic;
  enabled: boolean;
}

export interface StrategyDefinition {
  id: string;
  name: string;
  description: string;
  strategy_type: StrategyType;
  process_step: string;
  tool_type: string;
  rules: RuleConfig[];
  conditions?: ConditionalLogic;
  transformations?: TransformationConfig;
  target_vendor?: string;
  vendor_specific_params?: Record<string, any>;
  version: string;
  author: string;
  created_at: string;
  modified_at: string;
  lifecycle_state: StrategyLifecycle;
  schema_version: string;
}

export interface StrategyListItem {
  id: string;
  name: string;
  description: string;
  strategy_type: string;
  process_step: string;
  tool_type: string;
  version: string;
  author: string;
  created_at: string;
  modified_at: string;
  lifecycle_state: string;
  rule_count: number;
}

export interface StrategyVersion {
  version: string;
  created_at: string;
  created_by: string;
  changelog: string;
  is_active: boolean;
}

export interface SimulationRequest {
  strategy_id: string;
  wafer_map_data: Record<string, any>;
  process_parameters?: Record<string, any>;
  tool_constraints?: Record<string, any>;
}

export interface SimulationResult {
  selected_points: Array<{x: number, y: number, available: boolean}>;
  coverage_stats: {
    total_dies: number;
    available_dies: number;
    selected_count: number;
    coverage_percentage: number;
    distribution?: Record<string, any>;
  };
  performance_metrics: Record<string, any>;
  warnings: string[];
}

export interface CreateStrategyRequest {
  name: string;
  description?: string;
  process_step: string;
  tool_type: string;
  strategy_type: StrategyType;
  author: string;
}

export interface UpdateStrategyRequest {
  name?: string;
  description?: string;
  rules?: RuleConfig[];
  conditions?: ConditionalLogic;
  transformations?: TransformationConfig;
}

// Form-specific types
export interface StrategyFormData {
  // Step 1: Basic Info
  name: string;
  description: string;
  process_step: string;
  tool_type: string;
  strategy_type: StrategyType;
  author: string;
  
  // Step 2: Rules Configuration
  rules: RuleConfig[];
  
  // Step 3: Conditions
  conditions?: ConditionalLogic;
  
  // Step 4: Transformations
  transformations?: TransformationConfig;
  
  // Step 5: Vendor Settings
  target_vendor?: string;
  vendor_specific_params?: Record<string, any>;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// UI State types
export interface StrategyBuilderState {
  current_step: number;
  form_data: Partial<StrategyFormData>;
  validation_errors: Record<string, string[]>;
  is_saving: boolean;
  preview_data?: SimulationResult;
}

export interface WaferMapViewState {
  zoom: number;
  pan: {x: number, y: number};
  selected_dies: Die[];
  highlighted_dies: Die[];
  show_grid: boolean;
  show_coordinates: boolean;
}

// Error types
export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, any>;
}

// Enhanced error types for comprehensive error handling
export type ErrorSeverity = 'info' | 'warning' | 'error' | 'critical';

export interface BackendValidationError {
  field: string;
  code: string;
  message: string;
  value?: any;
}

export interface NetworkError {
  type: 'network';
  message: string;
  isTimeout: boolean;
  isOffline: boolean;
}

export interface ServerError {
  type: 'server';
  status: number;
  message: string;
  details?: Record<string, any>;
  requestId?: string;
}

export interface ClientError {
  type: 'client';
  status: number;
  message: string;
  validationErrors?: BackendValidationError[];
}

export interface ErrorResponse {
  error: {
    message: string;
    code?: string;
    details?: Record<string, any>;
    validation_errors?: BackendValidationError[];
  };
  request_id?: string;
  timestamp?: string;
}

export type ApplicationError = NetworkError | ServerError | ClientError;

export interface ErrorHandlerConfig {
  showToast: boolean;
  logError: boolean;
  severity: ErrorSeverity;
  retryable: boolean;
}