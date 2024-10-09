import React from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface FileUploadProps {
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  pdfType: string;
  handlePdfTypeChange: (value: string) => void;
  handleFileUpload: () => void;
  file: File | null;
  isUploading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  handleFileChange,
  pdfType,
  handlePdfTypeChange,
  handleFileUpload,
  file,
  isUploading,
}) => {
  return (
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
  );
};

export default FileUpload;