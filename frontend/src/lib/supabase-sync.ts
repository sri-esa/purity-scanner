import { supabase } from "@/integrations/supabase/client";
import type { User } from "@/lib/auth";

export const syncUserToSupabase = async (user: User) => {
  try {
    // Check if user already exists in our users table
    const { data: existingUser, error: fetchError } = await supabase
      .from('users')
      .select('id')
      .eq('id', user.id)
      .single();

    if (fetchError && fetchError.code !== 'PGRST116') {
      console.error('Error checking existing user:', fetchError);
      return;
    }

    // If user doesn't exist, create them
    if (!existingUser) {
      const { error: insertError } = await supabase
        .from('users')
        .insert({
          id: user.id,
          email: user.email,
          full_name: user.name,
          avatar_url: user.image,
          role: user.role || 'operator',
          organization_id: user.organizationId || null,
        });

      if (insertError) {
        console.error('Error creating user in Supabase:', insertError);
      } else {
        console.log('User synced to Supabase successfully');
      }
    } else {
      // Update existing user
      const { error: updateError } = await supabase
        .from('users')
        .update({
          email: user.email,
          full_name: user.name,
          avatar_url: user.image,
          role: user.role || 'operator',
          organization_id: user.organizationId || null,
          updated_at: new Date().toISOString(),
        })
        .eq('id', user.id);

      if (updateError) {
        console.error('Error updating user in Supabase:', updateError);
      } else {
        console.log('User updated in Supabase successfully');
      }
    }
  } catch (error) {
    console.error('Unexpected error syncing user to Supabase:', error);
  }
};
