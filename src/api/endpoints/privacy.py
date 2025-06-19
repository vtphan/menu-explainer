from fastapi import APIRouter

router = APIRouter(tags=["Legal"])


@router.get("/privacy")
def get_privacy_policy():
    """Return the privacy policy for the Menu Explainer API."""
    return {
        "title": "Menu Explainer API Privacy Policy",
        "last_updated": "2025-01-19",
        "content": {
            "introduction": "This privacy policy describes how the Menu Explainer API handles data.",
            "data_collection": {
                "description": "The Menu Explainer API is a read-only service that provides restaurant menu information.",
                "personal_data": "We do not collect, store, or process any personal data from API users.",
                "usage_data": "Basic API usage may be logged for operational purposes (e.g., error monitoring)."
            },
            "data_storage": {
                "description": "The API serves restaurant menu data from a pre-populated database.",
                "user_data": "No user data is stored by this API."
            },
            "data_sharing": {
                "description": "We do not share any data with third parties.",
                "menu_data": "Restaurant menu data is publicly accessible through the API endpoints."
            },
            "data_security": {
                "description": "The API is read-only and does not accept user input beyond query parameters.",
                "measures": "Standard web security practices are implemented."
            },
            "user_rights": {
                "description": "Since we don't collect personal data, there is no personal data to access, modify, or delete."
            },
            "contact": {
                "description": "For questions about this privacy policy or the API, please contact the API administrator.",
                "note": "This is a demonstration API for educational purposes."
            },
            "changes": {
                "description": "Any changes to this privacy policy will be reflected in the 'last_updated' field."
            }
        }
    }