def notify(user, message, link=""):
    """Create a notification for a user. Kept as a small helper so other
    apps (jobs) don't need to import the Notification model directly."""
    from .models import Notification
    return Notification.objects.create(user=user, message=message, link=link)
