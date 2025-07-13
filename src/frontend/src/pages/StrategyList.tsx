import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useStrategyStore } from '../stores/strategyStore';
import { StrategyLifecycle } from '../types/strategy';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { TableSkeleton } from '../components/ui/LoadingOverlay';

export default function StrategyList() {
  const {
    strategies,
    loading,
    error,
    filters,
    loadStrategies,
    setFilters,
    deleteStrategy,
  } = useStrategyStore();

  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadStrategies();
  }, [loadStrategies]);

  const handleFilterChange = (field: string, value: string) => {
    const newFilters = { ...filters, [field]: value || undefined };
    setFilters(newFilters);
    loadStrategies(newFilters);
  };

  const handleDeleteStrategy = async (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete strategy "${name}"?`)) {
      try {
        await deleteStrategy(id);
      } catch (error) {
        console.error('Failed to delete strategy:', error);
      }
    }
  };

  const filteredStrategies = strategies.filter(strategy =>
    strategy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    strategy.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    strategy.author.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getLifecycleColor = (state: string) => {
    switch (state) {
      case StrategyLifecycle.DRAFT:
        return 'bg-gray-100 text-gray-800';
      case StrategyLifecycle.REVIEW:
        return 'bg-yellow-100 text-yellow-800';
      case StrategyLifecycle.APPROVED:
        return 'bg-blue-100 text-blue-800';
      case StrategyLifecycle.ACTIVE:
        return 'bg-green-100 text-green-800';
      case StrategyLifecycle.DEPRECATED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center min-h-32">
          <LoadingSpinner size="lg" showLabel label="Loading strategies..." />
        </div>
        <TableSkeleton rows={5} columns={6} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error Loading Strategies</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Strategy Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your wafer sampling strategies and configurations
          </p>
        </div>
        <Link
          to="/strategy-builder"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create New Strategy
        </Link>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">
              Search
            </label>
            <input
              type="text"
              id="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search strategies..."
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label htmlFor="process_step" className="block text-sm font-medium text-gray-700">
              Process Step
            </label>
            <select
              id="process_step"
              value={filters.process_step || ''}
              onChange={(e) => handleFilterChange('process_step', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All Process Steps</option>
              <option value="Lithography">Lithography</option>
              <option value="Etch">Etch</option>
              <option value="CMP">CMP</option>
              <option value="Deposition">Deposition</option>
              <option value="Implant">Implant</option>
            </select>
          </div>

          <div>
            <label htmlFor="tool_type" className="block text-sm font-medium text-gray-700">
              Tool Type
            </label>
            <input
              type="text"
              id="tool_type"
              value={filters.tool_type || ''}
              onChange={(e) => handleFilterChange('tool_type', e.target.value)}
              placeholder="e.g., ASML_PAS5500"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="lifecycle_state" className="block text-sm font-medium text-gray-700">
              Lifecycle State
            </label>
            <select
              id="lifecycle_state"
              value={filters.lifecycle_state || ''}
              onChange={(e) => handleFilterChange('lifecycle_state', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All States</option>
              <option value={StrategyLifecycle.DRAFT}>Draft</option>
              <option value={StrategyLifecycle.REVIEW}>Review</option>
              <option value={StrategyLifecycle.APPROVED}>Approved</option>
              <option value={StrategyLifecycle.ACTIVE}>Active</option>
              <option value={StrategyLifecycle.DEPRECATED}>Deprecated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Strategy List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        {filteredStrategies.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No strategies found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first sampling strategy.
            </p>
            <div className="mt-6">
              <Link
                to="/strategy-builder"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Strategy
              </Link>
            </div>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {filteredStrategies.map((strategy) => (
              <li key={strategy.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {strategy.name}
                      </h3>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLifecycleColor(
                          strategy.lifecycle_state
                        )}`}
                      >
                        {strategy.lifecycle_state}
                      </span>
                    </div>
                    
                    {strategy.description && (
                      <p className="mt-1 text-sm text-gray-500 truncate">
                        {strategy.description}
                      </p>
                    )}
                    
                    <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                      <span>Process: {strategy.process_step}</span>
                      <span>Tool: {strategy.tool_type}</span>
                      <span>Rules: {strategy.rule_count}</span>
                      <span>Author: {strategy.author}</span>
                      <span>Modified: {new Date(strategy.modified_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/strategies/${strategy.id}`}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      View
                    </Link>
                    <Link
                      to={`/strategies/${strategy.id}/edit`}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      Edit
                    </Link>
                    <button
                      onClick={() => handleDeleteStrategy(strategy.id, strategy.name)}
                      className="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}