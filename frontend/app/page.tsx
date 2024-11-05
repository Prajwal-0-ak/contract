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

type ApiData = Record<string, string>;

interface ExtractedDataItem {
  field: string;
  value: string;
  page_num: string;
}

export default function ContractPage() {
  const [formData, setFormData] = useState({
    remark: "",
    subContractClause: "",
  });

  const [apiData, setApiData] = useState<ApiData>({});
  const [fieldPageMapping, setFieldPageMapping] = useState<Record<string, string>>({});

  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [excelFile, setExcelFile] = useState<Blob | null>(null);
  const [pdfType, setPdfType] = useState("SOW");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [showPdfViewer, setShowPdfViewer] = useState(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [editingField, setEditingField] = useState<{ name: string; value: string; page: number } | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const closeDialogRef = useRef<HTMLButtonElement>(null);

  const sowFields = [
    "client_company_name",
    "currency",
    "sow_start_date",
    "sow_end_date",
    "cola",
    "credit_period",
    "inclusive_or_exclusive_gst",
    "sow_value",
    "sow_no",
    "type_of_billing",
    "po_number",
    "amendment_no",
    "billing_unit_type_and_rate_cost",
    "particular_role_rate",
  ];

  const msaFields = [
    "client_company_name",
    "currency",
    "msa_start_date",
    "msa_end_date",
    "info_security",
    "limitation_of_liability",
    "data_processing_agreement",
    "insurance_required",
    "type_of_insurance_required",
    "is_cyber_insurance_required",
    "cyber_insurance_amount",
    "is_workman_compensation_insurance_required",
    "workman_compensation_insurance_amount",
    "other_insurance_required",
    "other_insurance_amount"
  ];

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
      setIsDownloadReady(false);
      setApiData({});
      setFieldPageMapping({});
    }
  };

  const handlePdfTypeChange = (value: string) => {
    setPdfType(value);
    setApiData({});
    setFieldPageMapping({});
  };

  const handleFileUpload = async () => {
    if (file) {
      setIsUploading(true);
      try {
        const uploadFormData = new FormData();
        uploadFormData.append("file", file);
        uploadFormData.append("pdfType", pdfType);

        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: uploadFormData,
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Response from server:", result);

        const extractedData = result.extracted_data as ExtractedDataItem[];
        const newApiData: ApiData = {};
        const newFieldPageMapping: Record<string, string> = {};

        extractedData.forEach((item) => {
          newApiData[item.field] = item.value || "";
          newFieldPageMapping[item.field] = item.page_num;
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

    if (sowFields.includes(name) || msaFields.includes(name)) {
      setApiData((prev) => ({ ...prev, [name]: newValue }));
    } else {
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

  const closePdfViewer = () => {
    setShowPdfViewer(false);
  };

  const fields = [
    { name: "remark", page: 0, value: formData.remark },
    { name: "subContractClause", page: 0, value: formData.subContractClause },
    ...((pdfType === "SOW" ? sowFields : msaFields).map((field) => ({
      name: field,
      page: parseInt(fieldPageMapping[field] || "0", 10),
      value: apiData[field] || "",
    }))),
  ];

  return (
    <div className="min-h-screen bg-gray-100">
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

                {fields.length > 2 && (
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
                )}

                {isDownloadReady && (
                  <div className="mt-8">
                    <Button onClick={handleDownload}>Download Excel</Button>
                  </div>
                )}
              </div>
            </div>

            {showPdfViewer && pdfFile && (
              <div className="w-full lg:w-1/2">
                <PDFViewer
                  file={pdfFile}
                  currentPage={currentPage}
                  setCurrentPage={setCurrentPage}
                  onClose={closePdfViewer}
                />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}