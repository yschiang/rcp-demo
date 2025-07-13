import React, { useState } from 'react';
import { StrategyFormData, RuleConfig } from '../../../types/strategy';

interface RulesConfigStepProps {
  formData: Partial<StrategyFormData>;
  updateData: (data: Partial<StrategyFormData>) => void;
  validationErrors: Record<string, string[]>;
}

export default function RulesConfigStep({ formData, updateData, validationErrors }: RulesConfigStepProps) {
  const [newRule, setNewRule] = useState<Partial<RuleConfig>>({
    rule_type: '',
    parameters: {},
    weight: 1,
    enabled: true,
  });

  const rules = formData.rules || [];

  const addRule = () => {
    if (!newRule.rule_type) return;
    
    const rule: RuleConfig = {
      rule_type: newRule.rule_type,
      parameters: newRule.parameters || {},
      weight: newRule.weight || 1,
      enabled: true,
    };

    updateData({
      rules: [...rules, rule]
    });

    setNewRule({
      rule_type: '',
      parameters: {},
      weight: 1,
      enabled: true,
    });
  };

  const removeRule = (index: number) => {
    const updatedRules = rules.filter((_, i) => i !== index);
    updateData({ rules: updatedRules });
  };

  const updateRule = (index: number, field: keyof RuleConfig, value: any) => {
    const updatedRules = [...rules];
    updatedRules[index] = { ...updatedRules[index], [field]: value };
    updateData({ rules: updatedRules });
  };

  const renderParametersForm = (ruleType: string, parameters: Record<string, any>, onChange: (params: Record<string, any>) => void) => {
    switch (ruleType) {
      case 'fixed_point':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Points (x,y coordinates)</label>
              <textarea
                value={parameters.points ? JSON.stringify(parameters.points, null, 2) : '[[0, 0]]'}
                onChange={(e) => {
                  try {
                    const points = JSON.parse(e.target.value);
                    onChange({ ...parameters, points });
                  } catch {}
                }}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                rows={3}
                placeholder='[[10, 10], [20, 20], [-10, -10]]'
              />
              <p className="mt-1 text-xs text-gray-500">JSON array of [x, y] coordinate pairs</p>
            </div>
          </div>
        );
      
      case 'center_edge':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Center Points</label>
              <input
                type="number"
                value={parameters.center_points || 5}
                onChange={(e) => onChange({ ...parameters, center_points: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Edge Points</label>
              <input
                type="number"
                value={parameters.edge_points || 8}
                onChange={(e) => onChange({ ...parameters, edge_points: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="1"
              />
            </div>
          </div>
        );
      
      case 'uniform_grid':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Grid Spacing</label>
              <input
                type="number"
                value={parameters.grid_spacing || 10}
                onChange={(e) => onChange({ ...parameters, grid_spacing: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Offset X</label>
              <input
                type="number"
                value={parameters.offset_x || 0}
                onChange={(e) => onChange({ ...parameters, offset_x: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Offset Y</label>
              <input
                type="number"
                value={parameters.offset_y || 0}
                onChange={(e) => onChange({ ...parameters, offset_y: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>
        );
      
      default:
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700">Parameters (JSON)</label>
            <textarea
              value={JSON.stringify(parameters, null, 2)}
              onChange={(e) => {
                try {
                  const params = JSON.parse(e.target.value);
                  onChange(params);
                } catch {}
              }}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              rows={3}
              placeholder='{}'
            />
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Existing Rules */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Current Rules</h3>
        {rules.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            No rules defined yet. Add your first rule below.
          </div>
        ) : (
          <div className="space-y-4">
            {rules.map((rule, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h4 className="font-medium text-gray-900 capitalize">
                      {rule.rule_type.replace('_', ' ')}
                    </h4>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Weight: {rule.weight}
                    </span>
                  </div>
                  <button
                    onClick={() => removeRule(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Weight</label>
                    <input
                      type="number"
                      value={rule.weight}
                      onChange={(e) => updateRule(index, 'weight', parseFloat(e.target.value))}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      min="0"
                      step="0.1"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    {renderParametersForm(rule.rule_type, rule.parameters, (params) => updateRule(index, 'parameters', params))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add New Rule */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Rule</h3>
        <div className="bg-gray-50 rounded-lg p-4 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Rule Type</label>
              <select
                value={newRule.rule_type}
                onChange={(e) => setNewRule({ ...newRule, rule_type: e.target.value, parameters: {} })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="">Select rule type</option>
                <option value="fixed_point">Fixed Point</option>
                <option value="center_edge">Center Edge</option>
                <option value="uniform_grid">Uniform Grid</option>
                <option value="hotspot_priority">Hotspot Priority</option>
                <option value="adaptive">Adaptive</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Weight</label>
              <input
                type="number"
                value={newRule.weight}
                onChange={(e) => setNewRule({ ...newRule, weight: parseFloat(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="0"
                step="0.1"
              />
            </div>
          </div>

          {newRule.rule_type && (
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Parameters</h4>
              {renderParametersForm(newRule.rule_type, newRule.parameters || {}, (params) => setNewRule({ ...newRule, parameters: params }))}
            </div>
          )}

          <button
            onClick={addRule}
            disabled={!newRule.rule_type}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Add Rule
          </button>
        </div>
      </div>

      {validationErrors.rules && (
        <div className="text-sm text-red-600">
          {validationErrors.rules.map((error, index) => (
            <p key={index}>{error}</p>
          ))}
        </div>
      )}
    </div>
  );
}