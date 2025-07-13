/**
 * Loading overlay component for full-page and container loading states.
 */
import React from 'react';
import LoadingSpinner, { SpinnerSize, SpinnerVariant } from './LoadingSpinner';

interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
  description?: string;
  spinnerSize?: SpinnerSize;
  spinnerVariant?: SpinnerVariant;
  backdrop?: 'light' | 'dark' | 'blur';
  fullScreen?: boolean;
  className?: string;
  children?: React.ReactNode;
}

const backdropClasses = {
  light: 'bg-white/80',
  dark: 'bg-gray-900/80',
  blur: 'bg-white/50 backdrop-blur-sm'
};

export default function LoadingOverlay({
  isVisible,
  message = 'Loading...',
  description,
  spinnerSize = 'lg',
  spinnerVariant = 'primary',
  backdrop = 'light',
  fullScreen = false,
  className = '',
  children
}: LoadingOverlayProps) {
  if (!isVisible) {
    return <>{children}</>;
  }

  const overlayClasses = `
    ${fullScreen ? 'fixed inset-0' : 'absolute inset-0'}
    flex items-center justify-center z-50
    ${backdropClasses[backdrop]}
    ${className}
  `.trim();

  const contentClasses = `
    bg-white rounded-lg shadow-lg p-6 max-w-sm mx-4
    flex flex-col items-center text-center
    ${backdrop === 'dark' ? 'bg-gray-800 text-white' : ''}
  `.trim();

  return (
    <>
      {children}
      <div className={overlayClasses}>
        <div className={contentClasses}>
          <LoadingSpinner
            size={spinnerSize}
            variant={spinnerVariant}
            showLabel={false}
          />
          <div className="mt-4">
            <h3 className="font-medium text-lg">{message}</h3>
            {description && (
              <p className="text-sm text-gray-600 mt-1">{description}</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

/**
 * Simple overlay without card styling for minimal loading states
 */
interface SimpleOverlayProps {
  isVisible: boolean;
  message?: string;
  spinnerSize?: SpinnerSize;
  spinnerVariant?: SpinnerVariant;
  backdrop?: 'light' | 'dark' | 'blur';
  fullScreen?: boolean;
  children?: React.ReactNode;
}

export function SimpleLoadingOverlay({
  isVisible,
  message = 'Loading...',
  spinnerSize = 'md',
  spinnerVariant = 'primary',
  backdrop = 'light',
  fullScreen = false,
  children
}: SimpleOverlayProps) {
  if (!isVisible) {
    return <>{children}</>;
  }

  const overlayClasses = `
    ${fullScreen ? 'fixed inset-0' : 'absolute inset-0'}
    flex flex-col items-center justify-center z-50
    ${backdropClasses[backdrop]}
  `.trim();

  return (
    <>
      {children}
      <div className={overlayClasses}>
        <LoadingSpinner
          size={spinnerSize}
          variant={spinnerVariant}
          label={message}
          showLabel={true}
        />
      </div>
    </>
  );
}

/**
 * Skeleton loading placeholder component
 */
interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  rounded?: boolean;
  animate?: boolean;
}

export function Skeleton({
  width = '100%',
  height = '1rem',
  className = '',
  rounded = false,
  animate = true
}: SkeletonProps) {
  const skeletonClasses = `
    bg-gray-200
    ${rounded ? 'rounded-full' : 'rounded'}
    ${animate ? 'animate-pulse' : ''}
    ${className}
  `.trim();

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height
  };

  return <div className={skeletonClasses} style={style} />;
}

/**
 * Skeleton loading for table rows
 */
interface TableSkeletonProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export function TableSkeleton({
  rows = 5,
  columns = 4,
  className = ''
}: TableSkeletonProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton
              key={colIndex}
              height="2rem"
              width={colIndex === 0 ? '60%' : '80%'}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton loading for card layouts
 */
interface CardSkeletonProps {
  showAvatar?: boolean;
  lines?: number;
  className?: string;
}

export function CardSkeleton({
  showAvatar = false,
  lines = 3,
  className = ''
}: CardSkeletonProps) {
  return (
    <div className={`p-4 space-y-3 ${className}`}>
      {showAvatar && (
        <div className="flex items-center space-x-3">
          <Skeleton width={40} height={40} rounded />
          <div className="flex-1 space-y-2">
            <Skeleton height="1rem" width="60%" />
            <Skeleton height="0.75rem" width="40%" />
          </div>
        </div>
      )}
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <Skeleton
            key={index}
            height="1rem"
            width={index === lines - 1 ? '80%' : '100%'}
          />
        ))}
      </div>
    </div>
  );
}