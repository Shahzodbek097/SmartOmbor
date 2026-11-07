from .models import CompanyMembership


def get_user_company(user):
    membership = (
        CompanyMembership.objects
        .filter(user=user, faol=True, company__faol=True)
        .select_related("company")
        .first()
    )

    if membership:
        return membership.company

    return None