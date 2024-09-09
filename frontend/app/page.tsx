"use client"

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, Download } from 'lucide-react'
import Link from 'next/link'
import * as XLSX from 'xlsx';

export default function LandingPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [message, setMessage] = useState('');
  const [excelFile, setExcelFile] = useState<Blob | null>(null);

  const fetchHelloWorld = async () => {
    try {
      const response = await fetch('http://localhost:8000/');
      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
      } else {
        setMessage('Failed to fetch message');
      }
    } catch (error) {
      console.error('Error fetching message:', error);
      setMessage('An error occurred while fetching the message');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setIsUploading(true);

      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          console.log('File uploaded successfully:', result);

          // Generate Excel from the CSV data received from the backend
          const extractedData = result.extracted_data; // assuming backend sends extracted_data
          const ws = XLSX.utils.json_to_sheet([extractedData]); // Convert JSON to worksheet
          const wb = XLSX.utils.book_new();
          XLSX.utils.book_append_sheet(wb, ws, 'Contract Data');

          // Generate Excel file as a Blob
          const excelBlob = new Blob([XLSX.write(wb, { bookType: 'xlsx', type: 'array' })], { type: 'application/octet-stream' });
          setExcelFile(excelBlob); // Save the Excel Blob in state

          alert('File uploaded and processed successfully!');
          setIsDownloadReady(true); // Enable the download button
        } else {
          const errorData = await response.json();
          console.error('File upload failed:', errorData.message);
          alert(`File upload failed: ${errorData.message}`);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        alert('An error occurred while uploading the file. Please try again.');
      } finally {
        setIsUploading(false);
      }
    }
  };

  // Handle Excel file download when the button is clicked
  const handleDownload = () => {
    if (excelFile) {
      const url = URL.createObjectURL(excelFile);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Contract_Report.xlsx');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link); // Clean up the link
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-1">
        <section className="w-full py-4 md:py-8 lg:py-12 xl:py-16">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                  Contract Analysis Made Easy
                </h1>
                <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                  Upload your contracts and get detailed reports in minutes. Save time and reduce errors with our advanced AI-powered analysis.
                </p>
              </div>
              <button onClick={fetchHelloWorld}>Fetch Hello World</button>
              <p>{message}</p>
              <div className="space-x-4">
                <Button>Get Started</Button>
                <Button variant="outline">Learn More</Button>
              </div>
            </div>
          </div>
        </section>
        <section className="w-full pb-6 md:pb-12 lg:pb-16">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12">Analyze Your Contract</h2>
            <Card className="max-w-2xl mx-auto">
              <CardHeader>
                <CardTitle>Upload Your Contract</CardTitle>
                <CardDescription>Upload your PDF contract to get started</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid w-full max-w-sm items-center gap-1.5">
                  <Label htmlFor="contract">Contract File</Label>
                  <Input id="contract" type="file" accept=".pdf" onChange={handleFileUpload} />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button disabled={isUploading}>
                  {isUploading ? (
                    <>
                      <Upload className="mr-2 h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload
                    </>
                  )}
                </Button>
                <Button onClick={handleDownload} disabled={!isDownloadReady} variant="outline">
                  <Download className="mr-2 h-4 w-4" />
                  Download Report
                </Button>
              </CardFooter>
            </Card>
          </div>
        </section>
        <section id="how-it-works" className="w-full py-12 md:py-24 lg:py-32 bg-gray-100 dark:bg-gray-800">
          <div className="container px-4 md:px-6 text-black">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12">How It Works</h2>
            <ol className="grid gap-6 md:grid-cols-3">
              <li className="flex flex-col items-center text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">1</div>
                <h3 className="mt-4 font-semibold">Upload Your Contract</h3>
                <p className="mt-2 text-sm">Simply upload your PDF contract through our secure interface.</p>
              </li>
              <li className="flex flex-col items-center text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">2</div>
                <h3 className="mt-4 font-semibold">AI Analysis</h3>
                <p className="mt-2 text-sm">Our advanced AI system analyzes your contract thoroughly.</p>
              </li>
              <li className="flex flex-col items-center text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">3</div>
                <h3 className="mt-4 font-semibold">Download Report</h3>
                <p className="mt-2 text-sm">Receive a comprehensive report with insights and recommendations.</p>
              </li>
            </ol>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-100 dark:bg-gray-800">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-black">
                  Ready to Streamline Your Contract Analysis?
                </h2>
                <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                  Join thousands of satisfied customers who have revolutionized their contract management process.
                </p>
              </div>
              <div className="space-x-4">
                <Button size="lg">Get Started Now</Button>
                <Button className='text-black' size="lg" variant="outline">Contact Sales</Button>
              </div>
            </div>
          </div>
        </section>
      </main>
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t">
        <p className="text-xs text-gray-500 dark:text-gray-400">© 2023 Acme Contract Analysis. All rights reserved.</p>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            Terms of Service
          </Link>
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            Privacy
          </Link>
        </nav>
      </footer>
    </div>
  )
}