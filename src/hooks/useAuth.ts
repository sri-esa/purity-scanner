import { useSession, signOut } from "@/lib/auth-client";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export const useAuth = () => {
  const { data: session, isPending } = useSession();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      await signOut();
      toast.success("Signed out successfully");
      navigate("/sign-in");
    } catch (error) {
      toast.error("Failed to sign out");
    }
  };

  return {
    user: session?.user || null,
    session: session || null,
    isAuthenticated: !!session?.user,
    isLoading: isPending,
    signOut: handleSignOut,
  };
};
