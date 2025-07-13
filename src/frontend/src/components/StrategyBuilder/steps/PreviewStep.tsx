import React, { useState, useEffect } from 'react';
import { StrategyFormData, SimulationResult } from '../../../types/strategy';
import WaferMapVisualization from '../../WaferMap/WaferMapVisualization';
import { useStrategyStore } from '../../../stores/strategyStore';

interface PreviewStepProps {
  formData: Partial<StrategyFormData>;
  updateData: (data: Partial<StrategyFormData>) => void;
  validationErrors: Record<string, string[]>;
}

export default function PreviewStep({ formData, updateData, validationErrors }: PreviewStepProps) {
  const { runSimulation, builderState } = useStrategyStore();
  const [isRunningSimulation, setIsRunningSimulation] = useState(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);

  const handleRunSimulation = async () => {
    setIsRunningSimulation(true);
    try {
      // Generate dummy wafer map data for demonstration
      const dummyWaferMap = {
        dies: Array.from({ length: 1000 }, (_, i) => ({
          x: (i % 32) - 16,
          y: Math.floor(i / 32) - 16,
          available: Math.random() > 0.1, // 90% of dies are available
        })),
        metadata: {
          wafer_size: '300mm',
          product_type: 'Logic',
          lot_id: 'DEMO001',
        },
      };

      const result = await runSimulation({
        strategy_id: 'preview',
        wafer_map_data: dummyWaferMap,
      });
      
      setSimulationResult(result);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setIsRunningSimulation(false);
    }
  };

  const validateStrategy = () => {
    const errors: string[] = [];
    
    if (!formData.name) errors.push('Strategy name is required');
    if (!formData.process_step) errors.push('Process step is required');
    if (!formData.tool_type) errors.push('Tool type is required');
    if (!formData.author) errors.push('Author is required');
    if (!formData.rules || formData.rules.length === 0) errors.push('At least one rule is required');
    
    return errors;
  };

  const validationErrors_local = validateStrategy();
  const isValid = validationErrors_local.length === 0;

  return (
    <div className="space-y-6">
      {/* Strategy Summary */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Strategy Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Basic Information</h4>
            <dl className="space-y-1">
              <div><dt className="inline font-medium">Name:</dt> <dd className="inline ml-1">{formData.name || 'Untitled'}</dd></div>
              <div><dt className="inline font-medium">Process:</dt> <dd className="inline ml-1">{formData.process_step || 'Not specified'}</dd></div>
              <div><dt className="inline font-medium">Tool:</dt> <dd className="inline ml-1">{formData.tool_type || 'Not specified'}</dd></div>
              <div><dt className="inline font-medium">Type:</dt> <dd className="inline ml-1">{formData.strategy_type || 'Not specified'}</dd></div>
              <div><dt className="inline font-medium">Author:</dt> <dd className="inline ml-1">{formData.author || 'Not specified'}</dd></div>
            </dl>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Configuration</h4>
            <dl className="space-y-1">
              <div><dt className="inline font-medium">Rules:</dt> <dd className="inline ml-1">{formData.rules?.length || 0} defined</dd></div>
              <div><dt className="inline font-medium">Conditions:</dt> <dd className="inline ml-1">{formData.conditions && Object.keys(formData.conditions).length > 0 ? 'Configured' : 'None'}</dd></div>
              <div><dt className="inline font-medium">Transformations:</dt> <dd className="inline ml-1">{formData.transformations ? 'Configured' : 'Default'}</dd></div>
            </dl>
          </div>
        </div>

        {formData.description && (
          <div className="mt-4">
            <h4 className="font-medium text-gray-700 mb-2">Description</h4>
            <p className="text-sm text-gray-600">{formData.description}</p>
          </div>
        )}
      </div>

      {/* Validation */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Validation</h3>
        
        {isValid ? (
          <div className="flex items-center text-green-600">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Strategy is valid and ready to create</span>
          </div>
        ) : (
          <div>
            <div className="flex items-center text-red-600 mb-3">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Please fix the following issues:</span>
            </div>
            <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
              {validationErrors_local.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Simulation */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Strategy Simulation</h3>
          <button
            onClick={handleRunSimulation}
            disabled={!isValid || isRunningSimulation}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md ${
              isValid && !isRunningSimulation
                ? 'text-white bg-blue-600 hover:bg-blue-700'
                : 'text-gray-400 bg-gray-200 cursor-not-allowed'
            }`}
          >
            {isRunningSimulation ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running...
              </>
            ) : (
              'Run Simulation'
            )}
          </button>
        </div>

        {simulationResult ? (
          <div className="space-y-6">
            {/* Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-blue-600">{simulationResult.coverage_stats.selected_count}</div>
                <div className="text-sm text-gray-600">Selected Dies</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-green-600">{simulationResult.coverage_stats.coverage_percentage.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Coverage</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-gray-600">{simulationResult.coverage_stats.available_dies}</div>
                <div className="text-sm text-gray-600">Available Dies</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-gray-600">{simulationResult.coverage_stats.total_dies}</div>
                <div className="text-sm text-gray-600">Total Dies</div>
              </div>
            </div>

            {/* Wafer Map Visualization */}
            <div>
              <h4 className="font-medium text-gray-700 mb-3">Wafer Map Preview</h4>
              <div className="border border-gray-200 rounded-lg bg-gray-50 p-4">
                <WaferMapVisualization
                  waferData={{
                    dies: simulationResult.selected_points.map(point => ({
                      x: point.x,
                      y: point.y,
                      available: point.available,
                    })),
                  }}
                  selectedPoints={simulationResult.selected_points}
                  onPointSelect={() => {}} // Read-only in preview
                />
              </div>
            </div>

            {/* Warnings */}
            {simulationResult.warnings.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">Simulation Warnings</h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <ul className="list-disc list-inside space-y-1">
                        {simulationResult.warnings.map((warning, index) => (
                          <li key={index}>{warning}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="mt-2">Run simulation to preview your strategy</p>
          </div>
        )}
      </div>

      {Object.keys(validationErrors).length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Validation Errors</h3>
              <div className="mt-2 text-sm text-red-700">
                {Object.entries(validationErrors).map(([field, errors]) => (
                  <div key={field} className="mb-1">
                    <strong>{field}:</strong> {errors.join(', ')}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}