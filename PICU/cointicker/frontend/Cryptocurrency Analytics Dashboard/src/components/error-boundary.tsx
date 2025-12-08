import { Component, ReactNode } from "react";
import { AlertCircle } from "lucide-react";
import { Button } from "./ui/button";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0b0e11] flex items-center justify-center p-5">
          <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-8 max-w-md text-center">
            <AlertCircle className="w-16 h-16 text-[#ff6b6b] mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-[#eaecef] mb-2">오류가 발생했습니다</h2>
            <p className="text-[#848e9c] mb-6">
              {this.state.error?.message || "예상치 못한 오류가 발생했습니다."}
            </p>
            <Button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90"
            >
              페이지 새로고침
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

