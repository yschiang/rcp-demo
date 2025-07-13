/**
 * Drag & drop file upload zone for schematic files.
 */
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

export interface UploadedFile extends File {
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'parsing' | 'completed' | 'error';
  error?: string;
  preview?: string;
}

interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
}

const DEFAULT_ACCEPT = {
  'application/octet-stream': ['.gds', '.gdsii'],
  'application/dxf': ['.dxf'],
  'image/svg+xml': ['.svg'],
  'application/zip': ['.zip']
};

const DEFAULT_MAX_SIZE = 100 * 1024 * 1024; // 100MB

export default function FileUploadZone({
  onFilesSelected,
  accept = DEFAULT_ACCEPT,
  maxSize = DEFAULT_MAX_SIZE,
  multiple = false,
  disabled = false,
  className = ''
}: FileUploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFilesSelected(acceptedFiles);
    }
    setDragActive(false);
  }, [onFilesSelected]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    fileRejections
  } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
    disabled,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false)
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getSupportedFormats = (): string => {
    return Object.values(accept).flat().join(', ');
  };

  const getBorderColor = (): string => {
    if (disabled) return 'border-gray-200';
    if (isDragReject) return 'border-red-400';
    if (isDragActive || dragActive) return 'border-blue-400';
    return 'border-gray-300';
  };

  const getBackgroundColor = (): string => {
    if (disabled) return 'bg-gray-50';
    if (isDragReject) return 'bg-red-50';
    if (isDragActive || dragActive) return 'bg-blue-50';
    return 'bg-gray-50 hover:bg-gray-100';
  };

  return (
    <div className={`w-full ${className}`}>
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${getBorderColor()}
          ${getBackgroundColor()}
          ${disabled ? 'cursor-not-allowed opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          {/* Upload Icon */}
          <div className="mx-auto w-16 h-16 text-gray-400">
            {isDragActive ? (
              <svg className="w-full h-full text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
            ) : isDragReject ? (
              <svg className="w-full h-full text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            ) : (
              <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            )}
          </div>

          {/* Upload Text */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop schematic files here' : 'Upload Schematic Files'}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              {isDragActive
                ? 'Release to upload'
                : disabled
                ? 'File upload is currently disabled'
                : 'Drag & drop files here, or click to browse'
              }
            </p>
            <p className="text-xs text-gray-500">
              Supported formats: {getSupportedFormats()}
            </p>
            <p className="text-xs text-gray-500">
              Maximum file size: {formatFileSize(maxSize)}
            </p>
          </div>

          {/* Browse Button */}
          {!disabled && (
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Browse Files
            </button>
          )}
        </div>
      </div>

      {/* File Rejection Errors */}
      {fileRejections.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <h4 className="text-sm font-medium text-red-800 mb-2">Upload Errors:</h4>
          <ul className="text-sm text-red-700 space-y-1">
            {fileRejections.map(({ file, errors }, index) => (
              <li key={index} className="flex items-start">
                <span className="font-medium mr-2">{file.name}:</span>
                <span>{errors.map(e => e.message).join(', ')}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}