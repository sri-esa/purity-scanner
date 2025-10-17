import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Server, Cpu, Database, Code, Lock, Gauge } from "lucide-react";

const specs = [
  {
    icon: Gauge,
    category: "Performance",
    items: [
      "≤3s inference + display latency",
      "95% purity prediction accuracy",
      "Real-time spectral processing",
      "99% system uptime guarantee"
    ]
  },
  {
    icon: Cpu,
    category: "Hardware",
    items: [
      "Raspberry Pi 4 (4GB RAM)",
      "Portable Raman spectrometer",
      "GPIO interface for sensor data",
      "Optional display support"
    ]
  },
  {
    icon: Code,
    category: "Software Stack",
    items: [
      "Three.js + Tailwind CSS frontend",
      "Node.js + Express backend",
      "TensorFlow Lite ML inference",
      "Python for data capture"
    ]
  },
  {
    icon: Database,
    category: "Data Management",
    items: [
      "MongoDB for spectral storage",
      "Up to 10,000 records capacity",
      "PDF/CSV report generation",
      "Cloud sync capability"
    ]
  },
  {
    icon: Server,
    category: "Deployment",
    items: [
      "Docker Compose orchestration",
      "Offline-first architecture",
      "Modular container design",
      "Easy scalability"
    ]
  },
  {
    icon: Lock,
    category: "Security",
    items: [
      "Encrypted local data storage",
      "Secure API key management",
      "Data integrity checks",
      "Automatic retry mechanisms"
    ]
  }
];

export const TechSpecs = () => {
  return (
    <section id="tech-specs" className="py-24 relative">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16 space-y-4">
          <Badge className="mb-4 bg-secondary/20 text-secondary border-secondary/30">
            Technical Specifications
          </Badge>
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold">
            Built on <span className="text-gradient-primary">Enterprise-Grade</span> Technology
          </h2>
          <p className="text-lg text-muted-foreground">
            Every component carefully selected for maximum performance, reliability, and maintainability.
          </p>
        </div>

        {/* Specs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {specs.map((spec, index) => {
            const Icon = spec.icon;
            return (
              <Card 
                key={index}
                className="p-6 bg-card border-border hover:border-primary/50 transition-all duration-300 space-y-4 group hover:glow-primary"
              >
                {/* Icon & Category */}
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center group-hover:bg-primary/30 transition-colors">
                    <Icon className="w-5 h-5 text-primary" />
                  </div>
                  <h3 className="font-display text-xl font-semibold group-hover:text-primary transition-colors">
                    {spec.category}
                  </h3>
                </div>

                {/* Items List */}
                <ul className="space-y-2">
                  {spec.items.map((item, itemIndex) => (
                    <li 
                      key={itemIndex}
                      className="flex items-start gap-2 text-sm text-muted-foreground"
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-secondary mt-1.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};
