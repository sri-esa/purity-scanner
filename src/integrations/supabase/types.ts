export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      analysis_results: {
        Row: {
          id: string
          session_id: string
          purity_percentage: number
          confidence_score: number
          processing_time_ms: number | null
          ml_model_version: string | null
          contaminants: Json | null
          spectral_quality_score: number | null
          baseline_correction_applied: boolean
          denoising_applied: boolean
          created_at: string
        }
        Insert: {
          id?: string
          session_id: string
          purity_percentage: number
          confidence_score: number
          processing_time_ms?: number | null
          ml_model_version?: string | null
          contaminants?: Json | null
          spectral_quality_score?: number | null
          baseline_correction_applied?: boolean
          denoising_applied?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          session_id?: string
          purity_percentage?: number
          confidence_score?: number
          processing_time_ms?: number | null
          ml_model_version?: string | null
          contaminants?: Json | null
          spectral_quality_score?: number | null
          baseline_correction_applied?: boolean
          denoising_applied?: boolean
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "analysis_results_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "analysis_sessions"
            referencedColumns: ["id"]
          }
        ]
      }
      analysis_sessions: {
        Row: {
          id: string
          device_id: string
          user_id: string | null
          material_id: string | null
          session_name: string | null
          status: Database["public"]["Enums"]["analysis_status"]
          started_at: string
          completed_at: string | null
          notes: string | null
          metadata: Json
          created_at: string
        }
        Insert: {
          id?: string
          device_id: string
          user_id?: string | null
          material_id?: string | null
          session_name?: string | null
          status?: Database["public"]["Enums"]["analysis_status"]
          started_at?: string
          completed_at?: string | null
          notes?: string | null
          metadata?: Json
          created_at?: string
        }
        Update: {
          id?: string
          device_id?: string
          user_id?: string | null
          material_id?: string | null
          session_name?: string | null
          status?: Database["public"]["Enums"]["analysis_status"]
          started_at?: string
          completed_at?: string | null
          notes?: string | null
          metadata?: Json
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "analysis_sessions_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "devices"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "analysis_sessions_material_id_fkey"
            columns: ["material_id"]
            isOneToOne: false
            referencedRelation: "materials"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "analysis_sessions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      device_logs: {
        Row: {
          id: string
          device_id: string
          log_level: string
          message: string
          context: Json
          created_at: string
        }
        Insert: {
          id?: string
          device_id: string
          log_level: string
          message: string
          context?: Json
          created_at?: string
        }
        Update: {
          id?: string
          device_id?: string
          log_level?: string
          message?: string
          context?: Json
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "device_logs_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "devices"
            referencedColumns: ["id"]
          }
        ]
      }
      devices: {
        Row: {
          id: string
          name: string
          serial_number: string
          model: string | null
          firmware_version: string | null
          status: Database["public"]["Enums"]["device_status"]
          last_seen: string | null
          location: string | null
          organization_id: string
          settings: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          serial_number: string
          model?: string | null
          firmware_version?: string | null
          status?: Database["public"]["Enums"]["device_status"]
          last_seen?: string | null
          location?: string | null
          organization_id: string
          settings?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          serial_number?: string
          model?: string | null
          firmware_version?: string | null
          status?: Database["public"]["Enums"]["device_status"]
          last_seen?: string | null
          location?: string | null
          organization_id?: string
          settings?: Json
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "devices_organization_id_fkey"
            columns: ["organization_id"]
            isOneToOne: false
            referencedRelation: "organizations"
            referencedColumns: ["id"]
          }
        ]
      }
      materials: {
        Row: {
          id: string
          name: string
          chemical_formula: string | null
          cas_number: string | null
          description: string | null
          category: string | null
          expected_purity_range: Json | null
          spectral_reference: Json | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          chemical_formula?: string | null
          cas_number?: string | null
          description?: string | null
          category?: string | null
          expected_purity_range?: Json | null
          spectral_reference?: Json | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          chemical_formula?: string | null
          cas_number?: string | null
          description?: string | null
          category?: string | null
          expected_purity_range?: Json | null
          spectral_reference?: Json | null
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      organizations: {
        Row: {
          id: string
          name: string
          description: string | null
          industry: string | null
          address: Json | null
          contact_info: Json | null
          settings: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          description?: string | null
          industry?: string | null
          address?: Json | null
          contact_info?: Json | null
          settings?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          description?: string | null
          industry?: string | null
          address?: Json | null
          contact_info?: Json | null
          settings?: Json
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      reports: {
        Row: {
          id: string
          session_id: string
          user_id: string | null
          title: string
          format: Database["public"]["Enums"]["report_format"]
          file_path: string | null
          file_size_bytes: number | null
          generated_at: string
          download_count: number
          metadata: Json
        }
        Insert: {
          id?: string
          session_id: string
          user_id?: string | null
          title: string
          format?: Database["public"]["Enums"]["report_format"]
          file_path?: string | null
          file_size_bytes?: number | null
          generated_at?: string
          download_count?: number
          metadata?: Json
        }
        Update: {
          id?: string
          session_id?: string
          user_id?: string | null
          title?: string
          format?: Database["public"]["Enums"]["report_format"]
          file_path?: string | null
          file_size_bytes?: number | null
          generated_at?: string
          download_count?: number
          metadata?: Json
        }
        Relationships: [
          {
            foreignKeyName: "reports_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "analysis_sessions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "reports_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      spectral_data: {
        Row: {
          id: string
          session_id: string
          wavelength: number
          intensity: number
          timestamp: string
          data_point_index: number | null
        }
        Insert: {
          id?: string
          session_id: string
          wavelength: number
          intensity: number
          timestamp?: string
          data_point_index?: number | null
        }
        Update: {
          id?: string
          session_id?: string
          wavelength?: number
          intensity?: number
          timestamp?: string
          data_point_index?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "spectral_data_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "analysis_sessions"
            referencedColumns: ["id"]
          }
        ]
      }
      system_metrics: {
        Row: {
          id: string
          device_id: string
          metric_name: string
          metric_value: number
          unit: string | null
          timestamp: string
        }
        Insert: {
          id?: string
          device_id: string
          metric_name: string
          metric_value: number
          unit?: string | null
          timestamp?: string
        }
        Update: {
          id?: string
          device_id?: string
          metric_name?: string
          metric_value?: number
          unit?: string | null
          timestamp?: string
        }
        Relationships: [
          {
            foreignKeyName: "system_metrics_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "devices"
            referencedColumns: ["id"]
          }
        ]
      }
      users: {
        Row: {
          id: string
          email: string
          full_name: string | null
          avatar_url: string | null
          role: Database["public"]["Enums"]["user_role"]
          organization_id: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          avatar_url?: string | null
          role?: Database["public"]["Enums"]["user_role"]
          organization_id?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          avatar_url?: string | null
          role?: Database["public"]["Enums"]["user_role"]
          organization_id?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "users_organization_id_fkey"
            columns: ["organization_id"]
            isOneToOne: false
            referencedRelation: "organizations"
            referencedColumns: ["id"]
          }
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      analysis_status: "pending" | "processing" | "completed" | "failed"
      device_status: "online" | "offline" | "maintenance" | "error"
      report_format: "pdf" | "csv" | "json"
      user_role: "admin" | "operator" | "viewer"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
