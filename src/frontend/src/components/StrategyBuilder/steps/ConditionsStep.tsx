import React from 'react';
import { StrategyFormData, ConditionalLogic } from '../../../types/strategy';

interface ConditionsStepProps {
  formData: Partial<StrategyFormData>;
  updateData: (data: Partial<StrategyFormData>) => void;
  validationErrors: Record<string, string[]>;
}

export default function ConditionsStep({ formData, updateData, validationErrors }: ConditionsStepProps) {
  const conditions = formData.conditions || {};

  const updateConditions = (field: keyof ConditionalLogic, value: any) => {
    const updatedConditions = { ...conditions, [field]: value };
    updateData({ conditions: updatedConditions });
  };

  const addCustomCondition = () => {
    const key = prompt('Enter condition key:');
    const value = prompt('Enter condition value:');
    if (key && value) {
      const customConditions = { ...conditions.custom_conditions, [key]: value };
      updateConditions('custom_conditions', customConditions);
    }
  };

  const removeCustomCondition = (key: string) => {
    const customConditions = { ...conditions.custom_conditions };
    delete customConditions[key];
    updateConditions('custom_conditions', customConditions);
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
            <h3 className="text-sm font-medium text-blue-800">Conditional Logic</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Define conditions that control when and how your sampling strategy is applied. 
                These conditions can be based on wafer characteristics, product types, or process parameters.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        {/* Wafer Size */}
        <div>
          <label htmlFor="wafer_size" className="block text-sm font-medium text-gray-700">
            Wafer Size
          </label>
          <select
            id="wafer_size"
            value={conditions.wafer_size || ''}
            onChange={(e) => updateConditions('wafer_size', e.target.value || undefined)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Any size</option>
            <option value="200mm">200mm</option>
            <option value="300mm">300mm</option>
            <option value="450mm">450mm</option>
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Apply this strategy only to wafers of the specified size
          </p>
        </div>

        {/* Product Type */}
        <div>
          <label htmlFor="product_type" className="block text-sm font-medium text-gray-700">
            Product Type
          </label>
          <input
            type="text"
            id="product_type"
            value={conditions.product_type || ''}
            onChange={(e) => updateConditions('product_type', e.target.value || undefined)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="e.g., Logic, Memory, Analog"
          />
          <p className="mt-1 text-xs text-gray-500">
            Filter by product type or technology node
          </p>
        </div>

        {/* Process Layer */}
        <div>
          <label htmlFor="process_layer" className="block text-sm font-medium text-gray-700">
            Process Layer
          </label>
          <input
            type="text"
            id="process_layer"
            value={conditions.process_layer || ''}
            onChange={(e) => updateConditions('process_layer', e.target.value || undefined)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="e.g., Metal1, Via2, Contact"
          />
          <p className="mt-1 text-xs text-gray-500">
            Specify the process layer this strategy applies to
          </p>
        </div>

        {/* Defect Density Threshold */}
        <div>
          <label htmlFor="defect_density_threshold" className="block text-sm font-medium text-gray-700">
            Defect Density Threshold
          </label>
          <input
            type="number"
            id="defect_density_threshold"
            value={conditions.defect_density_threshold || ''}
            onChange={(e) => updateConditions('defect_density_threshold', e.target.value ? parseFloat(e.target.value) : undefined)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="0.1"
            step="0.01"
            min="0"
          />
          <p className="mt-1 text-xs text-gray-500">
            Apply strategy when defect density exceeds this threshold
          </p>
        </div>
      </div>

      {/* Custom Conditions */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Custom Conditions</h3>
          <button
            onClick={addCustomCondition}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Condition
          </button>
        </div>

        {conditions.custom_conditions && Object.keys(conditions.custom_conditions).length > 0 ? (
          <div className="space-y-3">
            {Object.entries(conditions.custom_conditions).map(([key, value]) => (
              <div key={key} className="flex items-center gap-3 p-3 bg-gray-50 rounded-md">
                <div className="flex-1">
                  <span className="text-sm font-medium text-gray-700">{key}:</span>
                  <span className="ml-2 text-sm text-gray-900">{value}</span>
                </div>
                <button
                  onClick={() => removeCustomCondition(key)}
                  className="text-red-600 hover:text-red-800"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 text-gray-500 bg-gray-50 rounded-md">
            No custom conditions defined. Click "Add Condition" to create custom logic.
          </div>
        )}
      </div>

      {/* Preview Section */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Condition Summary</h3>
        <div className="bg-gray-50 rounded-md p-4">
          {Object.keys(conditions).length === 0 ? (
            <p className="text-gray-500">No conditions set - strategy will apply to all wafers.</p>
          ) : (
            <div className="space-y-2 text-sm">
              {conditions.wafer_size && (
                <p><span className="font-medium">Wafer Size:</span> {conditions.wafer_size}</p>
              )}
              {conditions.product_type && (
                <p><span className="font-medium">Product Type:</span> {conditions.product_type}</p>
              )}
              {conditions.process_layer && (
                <p><span className="font-medium">Process Layer:</span> {conditions.process_layer}</p>
              )}
              {conditions.defect_density_threshold && (
                <p><span className="font-medium">Defect Density Threshold:</span> {conditions.defect_density_threshold}</p>
              )}
              {conditions.custom_conditions && Object.keys(conditions.custom_conditions).length > 0 && (
                <div>
                  <span className="font-medium">Custom Conditions:</span>
                  <ul className="ml-4 mt-1">
                    {Object.entries(conditions.custom_conditions).map(([key, value]) => (
                      <li key={key}>• {key}: {value}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {validationErrors.conditions && (
        <div className="text-sm text-red-600">
          {validationErrors.conditions.map((error, index) => (
            <p key={index}>{error}</p>
          ))}
        </div>
      )}
    </div>
  );
}