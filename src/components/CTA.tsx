import { Button } from "@/components/ui/button";
import { ArrowRight, Mail } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const CTA = () => {
  const navigate = useNavigate();

  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background Gradient */}
      <div className="absolute inset-0 gradient-primary opacity-10" />
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `linear-gradient(hsl(217 91% 60% / 0.1) 1px, transparent 1px),
                            linear-gradient(90deg, hsl(217 91% 60% / 0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Heading */}
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold">
            Advancing <span className="text-gradient-primary">Chemical Analysis</span> Research
          </h2>

          {/* Description */}
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Contributing to accessible, accurate quality control solutions for laboratories 
            and research facilities worldwide.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button 
              variant="hero" 
              size="lg" 
              className="text-lg px-8 py-6 h-auto"
              onClick={() => navigate("/get-started")}
            >
              View Research
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button 
              variant="heroOutline" 
              size="lg" 
              className="text-lg px-8 py-6 h-auto"
            >
              <Mail className="w-5 h-5 mr-2" />
              Contact Team
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="pt-8 flex flex-col sm:flex-row gap-6 justify-center items-center text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-secondary" />
              <span>Open-source project</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-secondary" />
              <span>Academic research</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-secondary" />
              <span>Reproducible results</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
