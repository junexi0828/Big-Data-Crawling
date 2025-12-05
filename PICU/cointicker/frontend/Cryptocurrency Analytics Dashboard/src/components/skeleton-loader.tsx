export function SkeletonCard() {
  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-5 animate-pulse">
      <div className="flex items-start justify-between mb-3">
        <div className="w-12 h-12 bg-[#2b3139] rounded-lg"></div>
        <div className="w-16 h-6 bg-[#2b3139] rounded-md"></div>
      </div>
      <div className="space-y-2">
        <div className="w-20 h-8 bg-[#2b3139] rounded"></div>
        <div className="w-32 h-4 bg-[#2b3139] rounded"></div>
      </div>
    </div>
  );
}

export function SkeletonTable() {
  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 animate-pulse">
      <div className="w-48 h-6 bg-[#2b3139] rounded mb-4"></div>
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="w-8 h-8 bg-[#2b3139] rounded-full"></div>
            <div className="flex-1 h-4 bg-[#2b3139] rounded"></div>
            <div className="w-24 h-4 bg-[#2b3139] rounded"></div>
            <div className="w-16 h-4 bg-[#2b3139] rounded"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 animate-pulse">
      <div className="flex items-center justify-between mb-6">
        <div className="w-48 h-6 bg-[#2b3139] rounded"></div>
        <div className="flex gap-2">
          <div className="w-12 h-8 bg-[#2b3139] rounded"></div>
          <div className="w-12 h-8 bg-[#2b3139] rounded"></div>
          <div className="w-12 h-8 bg-[#2b3139] rounded"></div>
        </div>
      </div>
      <div className="w-full h-[300px] bg-[#2b3139] rounded"></div>
    </div>
  );
}

export function SkeletonNewsCard() {
  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-5 animate-pulse">
      <div className="flex items-start justify-between mb-3">
        <div className="w-24 h-6 bg-[#2b3139] rounded"></div>
        <div className="w-20 h-4 bg-[#2b3139] rounded"></div>
      </div>
      <div className="space-y-3">
        <div className="w-full h-5 bg-[#2b3139] rounded"></div>
        <div className="w-3/4 h-5 bg-[#2b3139] rounded"></div>
        <div className="flex gap-2">
          <div className="w-16 h-6 bg-[#2b3139] rounded-full"></div>
          <div className="w-16 h-6 bg-[#2b3139] rounded-full"></div>
          <div className="w-16 h-6 bg-[#2b3139] rounded-full"></div>
        </div>
      </div>
    </div>
  );
}

export function SkeletonInsightCard() {
  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-5 animate-pulse">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-[#2b3139] rounded-lg"></div>
        <div className="flex-1 space-y-3">
          <div className="flex gap-2">
            <div className="w-16 h-6 bg-[#2b3139] rounded"></div>
            <div className="w-16 h-6 bg-[#2b3139] rounded"></div>
          </div>
          <div className="w-full h-4 bg-[#2b3139] rounded"></div>
          <div className="w-2/3 h-4 bg-[#2b3139] rounded"></div>
          <div className="flex items-center justify-between pt-3 border-t border-[#2b3139]">
            <div className="w-24 h-4 bg-[#2b3139] rounded"></div>
            <div className="w-32 h-8 bg-[#2b3139] rounded"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
