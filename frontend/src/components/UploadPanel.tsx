import React, { useRef } from 'react';

interface UploadPanelProps {
  onFilesSelected: (files: File[]) => void;
  selectedFiles: File[];
  activeScenarioId: string | null;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({
  onFilesSelected,
  selectedFiles,
  activeScenarioId,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFilesSelected(Array.from(e.target.files));
    }
  };

  return (
    <div className="border border-space-700 bg-space-800 rounded-xl p-4 shadow-sm">
      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
        Satellite Imagery Upload
      </h3>

      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-space-600 hover:border-cyan-500 rounded-lg p-4 text-center cursor-pointer transition bg-space-900/40"
      >
        <input
          type="file"
          ref={fileInputRef}
          multiple
          accept=".tif,.tiff,.png,.jpg,.jpeg"
          className="hidden"
          onChange={handleChange}
        />
        <p className="text-xs font-medium text-slate-200">
          {selectedFiles.length > 0
            ? `${selectedFiles.length} file(s) loaded: ${selectedFiles.map((f) => f.name).join(', ')}`
            : activeScenarioId
            ? `Scenario active: ${activeScenarioId}`
            : 'Drop 1 or 2 satellite scenes (GeoTIFF / PNG)'}
        </p>
        <p className="text-[10px] text-slate-500 mt-1">
          Supports Single optical/SAR, Bi-temporal pairs, or Co-registered Optical-SAR pairs
        </p>
      </div>
    </div>
  );
};
