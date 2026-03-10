import { Brain, Route, Clock, Flame, Star } from "lucide-react";

const insights = [
  {
    icon: Route,
    title: "Preferred Route Detected",
    desc: "You take SCLR 73% of the time. Today it's 18% faster than your alternate.",
    type: "preference",
  },
  {
    icon: Clock,
    title: "Optimal Window Shifting",
    desc: "Your best departure has shifted 10 min earlier this week due to school zone traffic.",
    type: "timing",
  },
  {
    icon: Flame,
    title: "Streak: 5 Days On-Time",
    desc: "Following AI suggestions has reduced your avg commute by 22 min this month.",
    type: "streak",
  },
];

const weeklyStats = [
  { day: "Mon", saved: 15 },
  { day: "Tue", saved: 22 },
  { day: "Wed", saved: 8 },
  { day: "Thu", saved: 18 },
  { day: "Fri", saved: 25 },
];

const PersonalizedInsightsCard = () => {
  const maxSaved = Math.max(...weeklyStats.map((d) => d.saved));

  return (
    <div className="card-glass p-6 animate-slide-up-delay-4">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Personalized Insights</h3>
          <p className="text-sm text-muted-foreground">Learned from your travel behavior</p>
        </div>
        <div className="p-2 rounded-lg bg-primary/10">
          <Brain className="w-5 h-5 text-primary" />
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2 mb-6 p-4 rounded-lg bg-secondary/30">
        {weeklyStats.map((d) => (
          <div key={d.day} className="flex flex-col items-center gap-2">
            <div className="w-full h-20 flex items-end justify-center">
              <div
                className="w-6 rounded-t-md bg-gradient-to-t from-primary/60 to-primary transition-all"
                style={{ height: `${(d.saved / maxSaved) * 100}%` }}
              />
            </div>
            <span className="text-[10px] text-muted-foreground font-mono">{d.day}</span>
            <span className="text-xs font-mono text-primary">-{d.saved}m</span>
          </div>
        ))}
        <div className="col-span-5 text-center mt-2 text-xs text-muted-foreground">
          Time saved this week: <span className="text-primary font-semibold">88 min</span>
        </div>
      </div>

      <div className="space-y-3">
        {insights.map((insight, i) => (
          <div key={i} className="flex gap-3 p-3 rounded-lg bg-secondary/30 border border-border/30">
            <div className="p-2 rounded-lg bg-primary/10 h-fit">
              <insight.icon className="w-4 h-4 text-primary" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-foreground">{insight.title}</h4>
              <p className="text-xs text-muted-foreground mt-0.5">{insight.desc}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 rounded-lg bg-primary/5 border border-primary/20 flex items-center gap-3">
        <Star className="w-5 h-5 text-primary" />
        <div>
          <p className="text-sm font-medium text-foreground">Commuter Score: <span className="text-primary font-mono">87/100</span></p>
          <p className="text-xs text-muted-foreground">Top 15% of Mumbai commuters using NavAI</p>
        </div>
      </div>
    </div>
  );
};

export default PersonalizedInsightsCard;
