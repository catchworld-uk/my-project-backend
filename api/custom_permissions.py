from rest_framework.permissions import BasePermission

GROUP_TIERS = {
    "Basic": 1,
    "Dispatcher": 2,
    "CDD": 3,
    "Admin": 4
}

class HasMinimumTierPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Check the required tier level, to ensure the user has the correct or above tier level.
        required_tier_level = getattr(view, 'required_tier_level', None)
        if required_tier_level is None:
            return False

        # Get the highest tier level from user's groups
        user_groups = user.groups.values_list('name', flat=True)
        user_tiers = [GROUP_TIERS.get(group, 0) for group in user_groups]
        highest_tier = max(user_tiers) if user_tiers else 0

        return highest_tier >= required_tier_level

