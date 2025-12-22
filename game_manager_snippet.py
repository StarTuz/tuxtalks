
    def remove_group(self, group_name):
        """Removes all profiles belonging to a specific group."""
        initial_count = len(self.profiles)
        self.profiles = [p for p in self.profiles if p.group != group_name]
        removed_count = initial_count - len(self.profiles)
        
        if removed_count > 0:
             self.save_profiles()
             # Check if active profile was removed
             if self.active_profile and self.active_profile.group == group_name:
                  self.active_profile = self.profiles[0] if self.profiles else None
                  
        return removed_count
