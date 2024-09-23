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

export default function ContractForm() {
  // Form state
  const [formData, setFormData] = useState({
    remark: "",
    gst: "exclusive",
    subContractClause: "",
    sowValue: "",
  });

  // API response state
  const [apiData, setApiData] = useState({
    account_name: "",
    currency: "",
    sow_start_date: "",
    sow_end_date: "",
    sow_number: "",
    cola: "",
    total_fte: "",
    credit_period: "",
  });

  // File upload state
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [excelFile, setExcelFile] = useState<Blob | null>(null);
  const [pdfType, setPdfType] = useState("SOW");

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
      setFile(e.target.files[0]);
    }
  };

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
        });

        if (response.ok) {
          const result = await response.json();
          console.log("File uploaded successfully:", result);

          setApiData(result.extracted_data);

          const allData = { ...formData, ...result.extracted_data };
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
        } else {
          const errorData = await response.json();
          console.error("File upload failed:", errorData.detail);
          toast.error(
            "An error occurred while uploading the file. Please try again."
          );
        }
      } catch (error) {
        console.error("Error uploading file:", error);
        toast.error(
          "An error occurred while uploading the file. Please try again."
        );
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
    <div className="min-h-screen bg-black">
      <nav>
        <Button onClick={() => router.push('/chat')}>Chat</Button>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-6">
                Contract Form
              </h1>

              <form className="space-y-6 text-black">
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-3">
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
                    <Label htmlFor="gst">GST</Label>
                    <Select
                      onValueChange={handleSelectChange}
                      value={formData.gst}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select GST type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="exclusive">Exclusive</SelectItem>
                        <SelectItem value="inclusive">Inclusive</SelectItem>
                      </SelectContent>
                    </Select>
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
                  <div>
                    <Label htmlFor="sowValue">SOW Value</Label>
                    <Input
                      id="sowValue"
                      name="sowValue"
                      value={formData.sowValue}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </form>

              <div className="mt-8 text-black">
                <Label htmlFor="file-upload">Upload PDF</Label>
                <div className="mt-1 flex items-center gap-x-12">
                  <Input
                    id="file-upload"
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf"
                  />
                  <Select value={pdfType} onValueChange={handlePdfTypeChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select PDF type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="NDA">NDA</SelectItem>
                      <SelectItem value="SOW">SOW</SelectItem>
                      <SelectItem value="MSA">MSA</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    onClick={handleFileUpload}
                    disabled={!file || isUploading}
                    className="ml-4"
                  >
                    {isUploading ? "Uploading..." : "Upload PDF"}
                  </Button>
                </div>
              </div>

              <Separator className="mt-12 text-black" />

              <div className="mt-8 overflow-x-auto text-black">
                <h1>
                  <span className="text-2xl font-bold text-gray-900">
                    Contract Data
                  </span>
                </h1>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Field</TableHead>
                      <TableHead>Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {Object.entries({ ...formData, ...apiData }).map(
                      ([key, value]) => (
                        <TableRow key={key}>
                          <TableCell className="font-medium">{key}</TableCell>
                          <TableCell>{value}</TableCell>
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
        </div>
      </main>
    </div>
  );
}
