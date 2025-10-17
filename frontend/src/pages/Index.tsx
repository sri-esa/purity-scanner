import { Hero } from "@/components/Hero";
import { Features } from "@/components/Features";
import { HowItWorks } from "@/components/HowItWorks";
import { DataAnalytics } from "@/components/DataAnalytics";
import { UseCases } from "@/components/UseCases";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Hero />
      <Features />
      <HowItWorks />
      <DataAnalytics />
      <UseCases />
      <CTA />
      <Footer />
    </div>
  );
};

export default Index;
