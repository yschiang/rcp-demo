/**
 * Centralized toast notification service using react-hot-toast.
 */
import React from 'react';
import toast, { Toast } from 'react-hot-toast';
import { ApplicationError, ErrorSeverity } from '../types/strategy';
import { getErrorMessage, getErrorSeverity, isRetryableError } from './errorHandler';

/**
 * Toast configuration options
 */
interface ToastOptions {
  duration?: number;
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
  style?: React.CSSProperties;
  className?: string;
  icon?: string;
  id?: string;
}

/**
 * Enhanced toast options with retry functionality
 */
interface EnhancedToastOptions extends ToastOptions {
  retryAction?: () => void;
  retryLabel?: string;
}

/**
 * Default toast configurations based on severity
 */
const SEVERITY_CONFIGS: Record<ErrorSeverity, ToastOptions> = {
  info: {
    duration: 4000,
    icon: 'ℹ️',
    style: {
      background: '#EBF8FF',
      color: '#2B6CB0',
      border: '1px solid #BEE3F8'
    }
  },
  warning: {
    duration: 6000,
    icon: '⚠️',
    style: {
      background: '#FFFBEB',
      color: '#D69E2E',
      border: '1px solid #F6E05E'
    }
  },
  error: {
    duration: 8000,
    icon: '❌',
    style: {
      background: '#FED7D7',
      color: '#C53030',
      border: '1px solid #FC8181'
    }
  },
  critical: {
    duration: 0, // Never auto-dismiss
    icon: '🚨',
    style: {
      background: '#FED7D7',
      color: '#742A2A',
      border: '2px solid #E53E3E',
      fontWeight: 'bold'
    }
  }
};

/**
 * Show success toast notification
 */
export function showSuccess(
  message: string,
  options?: ToastOptions
): string {
  return toast.success(message, {
    duration: 4000,
    icon: '✅',
    style: {
      background: '#F0FFF4',
      color: '#22543D',
      border: '1px solid #9AE6B4'
    },
    ...options
  });
}

/**
 * Show info toast notification
 */
export function showInfo(
  message: string,
  options?: ToastOptions
): string {
  return toast(message, {
    ...SEVERITY_CONFIGS.info,
    ...options
  });
}

/**
 * Show warning toast notification
 */
export function showWarning(
  message: string,
  options?: ToastOptions
): string {
  return toast(message, {
    ...SEVERITY_CONFIGS.warning,
    ...options
  });
}

/**
 * Show error toast notification
 */
export function showError(
  message: string,
  options?: EnhancedToastOptions
): string {
  const { retryAction, retryLabel = 'Retry', ...toastOptions } = options || {};
  
  if (retryAction) {
    return toast((t) => (
      <div className="flex items-center gap-3">
        <span className="flex-1">{message}</span>
        <div className="flex gap-2">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              retryAction();
            }}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
          >
            {retryLabel}
          </button>
          <button
            onClick={() => toast.dismiss(t.id)}
            className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400 transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    ), {
      ...SEVERITY_CONFIGS.error,
      ...toastOptions,
      duration: 0 // Don't auto-dismiss when there's a retry action
    });
  }
  
  return toast.error(message, {
    ...SEVERITY_CONFIGS.error,
    ...toastOptions
  });
}

/**
 * Show critical error toast notification
 */
export function showCritical(
  message: string,
  options?: EnhancedToastOptions
): string {
  const { retryAction, retryLabel = 'Retry', ...toastOptions } = options || {};
  
  if (retryAction) {
    return toast((t) => (
      <div className="flex items-center gap-3">
        <span className="text-lg">🚨</span>
        <div className="flex-1">
          <div className="font-bold text-red-800">Critical Error</div>
          <div className="text-red-700">{message}</div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              retryAction();
            }}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
          >
            {retryLabel}
          </button>
          <button
            onClick={() => toast.dismiss(t.id)}
            className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400 transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    ), {
      ...SEVERITY_CONFIGS.critical,
      ...toastOptions
    });
  }
  
  return toast(message, {
    ...SEVERITY_CONFIGS.critical,
    ...toastOptions
  });
}

/**
 * Show loading toast for long-running operations
 */
export function showLoading(
  message: string,
  options?: ToastOptions
): string {
  return toast.loading(message, {
    duration: 0,
    style: {
      background: '#F7FAFC',
      color: '#4A5568',
      border: '1px solid #E2E8F0'
    },
    ...options
  });
}

/**
 * Update existing loading toast with success
 */
export function updateLoadingToSuccess(
  toastId: string,
  message: string,
  options?: ToastOptions
): void {
  toast.success(message, {
    id: toastId,
    duration: 4000,
    ...options
  });
}

/**
 * Update existing loading toast with error
 */
export function updateLoadingToError(
  toastId: string,
  message: string,
  options?: EnhancedToastOptions
): void {
  const { retryAction, ...toastOptions } = options || {};
  
  if (retryAction) {
    showError(message, { ...toastOptions, retryAction });
    toast.dismiss(toastId);
  } else {
    toast.error(message, {
      id: toastId,
      duration: 8000,
      ...toastOptions
    });
  }
}

/**
 * Show application error with appropriate severity and retry option
 */
export function showApplicationError(
  error: ApplicationError,
  retryAction?: () => void
): string {
  const message = getErrorMessage(error);
  const severity = getErrorSeverity(error);
  const canRetry = isRetryableError(error);
  
  const options: EnhancedToastOptions = canRetry && retryAction 
    ? { retryAction }
    : {};
  
  switch (severity) {
    case 'info':
      return showInfo(message, options);
    case 'warning':
      return showWarning(message, options);
    case 'error':
      return showError(message, options);
    case 'critical':
      return showCritical(message, options);
    default:
      return showError(message, options);
  }
}

/**
 * Show validation errors as a grouped toast
 */
export function showValidationErrors(
  fieldErrors: Record<string, string[]>
): string {
  const errorCount = Object.keys(fieldErrors).length;
  const totalErrors = Object.values(fieldErrors).flat().length;
  
  if (errorCount === 0) return '';
  
  const title = `${totalErrors} validation error${totalErrors > 1 ? 's' : ''} found`;
  const details = Object.entries(fieldErrors)
    .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
    .join('\n');
  
  return toast((t) => (
    <div className="max-w-md">
      <div className="font-medium text-red-800 mb-2">{title}</div>
      <div className="text-sm text-red-700 whitespace-pre-line">{details}</div>
      <button
        onClick={() => toast.dismiss(t.id)}
        className="mt-2 px-3 py-1 bg-red-100 text-red-800 text-sm rounded hover:bg-red-200 transition-colors"
      >
        Dismiss
      </button>
    </div>
  ), {
    duration: 10000,
    icon: '📝',
    style: {
      background: '#FED7D7',
      color: '#C53030',
      border: '1px solid #FC8181'
    }
  });
}

/**
 * Dismiss specific toast
 */
export function dismissToast(toastId: string): void {
  toast.dismiss(toastId);
}

/**
 * Dismiss all toasts
 */
export function dismissAllToasts(): void {
  toast.dismiss();
}

/**
 * Create a promise-based toast for async operations
 */
export function showPromiseToast<T>(
  promise: Promise<T>,
  {
    loading,
    success,
    error
  }: {
    loading: string;
    success: string | ((data: T) => string);
    error: string | ((error: any) => string);
  }
): Promise<T> {
  return toast.promise(promise, {
    loading,
    success,
    error
  });
}