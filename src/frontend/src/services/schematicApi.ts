/**
 * Schematic API service for file upload and management.
 * Handles communication with backend schematic endpoints.
 */
import axios from 'axios';
import { SchematicPreview } from '../components/SchematicUpload/FilePreview';

// Create axios instance with same config as main API client
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
});

// Helper function to transform snake_case to camelCase
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

// Deep transform object keys from snake_case to camelCase
function transformKeys(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(transformKeys);
  } else if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((result, key) => {
      const camelKey = snakeToCamel(key);
      result[camelKey] = transformKeys(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
}

// Transform backend response to frontend format
function transformSchematicResponse(data: any): SchematicPreview {
  const transformed = transformKeys(data);
  
  // Ensure required fields have proper defaults
  return {
    id: transformed.id || '',
    filename: transformed.filename || '',
    fileSize: transformed.fileSize || 0,
    formatType: transformed.formatType || 'Unknown',
    uploadDate: transformed.uploadDate || new Date().toISOString(),
    dieCount: transformed.dieCount || 0,
    availableDieCount: transformed.availableDieCount || 0,
    waferSize: transformed.waferSize,
    layoutBounds: {
      width: transformed.layoutBounds?.width || 0,
      height: transformed.layoutBounds?.height || 0,
      xMin: transformed.layoutBounds?.xMin || 0,
      yMin: transformed.layoutBounds?.yMin || 0,
      xMax: transformed.layoutBounds?.xMax || 0,
      yMax: transformed.layoutBounds?.yMax || 0
    },
    coordinateSystem: transformed.coordinateSystem || 'center-origin',
    metadata: transformed.metadata || {}
  };
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export const schematicApi = {
  /**
   * Upload a schematic file to the backend.
   * @param file The file to upload
   * @param createdBy The user uploading the file
   * @param onProgress Progress callback
   * @returns The parsed schematic data
   */
  async upload(
    file: File,
    createdBy: string = 'user',
    onProgress?: (progress: UploadProgress) => void
  ): Promise<SchematicPreview> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post(
        `/api/v1/schematics/upload?created_by=${encodeURIComponent(createdBy)}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              onProgress({
                loaded: progressEvent.loaded,
                total: progressEvent.total,
                percentage
              });
            }
          }
        }
      );

      return transformSchematicResponse(response.data);
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 400) {
        const detail = error.response.data?.detail;
        if (detail?.includes('Unsupported file type')) {
          throw new Error('Unsupported file format. Please upload GDSII, DXF, or SVG files.');
        } else if (detail?.includes('File too large')) {
          throw new Error('File size exceeds 100MB limit.');
        } else if (detail?.includes('Failed to parse')) {
          throw new Error('Failed to parse schematic file. Please ensure the file is valid.');
        }
      } else if (error.response?.status === 413) {
        throw new Error('File size exceeds maximum allowed size of 100MB.');
      } else if (error.response?.status === 422) {
        throw new Error('Invalid file format or corrupted file.');
      }
      
      // Re-throw with more context
      throw new Error(error.response?.data?.detail || 'Failed to upload schematic file');
    }
  },

  /**
   * Get a specific schematic by ID.
   * @param id The schematic ID
   * @returns The schematic data
   */
  async get(id: string): Promise<SchematicPreview> {
    const response = await apiClient.get(`/api/v1/schematics/${id}`);
    return transformSchematicResponse(response.data);
  },

  /**
   * List all schematics.
   * @param filters Optional filters
   * @returns List of schematics
   */
  async list(filters?: { format_type?: string; created_by?: string }): Promise<SchematicPreview[]> {
    const params = new URLSearchParams();
    if (filters?.format_type) params.append('format_type', filters.format_type);
    if (filters?.created_by) params.append('created_by', filters.created_by);

    const response = await apiClient.get('/api/v1/schematics/', { params });
    return response.data.map(transformSchematicResponse);
  },

  /**
   * Delete a schematic by ID.
   * @param id The schematic ID
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/schematics/${id}`);
  }
};