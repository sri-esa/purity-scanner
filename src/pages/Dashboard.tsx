import { useAuth } from "@/hooks/useAuth";
import { useUserSync } from "@/hooks/useUserSync";
import { useAnalysisSessions } from "@/hooks/useAnalysisSessions";
import { useRealtimeAnalytics } from "@/hooks/useRealtimeAnalytics";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { 
  LogOut, 
  User, 
  Settings, 
  Zap, 
  Activity, 
  BarChart3, 
  Beaker, 
  Shield,
  Loader2
} from "lucide-react";
import { useNavigate } from "react-router-dom";

export const Dashboard = () => {
  const { user, isAuthenticated, isLoading, signOut } = useAuth();
  const navigate = useNavigate();
  
  // Sync user to Supabase
  useUserSync();
  
  // Fetch data
  const { sessions } = useAnalysisSessions();
  const { analyticsData } = useRealtimeAnalytics();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    navigate("/sign-in");
    return null;
  }

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case "admin":
        return "destructive";
      case "operator":
        return "default";
      case "viewer":
        return "secondary";
      default:
        return "outline";
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "admin":
        return <Shield className="h-4 w-4" />;
      case "operator":
        return <Beaker className="h-4 w-4" />;
      case "viewer":
        return <User className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                  <Zap className="w-4 h-4 text-primary-foreground" />
                </div>
                <h1 className="text-xl font-bold">Purity Vision Lab</h1>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <Badge variant={getRoleBadgeVariant(user.role || "operator")} className="flex items-center space-x-1">
                {getRoleIcon(user.role || "operator")}
                <span className="capitalize">{user.role || "operator"}</span>
              </Badge>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.image || ""} alt={user.name || ""} />
                      <AvatarFallback>
                        {user.name?.charAt(0) || user.email?.charAt(0) || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user.name || "User"}</p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <User className="mr-2 h-4 w-4" />
                    <span>Profile</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={signOut}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">
              Welcome back, {user.name || "User"}!
            </h2>
            <p className="text-muted-foreground">
              Manage your chemical purity analysis sessions and view real-time results.
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{sessions.length}</div>
                <p className="text-xs text-muted-foreground">
                  Analysis sessions completed
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Purity</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData?.systemHealth.averagePurity.toFixed(1) || "0.0"}%
                </div>
                <p className="text-xs text-muted-foreground">
                  System performance
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Model Accuracy</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData?.systemHealth.modelAccuracy || "0.0"}%
                </div>
                <p className="text-xs text-muted-foreground">
                  ML model performance
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Samples Analyzed</CardTitle>
                <Beaker className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData?.systemHealth.samplesAnalyzed || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  This period
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>Start New Analysis</span>
                </CardTitle>
                <CardDescription>
                  Begin a new chemical purity analysis session
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button className="w-full" onClick={() => navigate("/get-started")}>
                  Start Analysis
                </Button>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>View Analytics</span>
                </CardTitle>
                <CardDescription>
                  Review analysis results and performance metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full" onClick={() => navigate("/")}>
                  View Dashboard
                </Button>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>Device Management</span>
                </CardTitle>
                <CardDescription>
                  Manage your Raman spectroscopy devices
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  Manage Devices
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Analysis Sessions</CardTitle>
              <CardDescription>
                Your latest chemical purity analysis results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Acetone Purity Test</p>
                    <p className="text-xs text-muted-foreground">2 hours ago</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-green-600">98.4%</p>
                    <p className="text-xs text-muted-foreground">High confidence</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Ethanol Quality Check</p>
                    <p className="text-xs text-muted-foreground">5 hours ago</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-green-600">96.8%</p>
                    <p className="text-xs text-muted-foreground">Good quality</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Methanol Analysis</p>
                    <p className="text-xs text-muted-foreground">1 day ago</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-yellow-600">94.2%</p>
                    <p className="text-xs text-muted-foreground">Needs attention</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};
