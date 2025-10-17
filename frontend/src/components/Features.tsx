import { Card } from "@/components/ui/card";
import { Cpu, Database, Eye, FileText, Globe, Layers, Sparkles, Workflow } from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "Spectral Capture",
    description: "Real-time Raman spectral data capture via Raspberry Pi GPIO interface for instant analysis."
  },
  {
    icon: Layers,
    title: "Data Preprocessing",
    description: "Advanced baseline correction, denoising, and normalization for pristine spectral input."
  },
  {
    icon: Cpu,
    title: "ML Inference",
    description: "On-device TensorFlow Lite model predicts purity percentage with exceptional accuracy."
  },
  {
    icon: Database,
    title: "Secure Storage",
    description: "MongoDB stores raw spectra, outputs, and metadata with comprehensive audit trails."
  },
  {
    icon: Workflow,
    title: "Backend API",
    description: "Node.js + Express powers CRUD operations, device communication, and model results."
  },
  {
    icon: Eye,
    title: "3D Visualization",
    description: "Three.js dashboard with interactive purity graphs and stunning 3D spectral comparisons."
  },
  {
    icon: FileText,
    title: "Smart Reports",
    description: "Generate time-stamped purity reports, exportable as PDF or CSV for compliance."
  },
  {
    icon: Globe,
    title: "Cloud Sync",
    description: "Operate offline on Raspberry Pi and seamlessly sync data to cloud when connected."
  }
];

export const Features = () => {
  return (
    <section id="features" className="py-24 relative">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16 space-y-4">
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold">
            Complete <span className="text-gradient-primary">End-to-End</span> Solution
          </h2>
          <p className="text-lg text-muted-foreground">
            Every component engineered for precision, speed, and reliability in chemical purity analysis.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card 
                key={index}
                className="group relative p-6 bg-card border-border hover:border-primary/50 transition-all duration-300 hover:glow-primary cursor-pointer overflow-hidden"
              >
                {/* Gradient Background on Hover */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300 gradient-primary" />
                
                {/* Content */}
                <div className="relative space-y-4">
                  <div className="w-12 h-12 rounded-lg gradient-primary flex items-center justify-center glow-primary">
                    <Icon className="w-6 h-6 text-foreground" />
                  </div>
                  <h3 className="font-display text-xl font-semibold group-hover:text-primary transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};
