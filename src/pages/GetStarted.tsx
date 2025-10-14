import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Zap, CheckCircle2, AlertCircle, Download, Upload, X } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

// Simulated spectral data for different materials
const materialSpectralData = {
  acetone: [
    { wavelength: 400, intensity: 120 },
    { wavelength: 500, intensity: 340 },
    { wavelength: 600, intensity: 580 },
    { wavelength: 700, intensity: 820 },
    { wavelength: 800, intensity: 950 },
    { wavelength: 900, intensity: 1100 },
    { wavelength: 1000, intensity: 890 },
    { wavelength: 1100, intensity: 650 },
    { wavelength: 1200, intensity: 420 },
    { wavelength: 1300, intensity: 280 },
  ],
  ethanol: [
    { wavelength: 400, intensity: 80 },
    { wavelength: 500, intensity: 290 },
    { wavelength: 600, intensity: 520 },
    { wavelength: 700, intensity: 780 },
    { wavelength: 800, intensity: 1020 },
    { wavelength: 900, intensity: 1180 },
    { wavelength: 1000, intensity: 940 },
    { wavelength: 1100, intensity: 690 },
    { wavelength: 1200, intensity: 460 },
    { wavelength: 1300, intensity: 310 },
  ],
  methanol: [
    { wavelength: 400, intensity: 100 },
    { wavelength: 500, intensity: 310 },
    { wavelength: 600, intensity: 550 },
    { wavelength: 700, intensity: 800 },
    { wavelength: 800, intensity: 980 },
    { wavelength: 900, intensity: 1140 },
    { wavelength: 1000, intensity: 910 },
    { wavelength: 1100, intensity: 670 },
    { wavelength: 1200, intensity: 440 },
    { wavelength: 1300, intensity: 295 },
  ],
};

type MaterialType = keyof typeof materialSpectralData;

const GetStarted = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [selectedMaterial, setSelectedMaterial] = useState<MaterialType | null>(null);
  const [scanResult, setScanResult] = useState<{
    purity: number;
    material: string;
    confidence: number;
    contaminants: string[];
  } | null>(null);
  const [spectralData, setSpectralData] = useState<any[]>([]);
  
  // Upload states
  const [uploadedImage, setUploadedImage] = useState<{
    url: string;
    name: string;
    type: string;
  } | null>(null);
  const [uploadError, setUploadError] = useState("");
  const [isAnalyzingImage, setIsAnalyzingImage] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startScan = (material: MaterialType) => {
    setIsScanning(true);
    setSelectedMaterial(material);
    setScanProgress(0);
    setScanResult(null);
    setSpectralData([]);

    // Simulate scanning progress
    const interval = setInterval(() => {
      setScanProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          completeScan(material);
          return 100;
        }
        return prev + 10;
      });
    }, 300);

    // Simulate spectral data acquisition
    const dataInterval = setInterval(() => {
      setSpectralData((prev) => {
        const newData = materialSpectralData[material].slice(0, prev.length + 1);
        if (newData.length >= materialSpectralData[material].length) {
          clearInterval(dataInterval);
        }
        return newData;
      });
    }, 300);
  };

  const completeScan = (material: MaterialType) => {
    setTimeout(() => {
      setIsScanning(false);
      
      // Simulate ML inference results with random variation
      const basePurity = 94 + Math.random() * 5;
      const purity = Math.round(basePurity * 10) / 10;
      
      const contaminants = purity < 97 
        ? ["Water traces", "Dissolved gases"]
        : purity < 98.5
        ? ["Water traces"]
        : [];

      setScanResult({
        purity,
        material: material.charAt(0).toUpperCase() + material.slice(1),
        confidence: 92 + Math.random() * 6,
        contaminants,
      });
    }, 500);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setUploadError('Please upload only JPG, PNG, or WEBP images');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError('Image size should be less than 10MB');
      return;
    }

    setUploadError("");
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage({
        url: e.target?.result as string,
        name: file.name,
        type: file.type
      });
    };
    reader.readAsDataURL(file);
  };

  const analyzeUploadedImage = () => {
    if (!uploadedImage) return;
    
    setIsAnalyzingImage(true);
    
    setTimeout(() => {
      const basePurity = 94 + Math.random() * 5;
      const purity = Math.round(basePurity * 10) / 10;
      
      setScanResult({
        purity,
        material: "Unknown Sample",
        confidence: 92 + Math.random() * 6,
        contaminants: purity < 97 ? ["Water traces", "Dissolved gases"] : []
      });
      
      setIsAnalyzingImage(false);
    }, 2500);
  };

  const clearUploadedImage = () => {
    setUploadedImage(null);
    setUploadError("");
    setScanResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const downloadReport = () => {
    if (!scanResult) return;
    
    const report = `
PURITY ANALYSIS REPORT
======================

Material: ${scanResult.material}
Purity: ${scanResult.purity}%
Confidence: ${scanResult.confidence.toFixed(1)}%
Contaminants: ${scanResult.contaminants.length > 0 ? scanResult.contaminants.join(", ") : "None detected"}

Scan Date: ${new Date().toLocaleString()}
Device: Real-Time Purity Scanner v1.0
Method: Raman Spectroscopy + ML Inference
    `.trim();

    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `purity-report-${scanResult.material.toLowerCase()}-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border sticky top-0 bg-background/95 backdrop-blur-sm z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => window.history.back()}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Button>
            <h1 className="font-display text-xl font-bold text-gradient-primary">
              Purity Scanner
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Page Header */}
          <div className="text-center space-y-4">
            <Badge className="mb-4 bg-primary/20 text-primary border-primary/30">
              <Zap className="w-3 h-3 mr-1" />
              Live Demo
            </Badge>
            <h1 className="font-display text-4xl md:text-5xl font-bold">
              Real-Time Purity <span className="text-gradient-primary">Analysis</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Select a material to simulate Raman spectroscopy scanning or upload an image for ML-powered purity detection.
            </p>
          </div>

          {/* Upload Media Section */}
          <Card className="p-6 bg-card border-border">
            <div className="text-center mb-6">
              <h3 className="font-display text-xl font-semibold mb-2">
                Upload Media for Analysis
              </h3>
              <p className="text-sm text-muted-foreground">
                Upload an image of your sample for AI-powered purity detection
              </p>
            </div>

            {!uploadedImage ? (
              <div className="space-y-4">
                <Card
                  onClick={() => fileInputRef.current?.click()}
                  className="p-8 cursor-pointer transition-all duration-300 hover:border-primary/50 hover:glow-primary"
                >
                  <div className="flex flex-col items-center gap-3 text-center">
                    <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                      <Upload className="w-8 h-8 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Upload Media</h4>
                      <p className="text-xs text-muted-foreground">Click to select JPG, PNG, or WEBP image</p>
                    </div>
                  </div>
                </Card>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  onChange={handleFileSelect}
                  className="hidden"
                />

                {uploadError && (
                  <div className="flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <span>{uploadError}</span>
                  </div>
                )}

                <div className="text-center text-xs text-muted-foreground">
                  Supported formats: JPG, PNG, WEBP • Maximum size: 10MB
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative rounded-lg overflow-hidden border border-border">
                  <img
                    src={uploadedImage.url}
                    alt="Uploaded sample"
                    className="w-full h-auto max-h-64 object-contain bg-muted"
                  />
                  <Button
                    onClick={clearUploadedImage}
                    variant="destructive"
                    size="sm"
                    className="absolute top-2 right-2"
                  >
                    <X className="w-4 h-4 mr-1" />
                    Remove
                  </Button>
                </div>

                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>{uploadedImage.name}</span>
                  <Badge variant="outline">{uploadedImage.type.split('/')[1].toUpperCase()}</Badge>
                </div>

                {!isAnalyzingImage && !scanResult && (
                  <Button
                    onClick={analyzeUploadedImage}
                    className="w-full"
                  >
                    Analyze Purity
                  </Button>
                )}

                {isAnalyzingImage && (
                  <div className="py-4 text-center space-y-3">
                    <div className="w-12 h-12 mx-auto rounded-full border-4 border-primary border-t-transparent animate-spin" />
                    <p className="text-sm text-muted-foreground">Analyzing image...</p>
                  </div>
                )}
              </div>
            )}
          </Card>

          {/* Material Selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {(Object.keys(materialSpectralData) as MaterialType[]).map((material) => (
              <Card
                key={material}
                className={`p-6 cursor-pointer transition-all duration-300 hover:border-primary/50 hover:glow-primary ${
                  selectedMaterial === material ? "border-primary glow-primary" : ""
                }`}
                onClick={() => !isScanning && startScan(material)}
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-display text-xl font-semibold capitalize">
                      {material}
                    </h3>
                    {selectedMaterial === material && scanResult && (
                      <CheckCircle2 className="w-5 h-5 text-primary" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Common solvent used in laboratories and industrial applications
                  </p>
                  <Button
                    variant={selectedMaterial === material ? "default" : "outline"}
                    className="w-full"
                    disabled={isScanning}
                  >
                    {isScanning && selectedMaterial === material
                      ? "Scanning..."
                      : "Start Scan"}
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          {/* Scanning Interface */}
          {selectedMaterial && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Spectral Data Visualization */}
              <Card className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-display text-xl font-semibold">
                    Raman Spectrum
                  </h3>
                  <Badge variant={isScanning ? "default" : "secondary"}>
                    {isScanning ? "Acquiring..." : "Complete"}
                  </Badge>
                </div>
                
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={spectralData}>
                      <defs>
                        <linearGradient id="colorIntensity" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis 
                        dataKey="wavelength" 
                        stroke="hsl(var(--muted-foreground))"
                        label={{ value: "Wavelength (nm)", position: "insideBottom", offset: -5 }}
                      />
                      <YAxis 
                        stroke="hsl(var(--muted-foreground))"
                        label={{ value: "Intensity", angle: -90, position: "insideLeft" }}
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
                        dataKey="intensity" 
                        stroke="hsl(var(--primary))" 
                        fillOpacity={1} 
                        fill="url(#colorIntensity)"
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {isScanning && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Scan Progress</span>
                      <span className="font-semibold">{scanProgress}%</span>
                    </div>
                    <Progress value={scanProgress} className="h-2" />
                  </div>
                )}
              </Card>

              {/* Analysis Results */}
              <Card className="p-6 space-y-4">
                <h3 className="font-display text-xl font-semibold">
                  ML Inference Results
                </h3>

                {!scanResult && !isScanning && (
                  <div className="h-64 flex items-center justify-center text-muted-foreground">
                    <div className="text-center space-y-2">
                      <AlertCircle className="w-12 h-12 mx-auto opacity-50" />
                      <p>Waiting for scan to complete...</p>
                    </div>
                  </div>
                )}

                {isScanning && (
                  <div className="h-64 flex items-center justify-center">
                    <div className="text-center space-y-4">
                      <div className="w-16 h-16 mx-auto rounded-full border-4 border-primary border-t-transparent animate-spin" />
                      <p className="text-muted-foreground">Processing spectral data...</p>
                      <p className="text-sm text-muted-foreground">Running TensorFlow Lite inference</p>
                    </div>
                  </div>
                )}

                {scanResult && !isScanning && (
                  <div className="space-y-6">
                    {/* Purity Percentage */}
                    <div className="text-center p-6 rounded-lg bg-primary/10 border border-primary/20">
                      <div className="text-5xl font-bold text-gradient-primary mb-2">
                        {scanResult.purity}%
                      </div>
                      <div className="text-sm text-muted-foreground">Purity Detected</div>
                    </div>

                    {/* Detailed Metrics */}
                    <div className="space-y-3">
                      <div className="flex justify-between items-center py-2 border-b border-border">
                        <span className="text-muted-foreground">Material</span>
                        <span className="font-semibold">{scanResult.material}</span>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b border-border">
                        <span className="text-muted-foreground">Confidence</span>
                        <span className="font-semibold">{scanResult.confidence.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between items-start py-2 border-b border-border">
                        <span className="text-muted-foreground">Contaminants</span>
                        <div className="text-right">
                          {scanResult.contaminants.length > 0 ? (
                            <div className="space-y-1">
                              {scanResult.contaminants.map((c, i) => (
                                <Badge key={i} variant="outline" className="ml-2">
                                  {c}
                                </Badge>
                              ))}
                            </div>
                          ) : (
                            <Badge variant="outline" className="border-primary text-primary">
                              None detected
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex justify-between items-center py-2">
                        <span className="text-muted-foreground">Analysis Time</span>
                        <span className="font-semibold">2.8s</span>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={() => {
                          setScanResult(null);
                          setSpectralData([]);
                          setSelectedMaterial(null);
                          clearUploadedImage();
                        }}
                      >
                        New Scan
                      </Button>
                      <Button
                        variant="default"
                        className="flex-1 gap-2"
                        onClick={downloadReport}
                      >
                        <Download className="w-4 h-4" />
                        Download Report
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
            </div>
          )}

          {/* Technical Info */}
          <Card className="p-6 bg-card/50">
            <h3 className="font-display text-lg font-semibold mb-4">
              How It Works
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-bold">
                  1
                </div>
                <h4 className="font-semibold text-sm">Spectral Capture</h4>
                <p className="text-xs text-muted-foreground">
                  Raman spectrometer captures the unique molecular fingerprint of the sample
                </p>
              </div>
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-bold">
                  2
                </div>
                <h4 className="font-semibold text-sm">Data Preprocessing</h4>
                <p className="text-xs text-muted-foreground">
                  Baseline correction, denoising, and normalization prepare data for ML
                </p>
              </div>
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-bold">
                  3
                </div>
                <h4 className="font-semibold text-sm">ML Inference</h4>
                <p className="text-xs text-muted-foreground">
                  TensorFlow Lite model on Raspberry Pi predicts purity in real-time
                </p>
              </div>
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-bold">
                  4
                </div>
                <h4 className="font-semibold text-sm">Results Display</h4>
                <p className="text-xs text-muted-foreground">
                  Instant purity percentage with confidence metrics and contaminant detection
                </p>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default GetStarted;