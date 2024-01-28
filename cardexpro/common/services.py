from typing import List, Dict, Any, Tuple
from cardexpro.common.types import DjangoModelType
from rest_framework.exceptions import ValidationError


def model_update(
    *,
    instance: DjangoModelType,
    fields: List[str],
    data: Dict[str, Any]
) -> Tuple[DjangoModelType, bool]:
    """
    Generic update service meant to be reused in local update services

    For example:

    def user_update(*, user: User, data) -> User:
        fields = ['first_name', 'last_name']
        user, has_updated = model_update(instance=user, fields=fields, data=data)

        // Do other actions with the user here

        return user

    Return value: Tuple with the following elements:
        1. The instance we updated
        2. A boolean value representing whether we performed an update or not.
    """
    has_updated = False

    for field in fields:
        # Skip if a field is not present in the actual data
        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            has_updated = True
            setattr(instance, field, data[field])

    # Perform an update only if any of the fields was actually changed
    if has_updated:
        instance.full_clean()
        # Update only the fields that are meant to be updated.
        # Django docs reference:
        # https://docs.djangoproject.com/en/dev/ref/models/instances/#specifying-which-fields-to-save
        instance.save(update_fields=fields)

    return instance, has_updated


def handle_validation_error(serializer):
    try:
        serializer.is_valid(raise_exception=True)
        return True  # Validation successful
    except ValidationError as ve:
        if (len(ve.detail.items())) == 1:
            error_message = next(iter(ve.detail.values()))[0]
            response_data = {
                "is_success": False,
                "data": {
                    "error_type": "",
                    "params": list(ve.detail.keys())[0],
                    "message": error_message,
                }
            }

        else:
            error_messages = ""
            error_type = ""
            for key, values in ve.detail.items():
                error_type += str(key) + " "
                error_messages += f"{str(key)}: {str(values[0])} "
            response_data = {
                "is_success": False,
                "data": {
                    "error_type": "",
                    "params": error_type,
                    "message": error_messages,
                }
            }

        return response_data


def error_response(
        *,
        error_type: str = "",
        params: str = "",
        message: str = "",
):
    return {
        "is_success": False,
        "data": {
            "error_type": error_type,
            "params": params,
            "message": message,
        }
    }


def success_response(
        *,
        data: dict = {},
):
    return {
        "is_success": True,
        "data": data
    }