"use client";

import React, { useState, useEffect, useRef } from 'react';
import { getDocument, GlobalWorkerOptions, PDFDocumentProxy } from 'pdfjs-dist';
import { Button } from "@/components/ui/button";

GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

interface PDFViewerProps {
  file: File | null;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ file }) => {
  const [pdfDoc, setPdfDoc] = useState<PDFDocumentProxy | null>(null);
  const [pageNum, setPageNum] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.5);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState<boolean>(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const data = e.target?.result as ArrayBuffer;
        try {
          const loadingTask = getDocument({ data });
          const pdf = await loadingTask.promise;
          setPdfDoc(pdf);
          setTotalPages(pdf.numPages);
          setPageNum(1);
        } catch (err) {
          setError('Error loading PDF: ' + (err as Error).message);
        }
      };
      reader.readAsArrayBuffer(file);
    }
  }, [file]);

  useEffect(() => {
    if (pdfDoc) {
      renderPage();
    }
  }, [pdfDoc, pageNum, scale]);

  const renderPage = async () => {
    if (isRendering || !pdfDoc || !canvasRef.current) return;
    setIsRendering(true);

    try {
      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale });
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (context) {
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        await page.render({ canvasContext: context, viewport }).promise;
      }
    } catch (err) {
      setError('Error rendering page: ' + (err as Error).message);
    } finally {
      setIsRendering(false);
    }
  };

  const handlePrevPage = () => pageNum > 1 && setPageNum(pageNum - 1);
  const handleNextPage = () => pageNum < totalPages && setPageNum(pageNum + 1);
  const handleZoomIn = () => setScale(scale + 0.25);
  const handleZoomOut = () => scale > 0.5 && setScale(scale - 0.25);

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg p-4">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">PDF Viewer</h2>
      {error && <div className="text-red-500 mb-4">{error}</div>}
      <div className="flex justify-between items-center mb-4">
        <div>
          <Button onClick={handlePrevPage} disabled={pageNum === 1 || isRendering} className="mr-2">
            Previous
          </Button>
          <Button onClick={handleNextPage} disabled={pageNum === totalPages || isRendering}>
            Next
          </Button>
        </div>
        <span className="text-gray-700">
          Page {pageNum} of {totalPages}
        </span>
        <div>
          <Button onClick={handleZoomOut} disabled={scale <= 0.5} className="mr-2">
            Zoom Out
          </Button>
          <Button onClick={handleZoomIn}>
            Zoom In
          </Button>
        </div>
      </div>
      <div className="border border-gray-300 rounded-lg overflow-auto">
        <canvas ref={canvasRef} className="mx-auto"></canvas>
      </div>
    </div>
  );
};

export default PDFViewer;