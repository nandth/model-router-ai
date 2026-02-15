import { useState, useEffect } from "react";
import GlassSurface from "../components/GlassSurface";
import SplitText from "../components/SplitText";

function Analyticspage() {
  const [stats, setStats] = useState({
    total_tokens: 0,
    total_requests: 0,
    success_rate: 0,
    tokens_saved: 0,
    avg_latency_ms: 0,
    escalation_rate: 0
  });

  useEffect(() => {
    // 1. Load data from Local Storage
    const history = JSON.parse(localStorage.getItem("analyticsHistory") || "[]");

    if (history.length > 0) {
      // 2. Calculate Stats
      const totalRequests = history.length;
      
      const totalTokens = history.reduce((sum, item) => sum + (item.tokens_used || 0), 0);
      const totalSaved = history.reduce((sum, item) => sum + (item.tokens_saved || 0), 0);
      const totalLatency = history.reduce((sum, item) => sum + (item.latency_ms || 0), 0);
      
      const successCount = history.filter(item => item.success === true).length;
      const escalatedCount = history.filter(item => item.routing?.escalated === true).length;

      setStats({
        total_tokens: totalTokens,
        total_requests: totalRequests,
        tokens_saved: totalSaved,
        success_rate: Math.round((successCount / totalRequests) * 100),
        avg_latency_ms: Math.round(totalLatency / totalRequests),
        escalation_rate: Math.round((escalatedCount / totalRequests) * 100)
      });
    }
  }, []);

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
            title="Total Tokens Used" 
            value={stats.total_tokens.toLocaleString()} 
        />
        <StatCard 
            title="Total Requests" 
            value={stats.total_requests} 
        />
        <StatCard 
            title="Success Rate" 
            value={`${stats.success_rate}%`} 
            highlight={stats.success_rate > 95}
        />
        <StatCard 
            title="Tokens Saved" 
            value={stats.tokens_saved.toLocaleString()}
            highlight={true} 
        />
        <StatCard 
            title="Avg Latency" 
            value={`${stats.avg_latency_ms} ms`} 
        />
        <StatCard 
            title="Escalation Rate" 
            value={`${stats.escalation_rate}%`} 
        />
      </div>
      
      {/*Button to clear history */}
      <button 
        onClick={() => {
            localStorage.removeItem("analyticsHistory");
            window.location.reload();
        }}
        className="mt-8 text-s text-gray-500 hover:text-white transition-colors"
      >
        Reset Analytics History
      </button>
    </div>
  );
}

function StatCard({ title, value, highlight = false }) {
  return (
    <GlassSurface
      width="100%"
      height={140}
      borderRadius={24}
      className={`transition-transform hover:scale-[1.02] ${highlight ? 'border-[#569cd6]' : ''}`}
    >
      <div className="w-full h-full flex flex-row justify-between items-center px-8">
        <h3 className="text-[#888888] text-sm uppercase tracking-widest font-medium text-left">
          {title}
        </h3>
        <p className="text-[#C7C7C7] text-3xl md:text-4xl font-bold text-right">
          {value}
        </p>
      </div>
    </GlassSurface>
  );
}

export default Analyticspage;