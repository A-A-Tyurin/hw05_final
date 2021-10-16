from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class ModelBackendUserWithProfile(ModelBackend):

    def get_user(self, user_id):
        try:
            user = (get_user_model()._default_manager
                                    .select_related("profile")
                                    .get(pk=user_id))
        except get_user_model().DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
