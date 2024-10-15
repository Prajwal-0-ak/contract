"use client";

import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import * as XLSX from "xlsx";
import { Separator } from "@/components/ui/separator";
import PDFViewer from "@/components/PDFViewer";
import ContractForm from "@/components/ContractForm";
import FileUpload from "@/components/FileUpload";
import ContractDataTable from "@/components/ContractDataTable";

interface ExtractedDataItem {
  field: string;
  value: string;
  page_num: string;
}

interface ApiData {
  client_company_name: string;
  currency: string;
  sow_start_date: string;
  sow_end_date: string;
  sow_no: string;
  sow_value: string;
  cola: string;
  credit_period: string;
  inclusive_or_exclusive_gst: string;
  type_of_billing: string;
  po_number: string;
  amendment_no: string;
}

export default function ContractPage() {
  const [formData, setFormData] = useState({
    remark: "",
    subContractClause: "",
  });

  const [apiData, setApiData] = useState<ApiData>({
    client_company_name: "",
    currency: "",
    sow_start_date: "",
    sow_end_date: "",
    sow_no: "",
    sow_value: "",
    cola: "",
    credit_period: "",
    inclusive_or_exclusive_gst: "",
    type_of_billing: "",
    po_number: "",
    amendment_no: "",
  });

  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [excelFile, setExcelFile] = useState<Blob | null>(null);
  const [pdfType, setPdfType] = useState("SOW");
  const [fieldPageMapping, setFieldPageMapping] = useState<Record<string, string>>({});
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [showPdfViewer, setShowPdfViewer] = useState(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [editingField, setEditingField] = useState<{ name: string; value: string; page: number; } | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const closeDialogRef = useRef<HTMLButtonElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPdfFile(selectedFile);
      setShowPdfViewer(true);
    }
  };

  const handlePdfTypeChange = (value: string) => {
    setPdfType(value);
  };

  const handleFileUpload = async () => {
    if (file) {
      setIsUploading(true);
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("pdfType", pdfType);

        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Response from server:", result);

        const extractedData = result.extracted_data as ExtractedDataItem[];
        const newApiData: ApiData = { ...apiData };
        const newFieldPageMapping: Record<string, string> = {};

        extractedData.forEach((item) => {
          if (item.field in newApiData) {
            newApiData[item.field as keyof ApiData] = item.value;
            newFieldPageMapping[item.field] = item.page_num;
          }
        });

        setApiData(newApiData);
        setFieldPageMapping(newFieldPageMapping);

        const allData = { ...formData, ...newApiData };
        const ws = XLSX.utils.json_to_sheet([allData]);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Contract Data");

        const excelBlob = new Blob(
          [XLSX.write(wb, { bookType: "xlsx", type: "array" })],
          { type: "application/octet-stream" }
        );
        setExcelFile(excelBlob);

        setIsDownloadReady(true);
        toast.success("File uploaded successfully");
      } catch (error) {
        console.error("Error uploading file:", error);
        if (error instanceof TypeError && error.message.includes("NetworkError")) {
          toast.error("Network error. Please check your connection and try again.");
        } else {
          toast.error(`An error occurred while uploading the file: ${(error as Error).message || "Unknown error"}`);
        }
      } finally {
        setIsUploading(false);
      }
    }
  };

  const handleDownload = () => {
    if (excelFile) {
      const url = URL.createObjectURL(excelFile);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "Contract_Report.xlsx");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success("Excel file downloaded successfully");
    }
  };

  const handleEditField = (field: { name: string; value: string; page: number }) => {
    setEditingField(field);
    setIsDialogOpen(true);
  };

  const handleSaveEdit = (name: string, newValue: string, newPage: string) => {
    if (!newValue.trim() || !newPage.trim()) {
      toast.error("Please fill in both value and page number.");
      return;
    }

    const pageNumber = parseInt(newPage, 10);
    if (isNaN(pageNumber) || pageNumber < 1) {
      toast.error("Please enter a valid page number.");
      return;
    }

    if (name in apiData) {
      setApiData((prev) => ({ ...prev, [name]: newValue }));
    } else if (name in formData) {
      setFormData((prev) => ({ ...prev, [name]: newValue }));
    }
    setFieldPageMapping((prev) => ({ ...prev, [name]: pageNumber.toString() }));
    setEditingField(null);
    setIsDialogOpen(false);
    closeDialogRef.current?.click();
    toast.success("Field updated successfully");
  };

  const handleFieldClick = (page: number) => {
    setCurrentPage(page);
  };

  const fields = [
    { name: "remark", page: 0, value: formData.remark },
    { name: "subContractClause", page: 0, value: formData.subContractClause },
    ...Object.entries(apiData).map(([field, value]) => ({
      name: field,
      page: parseInt(fieldPageMapping[field] || "0", 10),
      value: value || "",
    })),
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">
                  Contract Management
                </h1>
              </div>
            </div>
            <div className="flex items-center">
              <Button onClick={() => router.push("/chat")}>Chat</Button>
            </div>
          </div>
        </div>
      </nav> */}

      <main className="max-w-8xl mx-auto py-3 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <div className="flex flex-col lg:flex-row">
            <div
              className={`w-full ${
                showPdfViewer ? "lg:w-1/2" : ""
              } bg-white shadow overflow-hidden sm:rounded-lg mb-6 lg:mb-0 ${
                showPdfViewer ? "lg:mr-4" : ""
              }`}
            >
              <div className="px-4 py-5 sm:p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  Contract Form
                </h2>

                <ContractForm formData={formData} handleInputChange={handleInputChange} />

                <FileUpload
                  handleFileChange={handleFileChange}
                  pdfType={pdfType}
                  handlePdfTypeChange={handlePdfTypeChange}
                  handleFileUpload={handleFileUpload}
                  file={file}
                  isUploading={isUploading}
                />

                <Separator className="my-8" />

                <ContractDataTable
                  fields={fields}
                  handleEditField={handleEditField}
                  handleSaveEdit={handleSaveEdit}
                  editingField={editingField}
                  setEditingField={setEditingField}
                  isDialogOpen={isDialogOpen}
                  setIsDialogOpen={setIsDialogOpen}
                  closeDialogRef={closeDialogRef}
                  onFieldClick={handleFieldClick}
                />

                {isDownloadReady && (
                  <div className="mt-8">
                    <Button onClick={handleDownload}>Download Excel</Button>
                  </div>
                )}
              </div>
            </div>

            {showPdfViewer && (
              <div className="w-full lg:w-1/2">
                <PDFViewer
                  file={pdfFile}
                  currentPage={currentPage}
                  setCurrentPage={setCurrentPage}
                />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}