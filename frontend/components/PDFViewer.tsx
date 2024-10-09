"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { PDFDocumentProxy, PDFDocumentLoadingTask, GlobalWorkerOptions } from 'pdfjs-dist';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from "@/components/ui/table";
import { toast } from "sonner";

// Use a type for the dynamic import
type PDFJSType = typeof import('pdfjs-dist');
let pdfjsLib: PDFJSType;

if (typeof window !== "undefined") {
  // Use dynamic import for pdfjs-dist
  import('pdfjs-dist').then((pdfjs: PDFJSType) => {
    pdfjsLib = pdfjs;
    pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';
  });
}

interface PDFViewerProps {
  file: File | null;
  currentPage: number;
  setCurrentPage: (page: number) => void;
  fields: { name: string; page: number; value: string }[];
}

const PDFViewer: React.FC<PDFViewerProps> = ({ file, currentPage, setCurrentPage, fields }) => {
  const [pdfDoc, setPdfDoc] = useState<PDFDocumentProxy | null>(null);
  const [scale, setScale] = useState<number>(1.25); // Reduced default size
  const [totalPages, setTotalPages] = useState<number>(0);
  const [isRendering, setIsRendering] = useState<boolean>(false);
  const [searchPage, setSearchPage] = useState<string>('');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (file && pdfjsLib) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const data = e.target?.result as ArrayBuffer;
        try {
          const loadingTask: PDFDocumentLoadingTask = pdfjsLib.getDocument({ data });
          const pdf = await loadingTask.promise;
          setPdfDoc(pdf);
          setTotalPages(pdf.numPages);
          setCurrentPage(1);
        } catch (err) {
          console.error('Error loading PDF:', err);
          toast.error('Error loading PDF. Please try again.');
        }
      };
      reader.readAsArrayBuffer(file);
    }
  }, [file, setCurrentPage]);

  const renderPage = useCallback(async () => {
    if (isRendering || !pdfDoc || !canvasRef.current) return;
    setIsRendering(true);

    try {
      const page = await pdfDoc.getPage(currentPage);
      const viewport = page.getViewport({ scale });
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (context) {
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        await page.render({ canvasContext: context, viewport }).promise;
      }
    } catch (err) {
      console.error('Error rendering page:', err);
      if (err instanceof Error && err.message.includes('Invalid page request')) {
        setCurrentPage(1);
      }
    } finally {
      setIsRendering(false);
    }
  }, [pdfDoc, currentPage, scale, setCurrentPage, isRendering]);

  useEffect(() => {
    if (pdfDoc) {
      renderPage();
    }
  }, [pdfDoc, currentPage, scale, renderPage]);

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };
  
  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };
  
  const handleZoomIn = () => setScale(scale + 0.25);
  
  const handleZoomOut = () => {
    if (scale > 0.5) {
      setScale(scale - 0.25);
    }
  };

  const handleSearchPageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchPage(e.target.value);
  };

  const handlePageSearch = () => {
    const pageNumber = parseInt(searchPage, 10);
    if (!isNaN(pageNumber) && pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
      setSearchPage('');
    } else {
      toast.error(`Please enter a valid page number between 1 and ${totalPages}`);
    }
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg p-4">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">PDF Viewer</h2>

      <div className="flex mb-4">
        <Input
          type="number"
          min="1"
          max={totalPages}
          value={searchPage}
          onChange={handleSearchPageChange}
          className="border p-2 mr-2 w-24"
          placeholder={`Page (1-${totalPages})`}
          style={{ appearance: 'textfield' }} // Removes the spinner arrows
        />
        <Button onClick={handlePageSearch} disabled={isRendering || searchPage === ''}>
          Go
        </Button>
      </div>

      <div className="flex justify-between items-center mb-4">
        <div>
          <Button onClick={handlePrevPage} disabled={currentPage === 1 || isRendering} className="mr-2">
            Previous
          </Button>
          <Button onClick={handleNextPage} disabled={currentPage === totalPages || isRendering}>
            Next
          </Button>
        </div>
        <span className="text-gray-700">
          Page {currentPage} of {totalPages}
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

      {fields.length > 0 && (
        <div className="mt-4">
          <h3 className="text-xl font-semibold mb-2">Fields on Page {currentPage}</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Field Name</TableHead>
                <TableHead>Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {fields
                .filter(field => field.page === currentPage)
                .map((field, index) => (
                  <TableRow key={index} className="cursor-default">
                    <TableCell>{field.name}</TableCell>
                    <TableCell>{field.value}</TableCell>
                  </TableRow>
                ))
              }
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default PDFViewer;