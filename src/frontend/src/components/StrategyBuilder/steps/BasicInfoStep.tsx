import React from 'react';
import { StrategyFormData, StrategyType } from '../../../types/strategy';

interface BasicInfoStepProps {
  formData: Partial<StrategyFormData>;
  updateData: (data: Partial<StrategyFormData>) => void;
  validationErrors: Record<string, string[]>;
}

export default function BasicInfoStep({ formData, updateData, validationErrors }: BasicInfoStepProps) {
  const handleInputChange = (field: keyof StrategyFormData, value: string) => {
    updateData({ [field]: value });
  };

  const getFieldError = (field: string) => {
    return validationErrors[field]?.[0];
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        {/* Strategy Name */}
        <div className="sm:col-span-2">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Strategy Name *
          </label>
          <input
            type="text"
            id="name"
            value={formData.name || ''}
            onChange={(e) => handleInputChange('name', e.target.value)}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              getFieldError('name') ? 'border-red-300' : ''
            }`}
            placeholder="Enter a descriptive name for your strategy"
          />
          {getFieldError('name') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('name')}</p>
          )}
        </div>

        {/* Process Step */}
        <div>
          <label htmlFor="process_step" className="block text-sm font-medium text-gray-700">
            Process Step *
          </label>
          <input
            type="text"
            id="process_step"
            value={formData.process_step || ''}
            onChange={(e) => handleInputChange('process_step', e.target.value)}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              getFieldError('process_step') ? 'border-red-300' : ''
            }`}
            placeholder="e.g., Lithography, Etch, CMP"
          />
          {getFieldError('process_step') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('process_step')}</p>
          )}
        </div>

        {/* Tool Type */}
        <div>
          <label htmlFor="tool_type" className="block text-sm font-medium text-gray-700">
            Tool Type *
          </label>
          <input
            type="text"
            id="tool_type"
            value={formData.tool_type || ''}
            onChange={(e) => handleInputChange('tool_type', e.target.value)}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              getFieldError('tool_type') ? 'border-red-300' : ''
            }`}
            placeholder="e.g., ASML_PAS5500, KLA_2132"
          />
          {getFieldError('tool_type') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('tool_type')}</p>
          )}
        </div>

        {/* Strategy Type */}
        <div>
          <label htmlFor="strategy_type" className="block text-sm font-medium text-gray-700">
            Strategy Type *
          </label>
          <select
            id="strategy_type"
            value={formData.strategy_type || ''}
            onChange={(e) => handleInputChange('strategy_type', e.target.value)}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              getFieldError('strategy_type') ? 'border-red-300' : ''
            }`}
          >
            <option value="">Select strategy type</option>
            <option value={StrategyType.FIXED_POINT}>Fixed Point</option>
            <option value={StrategyType.CENTER_EDGE}>Center Edge</option>
            <option value={StrategyType.UNIFORM_GRID}>Uniform Grid</option>
            <option value={StrategyType.HOTSPOT_PRIORITY}>Hotspot Priority</option>
            <option value={StrategyType.ADAPTIVE}>Adaptive</option>
            <option value={StrategyType.CUSTOM}>Custom</option>
          </select>
          {getFieldError('strategy_type') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('strategy_type')}</p>
          )}
        </div>

        {/* Author */}
        <div>
          <label htmlFor="author" className="block text-sm font-medium text-gray-700">
            Author *
          </label>
          <input
            type="text"
            id="author"
            value={formData.author || ''}
            onChange={(e) => handleInputChange('author', e.target.value)}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              getFieldError('author') ? 'border-red-300' : ''
            }`}
            placeholder="Your name or ID"
          />
          {getFieldError('author') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('author')}</p>
          )}
        </div>

        {/* Description */}
        <div className="sm:col-span-2">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            id="description"
            rows={3}
            value={formData.description || ''}
            onChange={(e) => handleInputChange('description', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Describe the purpose and key characteristics of this strategy"
          />
          {getFieldError('description') && (
            <p className="mt-1 text-sm text-red-600">{getFieldError('description')}</p>
          )}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Getting Started</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Fill in the basic information for your sampling strategy. The tool type should match your metrology equipment model, 
                and the process step should correspond to where this strategy will be used in your fab flow.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}