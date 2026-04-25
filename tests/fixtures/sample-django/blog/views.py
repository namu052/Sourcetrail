from .models import UserProfile


def build_payload(profile: UserProfile) -> dict[str, object]:
    return {
        "email": profile.email,
        "display_name": profile.display_name(),
    }
