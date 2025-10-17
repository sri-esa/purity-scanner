import { Card } from "@/components/ui/card";
import { Beaker, Building2, Factory, GraduationCap, Pill, ShieldCheck } from "lucide-react";

const useCases = [
  {
    icon: Pill,
    title: "Pharmaceutical Quality Control",
    description: "Verify drug purity and detect counterfeit medications in real-time at production facilities and distribution centers."
  },
  {
    icon: Beaker,
    title: "Chemical Manufacturing",
    description: "Monitor reaction purity, validate batch consistency, and ensure product specifications are met throughout production."
  },
  {
    icon: ShieldCheck,
    title: "Regulatory Compliance",
    description: "Generate tamper-proof audit trails and certification reports for FDA, ISO, and international regulatory standards."
  },
  {
    icon: GraduationCap,
    title: "Research & Development",
    description: "Accelerate material research with instant spectral analysis and automated data logging for lab experiments."
  },
  {
    icon: Factory,
    title: "Industrial QA/QC",
    description: "Portable field testing for polymers, metals, and composites with immediate pass/fail determination."
  },
  {
    icon: Building2,
    title: "Supply Chain Verification",
    description: "Authenticate raw materials at receiving, detect adulteration, and verify supplier claims on-site."
  }
];

export const UseCases = () => {
  return (
    <section id="use-cases" className="py-24 relative gradient-accent">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16 space-y-4">
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold">
            Trusted Across <span className="text-gradient-secondary">Industries</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            From pharmaceutical labs to manufacturing floors, our technology ensures quality and compliance.
          </p>
        </div>

        {/* Use Cases Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {useCases.map((useCase, index) => {
            const Icon = useCase.icon;
            return (
              <Card 
                key={index}
                className="p-8 bg-card border-border hover:border-secondary/50 transition-all duration-300 space-y-4 group hover:glow-secondary"
              >
                {/* Icon */}
                <div className="w-14 h-14 rounded-xl gradient-secondary flex items-center justify-center glow-secondary">
                  <Icon className="w-7 h-7 text-foreground" />
                </div>

                {/* Content */}
                <div className="space-y-3">
                  <h3 className="font-display text-xl font-semibold group-hover:text-secondary transition-colors">
                    {useCase.title}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {useCase.description}
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
