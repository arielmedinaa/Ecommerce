from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Usa directamente el tipo str (en lugar de six.text_type)
        return (
            str(user.pk) +
            str(timestamp) +
            str(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()
    