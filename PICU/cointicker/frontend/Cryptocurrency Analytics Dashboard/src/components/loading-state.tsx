import { SkeletonCard, SkeletonChart, SkeletonTable } from "./skeleton-loader";

export function DashboardLoading() {
  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {[...Array(4)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <SkeletonChart />
        <SkeletonTable />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <SkeletonChart />
        </div>
        <SkeletonTable />
      </div>
    </div>
  );
}
