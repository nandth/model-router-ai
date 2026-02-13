import { useState, useEffect } from "react";
import GlassSurface from "../components/GlassSurface";
import SplitText from "../components/SplitText";

function Analyticspage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetching from the backend API endpoint identified in USAGE.md
        const res = await fetch("http://localhost:8080/api/stats");
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error("Failed to fetch stats:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[50vh] text-[#C7C7C7]">
        Loading analytics...
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex justify-center items-center h-full min-h-[50vh] text-[#C7C7C7]">
        Unable to load analytics data.
      </div>
    );
  }

  return (
    <div className="relative z-10 flex flex-col items-center gap-10 p-8 w-full max-w-6xl mx-auto">
      <SplitText
        text="Platform Analytics"
        className="text-4xl md:text-5xl font-semibold text-center text-[#C7C7C7]"
        delay={50}
        duration={1.2}
        ease="power3.out"
        splitType="chars"
        from={{ opacity: 0, y: 30 }}
        to={{ opacity: 1, y: 0 }}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
        <StatCard 
            title="Total Tokens Processed" 
            value={stats.total_tokens?.toLocaleString() || "0"} 
        />
        <StatCard 
            title="Total Requests" 
            value={stats.total_requests || "0"} 
        />
        <StatCard 
            title="Success Rate" 
            value={`${stats.success_rate || 0}%`} 
            highlight={stats.success_rate > 95}
        />
        <StatCard 
            title="Total Cost" 
            value={`$${stats.total_cost?.toFixed(4) || "0.0000"}`} 
        />
        <StatCard 
            title="Avg Latency" 
            value={`${stats.avg_latency_ms?.toFixed(0) || "0"} ms`} 
        />
        <StatCard 
            title="Escalation Rate" 
            value={`${stats.escalation_rate || 0}%`} 
        />
      </div>
    </div>
  );
}

function StatCard({ title, value, highlight = false }) {
  return (
    <GlassSurface
      width="100%"
      height={140}
      borderRadius={24}
      className={`flex flex-col justify-center items-center gap-3 p-4 transition-transform hover:scale-[1.02] ${highlight ? 'border-[#569cd6]' : ''}`}
    >
      <h3 className="text-[#888888] text-sm uppercase tracking-widest font-medium">{title}</h3>
      <p className="text-[#C7C7C7] text-3xl md:text-4xl font-bold">{value}</p>
    </GlassSurface>
  );
}

export default Analyticspage;