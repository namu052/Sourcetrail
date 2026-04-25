from blog.models import UserProfile
from blog.views import build_payload


def load_profile(email: str) -> UserProfile:
    profile = UserProfile(email=email)
    return profile


def render(email: str) -> dict[str, object]:
    return build_payload(load_profile(email))
