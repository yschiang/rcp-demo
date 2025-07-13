/**
 * Centralized error handling service for the application.
 */
import { AxiosError } from 'axios';
import {
  ApplicationError,
  BackendValidationError,
  ClientError,
  ErrorHandlerConfig,
  ErrorResponse,
  ErrorSeverity,
  NetworkError,
  ServerError
} from '../types/strategy';

/**
 * Default error handler configuration
 */
const DEFAULT_CONFIG: ErrorHandlerConfig = {
  showToast: true,
  logError: true,
  severity: 'error',
  retryable: false
};

/**
 * Parse axios error into application error format
 */
export function parseAxiosError(error: AxiosError): ApplicationError {
  // Network/connection errors
  if (!error.response) {
    const isTimeout = error.code === 'ECONNABORTED' || error.message.includes('timeout');
    const isOffline = !navigator.onLine;
    
    return {
      type: 'network',
      message: isTimeout 
        ? 'Request timed out. Please check your connection and try again.'
        : isOffline
        ? 'You appear to be offline. Please check your internet connection.'
        : 'Network error occurred. Please try again.',
      isTimeout,
      isOffline
    } as NetworkError;
  }

  const status = error.response.status;
  const responseData = error.response.data as ErrorResponse | any;

  // Server errors (5xx)
  if (status >= 500) {
    return {
      type: 'server',
      status,
      message: responseData?.error?.message || 
               responseData?.message || 
               'Internal server error. Please try again later.',
      details: responseData?.error?.details || responseData?.details,
      requestId: responseData?.request_id
    } as ServerError;
  }

  // Client errors (4xx)
  const validationErrors = responseData?.error?.validation_errors || 
                          responseData?.validation_errors || 
                          [];

  return {
    type: 'client',
    status,
    message: responseData?.error?.message || 
             responseData?.message || 
             getDefaultClientErrorMessage(status),
    validationErrors: validationErrors.map((ve: any) => ({
      field: ve.field || ve.loc?.[ve.loc.length - 1] || 'unknown',
      code: ve.type || ve.code || 'validation_error',
      message: ve.msg || ve.message || 'Invalid value',
      value: ve.input || ve.value
    }))
  } as ClientError;
}

/**
 * Get default error message for HTTP status codes
 */
function getDefaultClientErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return 'Invalid request data. Please check your inputs and try again.';
    case 401:
      return 'You are not authorized to perform this action. Please log in.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'The requested resource was not found.';
    case 409:
      return 'A conflict occurred. The resource may already exist.';
    case 422:
      return 'The provided data is invalid. Please check your inputs.';
    case 429:
      return 'Too many requests. Please wait a moment and try again.';
    default:
      return 'An error occurred. Please try again.';
  }
}

/**
 * Map backend validation errors to form field errors
 */
export function mapValidationErrors(
  validationErrors: BackendValidationError[]
): Record<string, string[]> {
  const fieldErrors: Record<string, string[]> = {};
  
  validationErrors.forEach(error => {
    if (!fieldErrors[error.field]) {
      fieldErrors[error.field] = [];
    }
    fieldErrors[error.field].push(error.message);
  });
  
  return fieldErrors;
}

/**
 * Extract user-friendly error message from different error formats
 */
export function getErrorMessage(error: ApplicationError): string {
  return error.message;
}

/**
 * Get error severity level for UI display
 */
export function getErrorSeverity(error: ApplicationError): ErrorSeverity {
  switch (error.type) {
    case 'network':
      return error.isOffline ? 'critical' : 'error';
    case 'server':
      return error.status >= 500 ? 'critical' : 'error';
    case 'client':
      if (error.status === 401 || error.status === 403) return 'warning';
      if (error.status === 404) return 'info';
      if (error.validationErrors && error.validationErrors.length > 0) return 'warning';
      return 'error';
    default:
      return 'error';
  }
}

/**
 * Determine if an error is retryable
 */
export function isRetryableError(error: ApplicationError): boolean {
  switch (error.type) {
    case 'network':
      return error.isTimeout || !error.isOffline;
    case 'server':
      return error.status >= 500;
    case 'client':
      return error.status === 429; // Rate limited
    default:
      return false;
  }
}

/**
 * Get error handler configuration for different error types
 */
export function getErrorConfig(error: ApplicationError): ErrorHandlerConfig {
  return {
    showToast: true,
    logError: true,
    severity: getErrorSeverity(error),
    retryable: isRetryableError(error)
  };
}

/**
 * Log error to console with structured format
 */
export function logError(error: ApplicationError, context?: string): void {
  const logData = {
    type: error.type,
    message: error.message,
    context,
    timestamp: new Date().toISOString(),
    error
  };
  
  console.error('Application Error:', logData);
  
  // In production, you might want to send this to a logging service
  // Example: sendToLoggingService(logData);
}

/**
 * Main error handler function
 */
export function handleApiError(
  axiosError: AxiosError,
  context?: string,
  config?: Partial<ErrorHandlerConfig>
): ApplicationError {
  const error = parseAxiosError(axiosError);
  const finalConfig = { ...getErrorConfig(error), ...config };
  
  if (finalConfig.logError) {
    logError(error, context);
  }
  
  return error;
}