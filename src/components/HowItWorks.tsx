import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";

const steps = [
  {
    step: "01",
    title: "Power On Device",
    description: "User powers on the portable Raman spectroscopy device with built-in Raspberry Pi."
  },
  {
    step: "02",
    title: "Capture Spectrum",
    description: "Raman sensor captures the sample's unique spectral fingerprint in milliseconds."
  },
  {
    step: "03",
    title: "AI Processing",
    description: "On-device ML model analyzes spectral data with baseline correction and denoising."
  },
  {
    step: "04",
    title: "Purity Prediction",
    description: "TensorFlow Lite model outputs purity percentage with confidence metrics."
  },
  {
    step: "05",
    title: "Data Storage",
    description: "Backend API stores results in MongoDB with complete metadata and audit trail."
  },
  {
    step: "06",
    title: "3D Visualization",
    description: "Dashboard displays purity %, confidence, and interactive 3D spectral plots."
  },
  {
    step: "07",
    title: "Report Generation",
    description: "Generate and download professional PDF reports or sync to cloud storage."
  }
];

export const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-24 relative gradient-accent">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16 space-y-4">
          <Badge className="mb-4 bg-primary/20 text-primary border-primary/30">
            Workflow
          </Badge>
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold">
            How It <span className="text-gradient-secondary">Works</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            From sample to result in under 3 seconds. A seamless workflow powered by AI and precision engineering.
          </p>
        </div>

        {/* Timeline */}
        <div className="max-w-4xl mx-auto space-y-8">
          {steps.map((item, index) => (
            <div 
              key={index}
              className="flex gap-6 items-start group"
            >
              {/* Step Number */}
              <div className="flex-shrink-0">
                <div className="w-16 h-16 rounded-full bg-card border-2 border-primary/30 flex items-center justify-center font-display text-xl font-bold text-gradient-primary group-hover:glow-primary transition-all duration-300">
                  {item.step}
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 pb-8 border-l-2 border-border pl-6 -ml-8 group-hover:border-primary/50 transition-colors duration-300">
                <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 hover:glow-primary transition-all duration-300">
                  <div className="flex items-start gap-3 mb-2">
                    <CheckCircle2 className="w-5 h-5 text-secondary flex-shrink-0 mt-1" />
                    <h3 className="font-display text-xl font-semibold">
                      {item.title}
                    </h3>
                  </div>
                  <p className="text-muted-foreground ml-8">
                    {item.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
