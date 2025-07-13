/**
 * Reusable loading spinner component with different sizes and styles.
 */
import React from 'react';

export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type SpinnerVariant = 'primary' | 'secondary' | 'white' | 'gray';

interface LoadingSpinnerProps {
  size?: SpinnerSize;
  variant?: SpinnerVariant;
  className?: string;
  label?: string;
  showLabel?: boolean;
}

const sizeClasses: Record<SpinnerSize, string> = {
  xs: 'h-3 w-3',
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12'
};

const variantClasses: Record<SpinnerVariant, string> = {
  primary: 'text-blue-600',
  secondary: 'text-gray-600',
  white: 'text-white',
  gray: 'text-gray-400'
};

const labelSizeClasses: Record<SpinnerSize, string> = {
  xs: 'text-xs',
  sm: 'text-sm',
  md: 'text-sm',
  lg: 'text-base',
  xl: 'text-lg'
};

export default function LoadingSpinner({
  size = 'md',
  variant = 'primary',
  className = '',
  label = 'Loading...',
  showLabel = false
}: LoadingSpinnerProps) {
  const spinnerClasses = `
    animate-spin rounded-full border-2 border-transparent
    ${sizeClasses[size]}
    ${variantClasses[variant]}
    ${className}
  `.trim();

  const labelClasses = `
    mt-2 font-medium
    ${labelSizeClasses[size]}
    ${variantClasses[variant]}
  `.trim();

  return (
    <div className="flex flex-col items-center justify-center">
      <svg
        className={spinnerClasses}
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {showLabel && (
        <div className={labelClasses}>
          {label}
        </div>
      )}
    </div>
  );
}

/**
 * Inline loading spinner for buttons and form elements
 */
interface InlineSpinnerProps {
  size?: SpinnerSize;
  variant?: SpinnerVariant;
  className?: string;
}

export function InlineSpinner({
  size = 'sm',
  variant = 'primary',
  className = ''
}: InlineSpinnerProps) {
  return (
    <LoadingSpinner
      size={size}
      variant={variant}
      className={`inline-block ${className}`}
    />
  );
}

/**
 * Button loading spinner that replaces button content
 */
interface ButtonSpinnerProps {
  variant?: SpinnerVariant;
  label?: string;
}

export function ButtonSpinner({
  variant = 'white',
  label = 'Loading...'
}: ButtonSpinnerProps) {
  return (
    <div className="flex items-center justify-center gap-2">
      <LoadingSpinner size="sm" variant={variant} />
      <span>{label}</span>
    </div>
  );
}

/**
 * Dots loading animation for minimal spaces
 */
interface DotsSpinnerProps {
  variant?: SpinnerVariant;
  size?: SpinnerSize;
}

export function DotsSpinner({
  variant = 'primary',
  size = 'md'
}: DotsSpinnerProps) {
  const dotSize = size === 'xs' ? 'h-1 w-1' : 
                 size === 'sm' ? 'h-1.5 w-1.5' :
                 size === 'md' ? 'h-2 w-2' :
                 size === 'lg' ? 'h-3 w-3' : 'h-4 w-4';

  return (
    <div className="flex items-center space-x-1">
      <div
        className={`${dotSize} ${variantClasses[variant]} bg-current rounded-full animate-pulse`}
        style={{ animationDelay: '0ms' }}
      />
      <div
        className={`${dotSize} ${variantClasses[variant]} bg-current rounded-full animate-pulse`}
        style={{ animationDelay: '150ms' }}
      />
      <div
        className={`${dotSize} ${variantClasses[variant]} bg-current rounded-full animate-pulse`}
        style={{ animationDelay: '300ms' }}
      />
    </div>
  );
}