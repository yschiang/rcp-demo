/**
 * Zustand store for strategy management state.
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  StrategyDefinition,
  StrategyListItem,
  StrategyFormData,
  SimulationResult,
  StrategyBuilderState,
  WaferMapViewState,
  StrategyType,
  StrategyLifecycle
} from '../types/strategy';
import { strategyApi } from '../services/api';

interface StrategyStore {
  // Strategy list state
  strategies: StrategyListItem[];
  loading: boolean;
  error: string | null;
  filters: {
    process_step?: string;
    tool_type?: string;
    lifecycle_state?: string;
  };

  // Current strategy state
  currentStrategy: StrategyDefinition | null;
  currentStrategyLoading: boolean;

  // Strategy builder state
  builderState: StrategyBuilderState;

  // Simulation state
  simulationResult: SimulationResult | null;
  simulationLoading: boolean;

  // Wafer map view state
  waferMapState: WaferMapViewState;

  // Actions
  loadStrategies: (filters?: typeof this.filters) => Promise<void>;
  loadStrategy: (id: string, version?: string) => Promise<void>;
  createStrategy: (data: StrategyFormData) => Promise<StrategyListItem>;
  updateStrategy: (id: string, data: Partial<StrategyFormData>) => Promise<void>;
  cloneStrategy: (id: string, newName: string, author: string) => Promise<void>;
  deleteStrategy: (id: string) => Promise<void>;
  promoteStrategy: (id: string, user: string) => Promise<void>;
  
  // Builder actions
  setBuilderStep: (step: number) => void;
  updateBuilderData: (data: Partial<StrategyFormData>) => void;
  resetBuilder: () => void;
  validateBuilder: () => boolean;
  
  // Simulation actions
  runSimulation: (strategyId: string, waferMapData: any, params?: any) => Promise<void>;
  clearSimulation: () => void;
  
  // Wafer map actions
  setWaferMapZoom: (zoom: number) => void;
  setWaferMapPan: (pan: {x: number, y: number}) => void;
  selectDies: (dies: any[]) => void;
  highlightDies: (dies: any[]) => void;
  toggleWaferMapOption: (option: 'show_grid' | 'show_coordinates') => void;
  
  // Utility actions
  setFilters: (filters: typeof this.filters) => void;
  clearError: () => void;
}

const initialBuilderState: StrategyBuilderState = {
  current_step: 1,
  form_data: {
    name: '',
    description: '',
    process_step: '',
    tool_type: '',
    strategy_type: StrategyType.CUSTOM,
    author: '',
    rules: []
  },
  validation_errors: {},
  is_saving: false
};

const initialWaferMapState: WaferMapViewState = {
  zoom: 1,
  pan: { x: 0, y: 0 },
  selected_dies: [],
  highlighted_dies: [],
  show_grid: true,
  show_coordinates: false
};

export const useStrategyStore = create<StrategyStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      strategies: [],
      loading: false,
      error: null,
      filters: {},
      currentStrategy: null,
      currentStrategyLoading: false,
      builderState: initialBuilderState,
      simulationResult: null,
      simulationLoading: false,
      waferMapState: initialWaferMapState,

      // Strategy list actions
      loadStrategies: async (filters = {}) => {
        set({ loading: true, error: null });
        try {
          const strategies = await strategyApi.list(filters);
          set({ strategies, filters, loading: false });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to load strategies',
            loading: false 
          });
        }
      },

      loadStrategy: async (id: string, version?: string) => {
        set({ currentStrategyLoading: true, error: null });
        try {
          const strategy = await strategyApi.get(id, version);
          set({ currentStrategy: strategy, currentStrategyLoading: false });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Failed to load strategy',
            currentStrategyLoading: false 
          });
        }
      },

      createStrategy: async (data: StrategyFormData) => {
        set((state) => ({
          builderState: { ...state.builderState, is_saving: true }
        }));
        
        try {
          const strategy = await strategyApi.create({
            name: data.name,
            description: data.description,
            process_step: data.process_step,
            tool_type: data.tool_type,
            strategy_type: data.strategy_type,
            author: data.author
          });
          
          // Reload strategies list
          await get().loadStrategies(get().filters);
          
          set((state) => ({
            builderState: { ...state.builderState, is_saving: false }
          }));
          
          return strategy;
        } catch (error: any) {
          set((state) => ({
            error: error.response?.data?.detail || 'Failed to create strategy',
            builderState: { ...state.builderState, is_saving: false }
          }));
          throw error;
        }
      },

      updateStrategy: async (id: string, data: Partial<StrategyFormData>) => {
        try {
          await strategyApi.update(id, data);
          await get().loadStrategy(id);
          await get().loadStrategies(get().filters);
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Failed to update strategy' });
          throw error;
        }
      },

      cloneStrategy: async (id: string, newName: string, author: string) => {
        try {
          await strategyApi.clone(id, newName, author);
          await get().loadStrategies(get().filters);
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Failed to clone strategy' });
          throw error;
        }
      },

      deleteStrategy: async (id: string) => {
        try {
          await strategyApi.delete(id);
          await get().loadStrategies(get().filters);
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Failed to delete strategy' });
          throw error;
        }
      },

      promoteStrategy: async (id: string, user: string) => {
        try {
          await strategyApi.promote(id, user);
          await get().loadStrategy(id);
          await get().loadStrategies(get().filters);
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Failed to promote strategy' });
          throw error;
        }
      },

      // Builder actions
      setBuilderStep: (step: number) => {
        set((state) => ({
          builderState: { ...state.builderState, current_step: step }
        }));
      },

      updateBuilderData: (data: Partial<StrategyFormData>) => {
        set((state) => ({
          builderState: {
            ...state.builderState,
            form_data: { ...state.builderState.form_data, ...data }
          }
        }));
      },

      resetBuilder: () => {
        set({ builderState: initialBuilderState });
      },

      validateBuilder: () => {
        const { form_data } = get().builderState;
        const errors: Record<string, string[]> = {};

        if (!form_data.name?.trim()) {
          errors.name = ['Name is required'];
        }
        if (!form_data.process_step?.trim()) {
          errors.process_step = ['Process step is required'];
        }
        if (!form_data.tool_type?.trim()) {
          errors.tool_type = ['Tool type is required'];
        }
        if (!form_data.author?.trim()) {
          errors.author = ['Author is required'];
        }

        set((state) => ({
          builderState: { ...state.builderState, validation_errors: errors }
        }));

        return Object.keys(errors).length === 0;
      },

      // Simulation actions
      runSimulation: async (strategyId: string, waferMapData: any, params = {}) => {
        set({ simulationLoading: true, error: null });
        try {
          const result = await strategyApi.simulate({
            strategy_id: strategyId,
            wafer_map_data: waferMapData,
            process_parameters: params.process_parameters || {},
            tool_constraints: params.tool_constraints || {}
          });
          
          set({ 
            simulationResult: result, 
            simulationLoading: false,
            waferMapState: {
              ...get().waferMapState,
              highlighted_dies: result.selected_points
            }
          });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Simulation failed',
            simulationLoading: false 
          });
        }
      },

      clearSimulation: () => {
        set({ simulationResult: null });
      },

      // Wafer map actions
      setWaferMapZoom: (zoom: number) => {
        set((state) => ({
          waferMapState: { ...state.waferMapState, zoom }
        }));
      },

      setWaferMapPan: (pan: {x: number, y: number}) => {
        set((state) => ({
          waferMapState: { ...state.waferMapState, pan }
        }));
      },

      selectDies: (dies: any[]) => {
        set((state) => ({
          waferMapState: { ...state.waferMapState, selected_dies: dies }
        }));
      },

      highlightDies: (dies: any[]) => {
        set((state) => ({
          waferMapState: { ...state.waferMapState, highlighted_dies: dies }
        }));
      },

      toggleWaferMapOption: (option: 'show_grid' | 'show_coordinates') => {
        set((state) => ({
          waferMapState: {
            ...state.waferMapState,
            [option]: !state.waferMapState[option]
          }
        }));
      },

      // Utility actions
      setFilters: (filters) => {
        set({ filters });
      },

      clearError: () => {
        set({ error: null });
      }
    }),
    {
      name: 'strategy-store'
    }
  )
);