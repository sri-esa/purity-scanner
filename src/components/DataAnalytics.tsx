import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from "recharts";

// Sample purity analysis data
const purityOverTime = [
  { time: "0s", purity: 0, baseline: 0 },
  { time: "0.5s", purity: 45, baseline: 50 },
  { time: "1s", purity: 78, baseline: 75 },
  { time: "1.5s", purity: 91, baseline: 87.5 },
  { time: "2s", purity: 96.2, baseline: 93.75 },
  { time: "2.5s", purity: 97.8, baseline: 96.87 },
  { time: "3s", purity: 98.4, baseline: 98.43 },
];

const materialComparison = [
  { material: "Acetone", purity: 98.4, samples: 45 },
  { material: "Ethanol", purity: 96.8, samples: 38 },
  { material: "Methanol", purity: 97.2, samples: 42 },
  { material: "Benzene", purity: 95.6, samples: 31 },
  { material: "Toluene", purity: 94.8, samples: 28 },
];

const accuracyMetrics = [
  { metric: "Week 1", accuracy: 92.3 },
  { metric: "Week 2", accuracy: 93.8 },
  { metric: "Week 3", accuracy: 94.5 },
  { metric: "Week 4", accuracy: 95.2 },
  { metric: "Week 5", accuracy: 96.1 },
  { metric: "Week 6", accuracy: 95.8 },
];

export const DataAnalytics = () => {
  return (
    <section id="analytics" className="py-24 relative">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16 space-y-4">
          <Badge className="mb-4 bg-secondary/20 text-secondary border-secondary/30">
            Real-Time Analytics
          </Badge>
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold">
            Purity <span className="text-gradient-primary">Analysis</span> Dashboard
          </h2>
          <p className="text-lg text-muted-foreground">
            Comprehensive data visualization showing real-time purity detection accuracy and system performance metrics.
          </p>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-7xl mx-auto mb-8">
          {/* Real-Time Purity Detection Chart */}
          <Card className="p-6 bg-card border-border space-y-4">
            <div>
              <h3 className="font-display text-xl font-semibold mb-2">
                Real-Time Purity Detection
              </h3>
              <p className="text-sm text-muted-foreground">
                Live purity percentage calculation over 3-second analysis window
              </p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={purityOverTime}>
                <defs>
                  <linearGradient id="colorPurity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="time" 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                  domain={[0, 100]}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="purity" 
                  stroke="hsl(var(--primary))" 
                  fillOpacity={1} 
                  fill="url(#colorPurity)"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="baseline" 
                  stroke="hsl(var(--secondary))" 
                  strokeDasharray="5 5"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Material Comparison Chart */}
          <Card className="p-6 bg-card border-border space-y-4">
            <div>
              <h3 className="font-display text-xl font-semibold mb-2">
                Material Purity Analysis
              </h3>
              <p className="text-sm text-muted-foreground">
                Comparative purity results across different chemical samples tested
              </p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={materialComparison}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="material" 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                  domain={[90, 100]}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Bar 
                  dataKey="purity" 
                  fill="hsl(var(--primary))"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* System Accuracy Trend - Full Width */}
        <div className="max-w-7xl mx-auto">
          <Card className="p-6 bg-card border-border space-y-4">
            <div>
              <h3 className="font-display text-xl font-semibold mb-2">
                System Accuracy Improvement
              </h3>
              <p className="text-sm text-muted-foreground">
                ML model accuracy progression over 6-week testing period with continuous learning
              </p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={accuracyMetrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="metric" 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  style={{ fontSize: '12px' }}
                  domain={[90, 100]}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="accuracy" 
                  stroke="hsl(var(--secondary))" 
                  strokeWidth={3}
                  dot={{ fill: 'hsl(var(--secondary))', r: 6 }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Key Insights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto mt-8">
          <Card className="p-6 bg-card border-border text-center space-y-2">
            <div className="text-4xl font-bold text-gradient-primary">98.4%</div>
            <div className="text-sm text-muted-foreground">Average Purity Detected</div>
          </Card>
          <Card className="p-6 bg-card border-border text-center space-y-2">
            <div className="text-4xl font-bold text-gradient-secondary">95.8%</div>
            <div className="text-sm text-muted-foreground">Model Accuracy Rate</div>
          </Card>
          <Card className="p-6 bg-card border-border text-center space-y-2">
            <div className="text-4xl font-bold text-gradient-accent">184</div>
            <div className="text-sm text-muted-foreground">Samples Analyzed</div>
          </Card>
        </div>
      </div>
    </section>
  );
};