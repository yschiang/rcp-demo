import React from 'react';
import { StrategyFormData, TransformationConfig } from '../../../types/strategy';

interface TransformationsStepProps {
  formData: Partial<StrategyFormData>;
  updateData: (data: Partial<StrategyFormData>) => void;
  validationErrors: Record<string, string[]>;
}

export default function TransformationsStep({ formData, updateData, validationErrors }: TransformationsStepProps) {
  const transformations = formData.transformations || {
    rotation_angle: 0,
    scale_factor: 1,
    offset_x: 0,
    offset_y: 0,
    flip_x: false,
    flip_y: false,
  };

  const updateTransformations = (field: keyof TransformationConfig, value: any) => {
    const updatedTransformations = { ...transformations, [field]: value };
    updateData({ transformations: updatedTransformations });
  };

  const resetTransformations = () => {
    updateData({
      transformations: {
        rotation_angle: 0,
        scale_factor: 1,
        offset_x: 0,
        offset_y: 0,
        flip_x: false,
        flip_y: false,
      }
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Coordinate Transformations</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Configure how sampling coordinates are transformed before being sent to the tool. 
                This includes rotation, scaling, offset adjustments, and coordinate system flips.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Rotation */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Rotation & Scaling</h3>
          
          <div>
            <label htmlFor="rotation_angle" className="block text-sm font-medium text-gray-700">
              Rotation Angle (degrees)
            </label>
            <input
              type="number"
              id="rotation_angle"
              value={transformations.rotation_angle}
              onChange={(e) => updateTransformations('rotation_angle', parseFloat(e.target.value) || 0)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              step="0.1"
              min="-360"
              max="360"
            />
            <p className="mt-1 text-xs text-gray-500">
              Rotate coordinates clockwise (0-360 degrees)
            </p>
          </div>

          <div>
            <label htmlFor="scale_factor" className="block text-sm font-medium text-gray-700">
              Scale Factor
            </label>
            <input
              type="number"
              id="scale_factor"
              value={transformations.scale_factor}
              onChange={(e) => updateTransformations('scale_factor', parseFloat(e.target.value) || 1)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              step="0.01"
              min="0.01"
              max="10"
            />
            <p className="mt-1 text-xs text-gray-500">
              Scale coordinates (1.0 = no scaling)
            </p>
          </div>
        </div>

        {/* Translation */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Translation</h3>
          
          <div>
            <label htmlFor="offset_x" className="block text-sm font-medium text-gray-700">
              X Offset
            </label>
            <input
              type="number"
              id="offset_x"
              value={transformations.offset_x}
              onChange={(e) => updateTransformations('offset_x', parseFloat(e.target.value) || 0)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              step="0.1"
            />
            <p className="mt-1 text-xs text-gray-500">
              Horizontal offset in micrometers
            </p>
          </div>

          <div>
            <label htmlFor="offset_y" className="block text-sm font-medium text-gray-700">
              Y Offset
            </label>
            <input
              type="number"
              id="offset_y"
              value={transformations.offset_y}
              onChange={(e) => updateTransformations('offset_y', parseFloat(e.target.value) || 0)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              step="0.1"
            />
            <p className="mt-1 text-xs text-gray-500">
              Vertical offset in micrometers
            </p>
          </div>
        </div>
      </div>

      {/* Flips */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Coordinate System Flips</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="flex items-center">
            <input
              id="flip_x"
              type="checkbox"
              checked={transformations.flip_x}
              onChange={(e) => updateTransformations('flip_x', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="flip_x" className="ml-2 block text-sm text-gray-900">
              Flip X Coordinates
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="flip_y"
              type="checkbox"
              checked={transformations.flip_y}
              onChange={(e) => updateTransformations('flip_y', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="flip_y" className="ml-2 block text-sm text-gray-900">
              Flip Y Coordinates
            </label>
          </div>
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Flip coordinates to match tool coordinate system orientation
        </p>
      </div>

      {/* Preview */}
      <div className="border-t pt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Transformation Preview</h3>
          <button
            onClick={resetTransformations}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Reset All
          </button>
        </div>

        <div className="bg-gray-50 rounded-md p-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Current Settings</h4>
              <ul className="space-y-1 text-gray-600">
                <li>Rotation: {transformations.rotation_angle}°</li>
                <li>Scale: {transformations.scale_factor}x</li>
                <li>X Offset: {transformations.offset_x}</li>
                <li>Y Offset: {transformations.offset_y}</li>
                <li>Flip X: {transformations.flip_x ? 'Yes' : 'No'}</li>
                <li>Flip Y: {transformations.flip_y ? 'Yes' : 'No'}</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Example Transformation</h4>
              <div className="text-gray-600">
                <p className="mb-1">Input point: (10, 20)</p>
                <p>
                  Output: ({' '}
                  {(
                    (transformations.flip_x ? -1 : 1) *
                    (10 * Math.cos(transformations.rotation_angle * Math.PI / 180) - 
                     20 * Math.sin(transformations.rotation_angle * Math.PI / 180)) *
                    transformations.scale_factor +
                    transformations.offset_x
                  ).toFixed(1)}, {' '}
                  {(
                    (transformations.flip_y ? -1 : 1) *
                    (10 * Math.sin(transformations.rotation_angle * Math.PI / 180) + 
                     20 * Math.cos(transformations.rotation_angle * Math.PI / 180)) *
                    transformations.scale_factor +
                    transformations.offset_y
                  ).toFixed(1)} )
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Transforms */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Custom Transformations</h3>
        <div className="bg-gray-50 rounded-md p-4">
          <p className="text-sm text-gray-600 mb-3">
            Define additional custom transformation functions (advanced users only)
          </p>
          <textarea
            value={transformations.custom_transforms ? JSON.stringify(transformations.custom_transforms, null, 2) : ''}
            onChange={(e) => {
              try {
                const customTransforms = e.target.value ? JSON.parse(e.target.value) : undefined;
                updateTransformations('custom_transforms', customTransforms);
              } catch {}
            }}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            rows={4}
            placeholder='[{"type": "matrix", "params": {"a": 1, "b": 0, "c": 0, "d": 1, "e": 0, "f": 0}}]'
          />
          <p className="mt-1 text-xs text-gray-500">
            JSON array of custom transformation objects
          </p>
        </div>
      </div>

      {validationErrors.transformations && (
        <div className="text-sm text-red-600">
          {validationErrors.transformations.map((error, index) => (
            <p key={index}>{error}</p>
          ))}
        </div>
      )}
    </div>
  );
}