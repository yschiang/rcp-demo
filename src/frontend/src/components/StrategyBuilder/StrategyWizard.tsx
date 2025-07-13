/**
 * Multi-step strategy creation wizard component.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStrategyStore } from '../../stores/strategyStore';
import { StrategyType, StrategyFormData } from '../../types/strategy';
import { ButtonSpinner } from '../ui/LoadingSpinner';

// Step components
import BasicInfoStep from './steps/BasicInfoStep';
import RulesConfigStep from './steps/RulesConfigStep';
import ConditionsStep from './steps/ConditionsStep';
import TransformationsStep from './steps/TransformationsStep';
import PreviewStep from './steps/PreviewStep';

interface StepConfig {
  id: number;
  title: string;
  description: string;
  component: React.ComponentType<any>;
  required: boolean;
}

const WIZARD_STEPS: StepConfig[] = [
  {
    id: 1,
    title: 'Basic Information',
    description: 'Strategy name, process, and tool configuration',
    component: BasicInfoStep,
    required: true
  },
  {
    id: 2,
    title: 'Rules Configuration',
    description: 'Define sampling rules and parameters',
    component: RulesConfigStep,
    required: true
  },
  {
    id: 3,
    title: 'Conditions',
    description: 'Set conditional logic and constraints',
    component: ConditionsStep,
    required: false
  },
  {
    id: 4,
    title: 'Transformations',
    description: 'Configure coordinate transformations',
    component: TransformationsStep,
    required: false
  },
  {
    id: 5,
    title: 'Preview & Validate',
    description: 'Review and test your strategy',
    component: PreviewStep,
    required: true
  }
];

export default function StrategyWizard() {
  const navigate = useNavigate();
  const {
    builderState,
    validationErrors,
    setBuilderStep,
    updateBuilderData,
    resetBuilder,
    validateBuilder,
    createStrategy,
    clearValidationErrors,
    runSimulation
  } = useStrategyStore();

  const [canProceed, setCanProceed] = useState(false);

  const currentStep = WIZARD_STEPS.find(step => step.id === builderState.current_step);
  const isLastStep = builderState.current_step === WIZARD_STEPS.length;
  const isFirstStep = builderState.current_step === 1;

  useEffect(() => {
    // Validate current step when form data changes
    validateCurrentStep();
  }, [builderState.form_data, builderState.current_step]);

  const validateCurrentStep = () => {
    switch (builderState.current_step) {
      case 1: // Basic Info
        const hasBasicInfo = !!(
          builderState.form_data.name &&
          builderState.form_data.process_step &&
          builderState.form_data.tool_type &&
          builderState.form_data.author
        );
        setCanProceed(hasBasicInfo);
        break;
      
      case 2: // Rules
        const hasRules = builderState.form_data.rules && builderState.form_data.rules.length > 0;
        setCanProceed(hasRules);
        break;
      
      case 3: // Conditions (optional)
      case 4: // Transformations (optional)
        setCanProceed(true);
        break;
      
      case 5: // Preview
        setCanProceed(validateBuilder());
        break;
      
      default:
        setCanProceed(false);
    }
  };

  const handleNext = () => {
    if (canProceed && !isLastStep) {
      setBuilderStep(builderState.current_step + 1);
    }
  };

  const handlePrevious = () => {
    if (!isFirstStep) {
      setBuilderStep(builderState.current_step - 1);
    }
  };

  const handleFinish = async () => {
    if (!validateBuilder()) {
      return;
    }

    // Clear any previous validation errors
    clearValidationErrors();

    try {
      const strategy = await createStrategy(builderState.form_data as StrategyFormData);
      resetBuilder();
      navigate('/strategies');
    } catch (error: any) {
      // Error handling is now managed by the store and API interceptor
      console.error('Strategy creation failed:', error);
    }
  };

  const handleCancel = () => {
    if (window.confirm('Are you sure you want to cancel? All changes will be lost.')) {
      resetBuilder();
      navigate('/strategies');
    }
  };

  const handleStepClick = (stepId: number) => {
    // Allow navigation to previous steps or current step
    if (stepId <= builderState.current_step) {
      setBuilderStep(stepId);
    }
  };

  const StepComponent = currentStep?.component;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Create New Strategy
              </h1>
              <p className="text-sm text-gray-500">
                {currentStep?.description}
              </p>
            </div>
            <button
              onClick={handleCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Step Navigation Sidebar */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-2">
              {WIZARD_STEPS.map((step, index) => {
                const isCurrent = step.id === builderState.current_step;
                const isCompleted = step.id < builderState.current_step;
                const isAccessible = step.id <= builderState.current_step;

                return (
                  <button
                    key={step.id}
                    onClick={() => handleStepClick(step.id)}
                    disabled={!isAccessible}
                    className={`
                      w-full text-left p-4 rounded-lg border transition-colors
                      ${isCurrent 
                        ? 'bg-blue-50 border-blue-200 text-blue-900' 
                        : isCompleted
                        ? 'bg-green-50 border-green-200 text-green-900 hover:bg-green-100'
                        : isAccessible
                        ? 'bg-white border-gray-200 text-gray-900 hover:bg-gray-50'
                        : 'bg-gray-50 border-gray-100 text-gray-400 cursor-not-allowed'
                      }
                    `}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`
                        w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                        ${isCurrent 
                          ? 'bg-blue-600 text-white' 
                          : isCompleted
                          ? 'bg-green-600 text-white'
                          : isAccessible
                          ? 'bg-gray-200 text-gray-600'
                          : 'bg-gray-100 text-gray-400'
                        }
                      `}>
                        {isCompleted ? (
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          step.id
                        )}
                      </div>
                      <div>
                        <div className="font-medium">{step.title}</div>
                        <div className="text-xs opacity-75">{step.description}</div>
                        {step.required && (
                          <div className="text-xs text-red-600 mt-1">Required</div>
                        )}
                      </div>
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              {/* Step Content */}
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {currentStep?.title}
                  </h2>
                  {currentStep?.required && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Required
                    </span>
                  )}
                </div>
                
                {StepComponent && (
                  <StepComponent
                    formData={builderState.form_data}
                    updateData={updateBuilderData}
                    validationErrors={builderState.validation_errors}
                  />
                )}
              </div>

              {/* Validation Errors */}
              {Object.keys(validationErrors).length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">
                        Please fix the following errors:
                      </h3>
                      <div className="mt-2 text-sm text-red-700">
                        {Object.entries(validationErrors).map(([field, errors]) => (
                          <div key={field} className="mb-1">
                            <strong className="capitalize">{field.replace('_', ' ')}:</strong> {errors.join(', ')}
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={clearValidationErrors}
                        className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Navigation Buttons */}
              <div className="flex items-center justify-between pt-6 border-t">
                <button
                  onClick={handlePrevious}
                  disabled={isFirstStep}
                  className={`
                    px-4 py-2 text-sm font-medium rounded-md
                    ${isFirstStep
                      ? 'text-gray-400 cursor-not-allowed'
                      : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  Previous
                </button>

                <div className="flex gap-3">
                  {isLastStep ? (
                    <button
                      onClick={handleFinish}
                      disabled={!canProceed || builderState.is_saving}
                      className={`
                        px-6 py-2 text-sm font-medium rounded-md
                        ${canProceed && !builderState.is_saving
                          ? 'bg-green-600 text-white hover:bg-green-700'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }
                      `}
                    >
                      {builderState.is_saving ? (
                        <ButtonSpinner variant="white" label="Creating..." />
                      ) : (
                        'Create Strategy'
                      )}
                    </button>
                  ) : (
                    <button
                      onClick={handleNext}
                      disabled={!canProceed}
                      className={`
                        px-6 py-2 text-sm font-medium rounded-md
                        ${canProceed
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }
                      `}
                    >
                      Next
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}