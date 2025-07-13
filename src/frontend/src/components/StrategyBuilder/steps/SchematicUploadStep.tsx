/**
 * Schematic upload step component for strategy wizard.
 * Handles file upload, processing, and preview with validation.
 */
import React, { useState, useCallback } from 'react';
import FileUploadZone, { UploadedFile } from '../../SchematicUpload/FileUploadZone';
import UploadProgress from '../../SchematicUpload/UploadProgress';
import FilePreview, { SchematicPreview } from '../../SchematicUpload/FilePreview';
import { showError, showSuccess } from '../../../services/toastService';
import { useSchematicStore } from '../../../stores/schematicStore';
import { StrategyFormData } from '../../../types/strategy';
import { schematicApi } from '../../../services/schematicApi';

interface SchematicUploadStepProps {
  formData: Partial<StrategyFormData>;
  updateData: (data: Partial<StrategyFormData>) => void;
  validationErrors: Record<string, string[]>;
  onSchematicUploaded?: (schematic: SchematicPreview) => void;
}

export default function SchematicUploadStep({
  formData,
  updateData,
  validationErrors,
  onSchematicUploaded
}: SchematicUploadStepProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Use schematic store for state management
  const {
    uploadState,
    schematics,
    addUploadFile,
    updateUploadFile,
    removeUploadFile,
    addSchematic,
    removeSchematic,
    setUploadProgress,
    setUploadError,
    getUploadStatistics
  } = useSchematicStore();

  // Generate unique ID for files
  const generateFileId = (): string => {
    return `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  // Handle file selection from upload zone
  const handleFilesSelected = useCallback(async (files: File[]) => {
    const newUploadedFiles: UploadedFile[] = files.map(file => ({
      ...file,
      id: generateFileId(),
      progress: 0,
      status: 'pending' as const
    }));

    // Add files to store
    newUploadedFiles.forEach(file => addUploadFile(file));
    setIsProcessing(true);

    // Process each file sequentially
    for (const uploadedFile of newUploadedFiles) {
      try {
        // Update status to uploading
        updateUploadFile(uploadedFile.id, { status: 'uploading' });

        // Upload file with real API
        const schematicPreview = await schematicApi.upload(
          uploadedFile,
          formData.author || 'user',
          (progress) => {
            // Update progress in real-time
            updateUploadFile(uploadedFile.id, { 
              progress: progress.percentage,
              status: 'uploading'
            });
          }
        );

        // Update to completed status
        updateUploadFile(uploadedFile.id, { 
          status: 'completed',
          progress: 100
        });

        // Add to schematic store
        addSchematic(schematicPreview);
        
        // Notify parent component
        if (onSchematicUploaded) {
          onSchematicUploaded(schematicPreview);
        }

        showSuccess(`Successfully uploaded and parsed ${uploadedFile.name}`);

      } catch (error) {
        // Update to error status
        const errorMessage = error instanceof Error ? error.message : 'Upload failed';
        updateUploadFile(uploadedFile.id, { 
          status: 'error',
          error: errorMessage 
        });
        setUploadError(uploadedFile.id, errorMessage);
        
        showError(`Failed to upload ${uploadedFile.name}: ${errorMessage}`);
      }
    }

    setIsProcessing(false);
  }, [addUploadFile, updateUploadFile, addSchematic, setUploadError, onSchematicUploaded, formData.author]);

  // Handle file actions
  const handleCancelUpload = useCallback((fileId: string) => {
    removeUploadFile(fileId);
  }, [removeUploadFile]);

  const handleRemoveFile = useCallback((fileId: string) => {
    removeUploadFile(fileId);
    // Also remove from schematics if it exists
    const schematic = schematics.find(s => s.id === fileId);
    if (schematic) {
      removeSchematic(fileId);
    }
  }, [removeUploadFile, removeSchematic, schematics]);

  const handleRetryUpload = useCallback(async (fileId: string) => {
    const fileToRetry = uploadState.files.find(f => f.id === fileId);
    if (!fileToRetry) return;

    // Reset file status and retry
    updateUploadFile(fileId, { 
      status: 'uploading',
      progress: 0,
      error: undefined 
    });

    try {
      // Upload file with real API
      const schematicPreview = await schematicApi.upload(
        fileToRetry,
        formData.author || 'user',
        (progress) => {
          // Update progress in real-time
          updateUploadFile(fileId, { 
            progress: progress.percentage,
            status: 'uploading'
          });
        }
      );

      // Update to completed status
      updateUploadFile(fileId, { 
        status: 'completed',
        progress: 100
      });

      // Add to schematic store
      addSchematic(schematicPreview);
      
      // Notify parent component
      if (onSchematicUploaded) {
        onSchematicUploaded(schematicPreview);
      }

      showSuccess(`Successfully uploaded and parsed ${fileToRetry.name}`);

    } catch (error) {
      // Update to error status
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      updateUploadFile(fileId, { 
        status: 'error',
        error: errorMessage 
      });
      setUploadError(fileId, errorMessage);
      
      showError(`Failed to retry upload ${fileToRetry.name}: ${errorMessage}`);
    }
  }, [uploadState.files, updateUploadFile, addSchematic, setUploadError, onSchematicUploaded, formData.author]);

  const handleRemovePreview = useCallback((previewId: string) => {
    removeSchematic(previewId);
    removeUploadFile(previewId);
  }, [removeSchematic, removeUploadFile]);

  const handleValidateSchematic = useCallback((preview: SchematicPreview) => {
    // TODO: Implement schematic validation logic
    showSuccess(`Validation started for ${preview.filename}`);
  }, []);

  // Check if we can proceed to next step
  const canProceed = schematics.length > 0 && !isProcessing;

  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Upload Schematic Files
        </h2>
        <p className="text-gray-600">
          Upload schematic files (GDSII, DXF, SVG) to define die boundaries and layout information 
          for your wafer sampling strategy.
        </p>
      </div>

      {/* File Upload Zone */}
      <FileUploadZone
        onFilesSelected={handleFilesSelected}
        multiple={false}
        disabled={isProcessing}
        className="mb-6"
      />

      {/* Upload Progress */}
      <UploadProgress
        files={uploadState.files}
        onCancel={handleCancelUpload}
        onRemove={handleRemoveFile}
        onRetry={handleRetryUpload}
      />

      {/* Schematic Previews */}
      {schematics.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">
            Uploaded Schematics ({schematics.length})
          </h3>
          <div className="space-y-4">
            {schematics.map((preview) => (
              <FilePreview
                key={preview.id}
                preview={preview}
                onRemove={() => handleRemovePreview(preview.id)}
                onValidate={() => handleValidateSchematic(preview)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Status Summary */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
        <div className="text-sm text-gray-600">
          {schematics.length === 0 ? (
            <div className="flex items-center text-orange-600">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              No schematic uploaded (this step is optional)
            </div>
          ) : (
            <div className="flex items-center text-green-600">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              {schematics.length} schematic{schematics.length > 1 ? 's' : ''} ready for use in strategy
            </div>
          )}
        </div>
        {isProcessing && (
          <div className="text-sm text-blue-600 mt-2">
            Processing uploads... Please wait before proceeding to the next step.
          </div>
        )}
      </div>
    </div>
  );
}