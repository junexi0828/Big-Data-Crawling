import { useState } from "react";
import { Download, FileText, FileSpreadsheet } from "lucide-react";
import { Button } from "./ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

interface DataExportProps {
  data: any;
  filename?: string;
}

export function DataExport({ data, filename = "crypto-data" }: DataExportProps) {
  const exportToJSON = () => {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${filename}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    if (!Array.isArray(data) || data.length === 0) {
      alert("CSV로 내보낼 데이터가 없습니다.");
      return;
    }

    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(","),
      ...data.map((row) =>
        headers.map((header) => {
          const value = row[header];
          return typeof value === "string" && value.includes(",")
            ? `"${value}"`
            : value;
        }).join(",")
      ),
    ];

    const csvStr = csvRows.join("\n");
    const blob = new Blob([csvStr], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${filename}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="bg-[#2b3139] border-[#2b3139] text-[#eaecef] hover:bg-[#2b3139]/80"
        >
          <Download className="w-4 h-4 mr-2" />
          내보내기
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="bg-[#1e2329] border-[#2b3139]">
        <DropdownMenuItem
          onClick={exportToJSON}
          className="text-[#eaecef] hover:bg-[#2b3139] cursor-pointer"
        >
          <FileText className="w-4 h-4 mr-2" />
          JSON으로 내보내기
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={exportToCSV}
          className="text-[#eaecef] hover:bg-[#2b3139] cursor-pointer"
        >
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          CSV로 내보내기
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

