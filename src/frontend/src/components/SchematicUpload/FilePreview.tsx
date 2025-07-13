/**
 * File preview component showing schematic metadata and statistics.
 */
import React from 'react';

export interface SchematicPreview {
  id: string;
  filename: string;
  fileSize: number;
  formatType: string;
  uploadDate: string;
  dieCount: number;
  availableDieCount: number;
  waferSize?: string;
  layoutBounds: {
    width: number;
    height: number;
    xMin: number;
    yMin: number;
    xMax: number;
    yMax: number;
  };
  coordinateSystem: string;
  metadata?: {
    softwareInfo?: string;
    units?: string;
    layerInfo?: Record<string, any>;
  };
}

interface FilePreviewProps {
  preview: SchematicPreview;
  onRemove?: () => void;
  onValidate?: () => void;
  className?: string;
}

export default function FilePreview({
  preview,
  onRemove,
  onValidate,
  className = ''
}: FilePreviewProps) {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatCoordinate = (value: number): string => {
    return value.toFixed(2);
  };

  const getFormatIcon = (format: string) => {
    const formatLower = format.toLowerCase();
    
    if (formatLower.includes('gds')) {
      return (
        <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center">
          <span className="text-xs font-bold text-purple-600">GDS</span>
        </div>
      );
    } else if (formatLower.includes('dxf')) {
      return (
        <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
          <span className="text-xs font-bold text-blue-600">DXF</span>
        </div>
      );
    } else if (formatLower.includes('svg')) {
      return (
        <div className="w-8 h-8 bg-green-100 rounded flex items-center justify-center">
          <span className="text-xs font-bold text-green-600">SVG</span>
        </div>
      );
    } else {
      return (
        <div className="w-8 h-8 bg-gray-100 rounded flex items-center justify-center">
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
      );
    }
  };

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getFormatIcon(preview.formatType)}
          <div>
            <h3 className="text-lg font-medium text-gray-900">{preview.filename}</h3>
            <p className="text-sm text-gray-500">
              {formatFileSize(preview.fileSize)} • {preview.formatType.toUpperCase()} Format
            </p>
          </div>
        </div>
        
        {onRemove && (
          <button
            onClick={onRemove}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-600">{preview.dieCount.toLocaleString()}</div>
          <div className="text-sm text-gray-600">Total Dies</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-green-600">{preview.availableDieCount.toLocaleString()}</div>
          <div className="text-sm text-gray-600">Available Dies</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {((preview.availableDieCount / preview.dieCount) * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Availability</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-600">{preview.waferSize || 'Unknown'}</div>
          <div className="text-sm text-gray-600">Wafer Size</div>
        </div>
      </div>

      {/* Layout Information */}
      <div className="space-y-4">
        <h4 className="font-medium text-gray-900">Layout Information</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h5 className="font-medium text-gray-700 mb-2">Layout Bounds</h5>
            <dl className="space-y-1">
              <div className="flex justify-between">
                <dt className="text-gray-600">Width:</dt>
                <dd className="font-mono">{formatCoordinate(preview.layoutBounds.width)} μm</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Height:</dt>
                <dd className="font-mono">{formatCoordinate(preview.layoutBounds.height)} μm</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">X Range:</dt>
                <dd className="font-mono">
                  {formatCoordinate(preview.layoutBounds.xMin)} to {formatCoordinate(preview.layoutBounds.xMax)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Y Range:</dt>
                <dd className="font-mono">
                  {formatCoordinate(preview.layoutBounds.yMin)} to {formatCoordinate(preview.layoutBounds.yMax)}
                </dd>
              </div>
            </dl>
          </div>
          
          <div>
            <h5 className="font-medium text-gray-700 mb-2">File Properties</h5>
            <dl className="space-y-1">
              <div className="flex justify-between">
                <dt className="text-gray-600">Coordinate System:</dt>
                <dd className="capitalize">{preview.coordinateSystem}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Upload Date:</dt>
                <dd>{new Date(preview.uploadDate).toLocaleDateString()}</dd>
              </div>
              {preview.metadata?.units && (
                <div className="flex justify-between">
                  <dt className="text-gray-600">Units:</dt>
                  <dd>{preview.metadata.units}</dd>
                </div>
              )}
              {preview.metadata?.softwareInfo && (
                <div className="flex justify-between">
                  <dt className="text-gray-600">Created By:</dt>
                  <dd className="truncate" title={preview.metadata.softwareInfo}>
                    {preview.metadata.softwareInfo}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        {/* Metadata Details */}
        {preview.metadata?.layerInfo && Object.keys(preview.metadata.layerInfo).length > 0 && (
          <div>
            <h5 className="font-medium text-gray-700 mb-2">Layer Information</h5>
            <div className="bg-gray-50 rounded p-3 text-xs">
              <pre className="text-gray-600 whitespace-pre-wrap">
                {JSON.stringify(preview.metadata.layerInfo, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex justify-end space-x-3">
        {onValidate && (
          <button
            onClick={onValidate}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Validate with Strategy
          </button>
        )}
      </div>
    </div>
  );
}