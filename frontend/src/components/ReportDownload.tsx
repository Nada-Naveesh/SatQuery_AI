import React from 'react';
import { getPdfReportUrl } from '../api/client';

interface ReportDownloadProps {
  traceId?: string;
}

export const ReportDownload: React.FC<ReportDownloadProps> = ({ traceId }) => {
  const handleDownload = () => {
    if (!traceId) return;
    const url = getPdfReportUrl(traceId);
    window.open(url, '_blank');
  };

  return (
    <button
      onClick={handleDownload}
      disabled={!traceId}
      className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-medium px-3.5 py-2 rounded-lg transition shadow-md"
    >
      <span>Download Mission PDF</span>
    </button>
  );
};
