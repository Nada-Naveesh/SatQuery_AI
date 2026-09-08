import React, { useState } from 'react';
import { VisualEvidence } from '../types';

interface ImageViewerProps {
  baseImageUrl: string;
  visualEvidence?: VisualEvidence;
  detectedTask?: string;
  dimensions?: number[];
  resolutionM?: number;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  baseImageUrl,
  visualEvidence,
  detectedTask,
  dimensions = [512, 512],
  resolutionM = 10.0,
}) => {
  const [viewMode, setViewMode] = useState<'base' | 'overlay' | 'split'>('base');

  return (
    <div className="border border-space-700 bg-space-800 rounded-xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Satellite Viewport
          </span>
          {detectedTask && (
            <span className="text-[10px] px-2 py-0.5 rounded font-mono font-medium bg-cyan-950 text-cyan-400 border border-cyan-800">
              Task: {detectedTask.toUpperCase().replace('_', ' ')}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-1 bg-space-900 p-1 rounded-md border border-space-700 text-xs">
          <button
            onClick={() => setViewMode('base')}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition ${
              viewMode === 'base' ? 'bg-space-700 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Base
          </button>
          <button
            onClick={() => setViewMode('overlay')}
            disabled={!visualEvidence?.overlay_base64}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition disabled:opacity-30 ${
              viewMode === 'overlay' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Evidence Overlay
          </button>
          <button
            onClick={() => setViewMode('split')}
            disabled={!visualEvidence?.overlay_base64}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition disabled:opacity-30 ${
              viewMode === 'split' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Split Comparison
          </button>
        </div>
      </div>

      <div className="relative w-full h-80 bg-black/60 rounded-lg border border-space-700 overflow-hidden flex items-center justify-center">
        {/* Base Image */}
        {baseImageUrl && (
          <img
            src={baseImageUrl}
            alt="Base Satellite Layer"
            className="absolute inset-0 w-full h-full object-contain"
          />
        )}

        {/* Evidence Overlay */}
        {viewMode === 'overlay' && visualEvidence?.overlay_base64 && (
          <img
            src={visualEvidence.overlay_base64}
            alt="Evidence Overlay Mask"
            className="absolute inset-0 w-full h-full object-contain opacity-95 transition-opacity"
          />
        )}

        {/* Split View */}
        {viewMode === 'split' && visualEvidence?.overlay_base64 && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-0 overflow-hidden w-1/2 border-r-2 border-cyan-400 shadow-2xl">
              <img
                src={visualEvidence.overlay_base64}
                alt="Split Comparison"
                className="absolute inset-0 w-full h-full object-contain max-w-none"
              />
            </div>
          </div>
        )}
      </div>

      <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 px-1">
        <span>Dimensions: {dimensions[0]} x {dimensions[1]} px</span>
        <span>CRS: EPSG:4326 &bull; GSD: {resolutionM}m</span>
      </div>
    </div>
  );
};
