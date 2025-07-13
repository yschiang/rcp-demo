/**
 * Zustand store for schematic data management.
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { SchematicPreview } from '../components/SchematicUpload/FilePreview';
import { UploadedFile } from '../components/SchematicUpload/FileUploadZone';

interface SchematicUploadState {
  files: UploadedFile[];
  uploadProgress: Record<string, number>;
  uploadErrors: Record<string, string>;
  isUploading: boolean;
}

interface SchematicVisualizationState {
  showOverlay: boolean;
  overlayOpacity: number;
  highlightMode: 'none' | 'boundaries' | 'dies' | 'layers';
  selectedLayer?: string;
}

interface SchematicStore {
  // Schematic data state
  schematics: SchematicPreview[];
  activeSchematics: SchematicPreview[];
  selectedSchematic: SchematicPreview | null;
  
  // Upload state
  uploadState: SchematicUploadState;
  
  // Visualization state
  visualizationState: SchematicVisualizationState;
  
  // Loading and error state
  loading: boolean;
  error: string | null;
  
  // Actions for schematic management
  addSchematic: (schematic: SchematicPreview) => void;
  removeSchematic: (schematicId: string) => void;
  selectSchematic: (schematicId: string | null) => void;
  updateSchematic: (schematicId: string, updates: Partial<SchematicPreview>) => void;
  
  // Actions for upload management
  addUploadFile: (file: UploadedFile) => void;
  updateUploadFile: (fileId: string, updates: Partial<UploadedFile>) => void;
  removeUploadFile: (fileId: string) => void;
  clearUploadFiles: () => void;
  setUploadProgress: (fileId: string, progress: number) => void;
  setUploadError: (fileId: string, error: string) => void;
  clearUploadError: (fileId: string) => void;
  
  // Actions for visualization settings
  setShowOverlay: (show: boolean) => void;
  setOverlayOpacity: (opacity: number) => void;
  setHighlightMode: (mode: 'none' | 'boundaries' | 'dies' | 'layers') => void;
  setSelectedLayer: (layer: string | null) => void;
  
  // Utility actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  resetState: () => void;
  
  // Integration actions
  getActiveSchematicForWaferMap: () => SchematicPreview | null;
  getSchematicById: (id: string) => SchematicPreview | null;
  getUploadFileById: (id: string) => UploadedFile | null;
  
  // Statistics and computed values
  getTotalSchematicDies: () => number;
  getAverageSchematicSize: () => number;
  getUploadStatistics: () => {
    totalFiles: number;
    completedFiles: number;
    failedFiles: number;
    uploadingFiles: number;
  };
}

const initialUploadState: SchematicUploadState = {
  files: [],
  uploadProgress: {},
  uploadErrors: {},
  isUploading: false
};

const initialVisualizationState: SchematicVisualizationState = {
  showOverlay: true,
  overlayOpacity: 0.6,
  highlightMode: 'boundaries',
  selectedLayer: undefined
};

export const useSchematicStore = create<SchematicStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      schematics: [],
      activeSchematics: [],
      selectedSchematic: null,
      uploadState: initialUploadState,
      visualizationState: initialVisualizationState,
      loading: false,
      error: null,

      // Schematic management actions
      addSchematic: (schematic: SchematicPreview) => {
        set((state) => ({
          schematics: [...state.schematics, schematic],
          activeSchematics: [...state.activeSchematics, schematic],
          selectedSchematic: schematic // Auto-select newly added schematic
        }));
      },

      removeSchematic: (schematicId: string) => {
        set((state) => ({
          schematics: state.schematics.filter(s => s.id !== schematicId),
          activeSchematics: state.activeSchematics.filter(s => s.id !== schematicId),
          selectedSchematic: state.selectedSchematic?.id === schematicId ? null : state.selectedSchematic
        }));
      },

      selectSchematic: (schematicId: string | null) => {
        const schematic = schematicId ? get().getSchematicById(schematicId) : null;
        set({ selectedSchematic: schematic });
      },

      updateSchematic: (schematicId: string, updates: Partial<SchematicPreview>) => {
        set((state) => ({
          schematics: state.schematics.map(s => 
            s.id === schematicId ? { ...s, ...updates } : s
          ),
          activeSchematics: state.activeSchematics.map(s => 
            s.id === schematicId ? { ...s, ...updates } : s
          ),
          selectedSchematic: state.selectedSchematic?.id === schematicId 
            ? { ...state.selectedSchematic, ...updates } 
            : state.selectedSchematic
        }));
      },

      // Upload management actions
      addUploadFile: (file: UploadedFile) => {
        set((state) => ({
          uploadState: {
            ...state.uploadState,
            files: [...state.uploadState.files, file],
            isUploading: true
          }
        }));
      },

      updateUploadFile: (fileId: string, updates: Partial<UploadedFile>) => {
        set((state) => ({
          uploadState: {
            ...state.uploadState,
            files: state.uploadState.files.map(f => 
              f.id === fileId ? { ...f, ...updates } : f
            )
          }
        }));
      },

      removeUploadFile: (fileId: string) => {
        set((state) => {
          const newFiles = state.uploadState.files.filter(f => f.id !== fileId);
          const { [fileId]: removedProgress, ...restProgress } = state.uploadState.uploadProgress;
          const { [fileId]: removedError, ...restErrors } = state.uploadState.uploadErrors;
          
          return {
            uploadState: {
              ...state.uploadState,
              files: newFiles,
              uploadProgress: restProgress,
              uploadErrors: restErrors,
              isUploading: newFiles.some(f => f.status === 'uploading' || f.status === 'parsing')
            }
          };
        });
      },

      clearUploadFiles: () => {
        set((state) => ({
          uploadState: {
            ...initialUploadState
          }
        }));
      },

      setUploadProgress: (fileId: string, progress: number) => {
        set((state) => ({
          uploadState: {
            ...state.uploadState,
            uploadProgress: {
              ...state.uploadState.uploadProgress,
              [fileId]: progress
            }
          }
        }));
      },

      setUploadError: (fileId: string, error: string) => {
        set((state) => ({
          uploadState: {
            ...state.uploadState,
            uploadErrors: {
              ...state.uploadState.uploadErrors,
              [fileId]: error
            }
          }
        }));
      },

      clearUploadError: (fileId: string) => {
        set((state) => {
          const { [fileId]: removedError, ...restErrors } = state.uploadState.uploadErrors;
          return {
            uploadState: {
              ...state.uploadState,
              uploadErrors: restErrors
            }
          };
        });
      },

      // Visualization settings actions
      setShowOverlay: (show: boolean) => {
        set((state) => ({
          visualizationState: {
            ...state.visualizationState,
            showOverlay: show
          }
        }));
      },

      setOverlayOpacity: (opacity: number) => {
        set((state) => ({
          visualizationState: {
            ...state.visualizationState,
            overlayOpacity: Math.max(0, Math.min(1, opacity))
          }
        }));
      },

      setHighlightMode: (mode: 'none' | 'boundaries' | 'dies' | 'layers') => {
        set((state) => ({
          visualizationState: {
            ...state.visualizationState,
            highlightMode: mode
          }
        }));
      },

      setSelectedLayer: (layer: string | null) => {
        set((state) => ({
          visualizationState: {
            ...state.visualizationState,
            selectedLayer: layer || undefined
          }
        }));
      },

      // Utility actions
      setLoading: (loading: boolean) => {
        set({ loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },

      resetState: () => {
        set({
          schematics: [],
          activeSchematics: [],
          selectedSchematic: null,
          uploadState: initialUploadState,
          visualizationState: initialVisualizationState,
          loading: false,
          error: null
        });
      },

      // Integration actions
      getActiveSchematicForWaferMap: () => {
        const state = get();
        return state.selectedSchematic || 
               (state.activeSchematics.length > 0 ? state.activeSchematics[0] : null);
      },

      getSchematicById: (id: string) => {
        return get().schematics.find(s => s.id === id) || null;
      },

      getUploadFileById: (id: string) => {
        return get().uploadState.files.find(f => f.id === id) || null;
      },

      // Statistics and computed values
      getTotalSchematicDies: () => {
        return get().activeSchematics.reduce((total, schematic) => 
          total + schematic.dieCount, 0
        );
      },

      getAverageSchematicSize: () => {
        const schematics = get().activeSchematics;
        if (schematics.length === 0) return 0;
        
        const totalSize = schematics.reduce((total, schematic) => 
          total + (schematic.layoutBounds.width * schematic.layoutBounds.height), 0
        );
        
        return totalSize / schematics.length;
      },

      getUploadStatistics: () => {
        const files = get().uploadState.files;
        return {
          totalFiles: files.length,
          completedFiles: files.filter(f => f.status === 'completed').length,
          failedFiles: files.filter(f => f.status === 'error').length,
          uploadingFiles: files.filter(f => f.status === 'uploading' || f.status === 'parsing').length
        };
      }
    }),
    {
      name: 'schematic-store'
    }
  )
);