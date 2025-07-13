/**
 * Upload progress component for schematic file processing.
 */
import React from 'react';
import { UploadedFile } from './FileUploadZone';
import LoadingSpinner, { DotsSpinner } from '../ui/LoadingSpinner';

interface UploadProgressProps {
  files: UploadedFile[];
  onCancel?: (fileId: string) => void;
  onRemove?: (fileId: string) => void;
  onRetry?: (fileId: string) => void;
}

export default function UploadProgress({
  files,
  onCancel,
  onRemove,
  onRetry
}: UploadProgressProps) {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (file: UploadedFile) => {
    switch (file.status) {
      case 'pending':
        return (
          <div className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-gray-400"></div>
          </div>
        );
      case 'uploading':
        return <LoadingSpinner size="sm" variant="primary" />;
      case 'parsing':
        return <DotsSpinner size="sm" variant="primary" />;
      case 'completed':
        return (
          <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
            <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center">
            <svg className="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
        );
      default:
        return null;
    }
  };

  const getStatusText = (file: UploadedFile): string => {
    switch (file.status) {
      case 'pending':
        return 'Waiting to upload';
      case 'uploading':
        return `Uploading... ${file.progress}%`;
      case 'parsing':
        return 'Parsing schematic data...';
      case 'completed':
        return 'Upload complete';
      case 'error':
        return file.error || 'Upload failed';
      default:
        return 'Unknown status';
    }
  };

  const getStatusColor = (file: UploadedFile): string => {
    switch (file.status) {
      case 'pending':
        return 'text-gray-500';
      case 'uploading':
      case 'parsing':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  const canCancel = (file: UploadedFile): boolean => {
    return file.status === 'uploading' || file.status === 'parsing';
  };

  const canRetry = (file: UploadedFile): boolean => {
    return file.status === 'error';
  };

  const canRemove = (file: UploadedFile): boolean => {
    return file.status === 'completed' || file.status === 'error';
  };

  if (files.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 space-y-4">
      <h4 className="text-sm font-medium text-gray-900">Upload Progress</h4>
      <div className="space-y-3">
        {files.map((file) => (
          <div
            key={file.id}
            className="bg-white border border-gray-200 rounded-lg p-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {getStatusIcon(file)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500 ml-2">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                  <p className={`text-xs ${getStatusColor(file)}`}>
                    {getStatusText(file)}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2 ml-4">
                {canCancel(file) && onCancel && (
                  <button
                    onClick={() => onCancel(file.id)}
                    className="text-xs text-gray-500 hover:text-gray-700"
                  >
                    Cancel
                  </button>
                )}
                {canRetry(file) && onRetry && (
                  <button
                    onClick={() => onRetry(file.id)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    Retry
                  </button>
                )}
                {canRemove(file) && onRemove && (
                  <button
                    onClick={() => onRemove(file.id)}
                    className="text-xs text-gray-500 hover:text-gray-700"
                  >
                    Remove
                  </button>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            {(file.status === 'uploading' || file.status === 'parsing') && (
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      file.status === 'uploading' ? 'bg-blue-600' : 'bg-blue-400'
                    }`}
                    style={{
                      width: `${file.status === 'uploading' ? file.progress : 100}%`
                    }}
                  ></div>
                </div>
              </div>
            )}

            {/* Error Details */}
            {file.status === 'error' && file.error && (
              <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                {file.error}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}