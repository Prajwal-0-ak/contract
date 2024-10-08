"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import * as XLSX from "xlsx";
import { Separator } from "@/components/ui/separator";
import { useRouter } from "next/navigation";
import PDFViewer from "@/components/PDFViewer";

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

export default function ContractForm() {
  // Form state
  const [formData, setFormData] = useState({
    remark: "",
    subContractClause: "",
  });

  // API response state
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

  // File upload state
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [excelFile, setExcelFile] = useState<Blob | null>(null);
  const [pdfType, setPdfType] = useState("SOW");

  const [fieldPageMapping, setFieldPageMapping] = useState<Record<string, string>>({});

  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [showPdfViewer, setShowPdfViewer] = useState(false);

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // Handle select changes
  const handleSelectChange = (value: string) => {
    setFormData((prevData) => ({
      ...prevData,
      gst: value,
    }));
  };

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPdfFile(selectedFile);
      setShowPdfViewer(true);
    }
  };

  // Handle PDF type change
  const handlePdfTypeChange = (value: string) => {
    setPdfType(value);
  };

  // Handle file upload
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
          // Add this line to include credentials
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Response from server:", result);

        // Process the extracted data
        const extractedData = result.extracted_data as ExtractedDataItem[];
        
        const newApiData: ApiData = {
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
        };

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
        if (error instanceof TypeError && error.message.includes('NetworkError')) {
          toast.error("Network error. Please check your connection and try again.");
        } else {
          toast.error(
            `An error occurred while uploading the file: ${(error as Error).message || 'Unknown error'}`
          );
        }
      } finally {
        setIsUploading(false);
      }
    }
  };

  // Handle Excel download
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

  const router = useRouter();
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
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
              <Button onClick={() => router.push("/chat")}>
                Chat
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-8xl mx-auto py-6 sm:px-6 lg:px-8">
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

                <form className="space-y-6 text-black">
                  <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                    <div>
                      <Label htmlFor="remark">Remark</Label>
                      <Input
                        id="remark"
                        name="remark"
                        value={formData.remark}
                        onChange={handleInputChange}
                      />
                    </div>
                    <div>
                      <Label htmlFor="subContractClause">
                        Sub Contract Clause
                      </Label>
                      <Input
                        id="subContractClause"
                        name="subContractClause"
                        value={formData.subContractClause}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>
                </form>

                <div className="mt-8">
                  <Label htmlFor="file-upload">Upload PDF</Label>
                  <div className="mt-1 flex items-center gap-x-4">
                    <Input
                      id="file-upload"
                      type="file"
                      onChange={handleFileChange}
                      accept=".pdf"
                    />
                    <Select value={pdfType} onValueChange={handlePdfTypeChange}>
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Select PDF type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="NDA">NDA</SelectItem>
                        <SelectItem value="SOW">SOW</SelectItem>
                        <SelectItem value="MSA">MSA</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button
                    onClick={handleFileUpload}
                    disabled={!file || isUploading}
                    className="mt-4"
                  >
                    {isUploading ? "Uploading..." : "Upload PDF"}
                  </Button>
                </div>

                <Separator className="my-8" />

                <div className="mt-8 overflow-x-auto">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    Contract Data
                  </h2>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Field</TableHead>
                        <TableHead>Value</TableHead>
                        <TableHead>Page No</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {Object.entries({ ...formData, ...apiData }).map(
                        ([key, value]) => (
                          <TableRow key={key}>
                            <TableCell className="font-medium">{key}</TableCell>
                            <TableCell>{value}</TableCell>
                            <TableCell>
                              {fieldPageMapping[key] || "N/A"}
                            </TableCell>
                          </TableRow>
                        )
                      )}
                    </TableBody>
                  </Table>
                </div>

                {isDownloadReady && (
                  <div className="mt-8">
                    <Button onClick={handleDownload}>Download Excel</Button>
                  </div>
                )}
              </div>
            </div>

            {showPdfViewer && (
              <div className="w-full lg:w-1/2">
                <PDFViewer file={pdfFile} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}