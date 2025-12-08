import { useEffect, useState } from "react";
import { Keyboard } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Button } from "./ui/button";

interface Shortcut {
  key: string;
  description: string;
}

const shortcuts: Shortcut[] = [
  { key: "⌘/Ctrl + K", description: "코인 검색" },
  { key: "⌘/Ctrl + R", description: "데이터 새로고침" },
  { key: "⌘/Ctrl + 1", description: "대시보드로 이동" },
  { key: "⌘/Ctrl + 2", description: "뉴스로 이동" },
  { key: "⌘/Ctrl + 3", description: "인사이트로 이동" },
  { key: "Esc", description: "모달 닫기" },
];

export function KeyboardShortcuts() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K: 검색
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        // 검색 기능 트리거 (추후 구현)
      }

      // Cmd/Ctrl + ?: 단축키 도움말
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        e.preventDefault();
        setIsOpen(true);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="text-[#848e9c] hover:text-[#eaecef]"
          title="키보드 단축키 (⌘/Ctrl + /)"
        >
          <Keyboard className="w-4 h-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-[#1e2329] border-[#2b3139] text-[#eaecef] max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="w-5 h-5" />
            키보드 단축키
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-3 mt-4">
          {shortcuts.map((shortcut, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-[#2b3139] rounded-lg"
            >
              <span className="text-[#848e9c]">{shortcut.description}</span>
              <kbd className="px-2 py-1 bg-[#0b0e11] border border-[#2b3139] rounded text-sm text-[#eaecef]">
                {shortcut.key}
              </kbd>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}

