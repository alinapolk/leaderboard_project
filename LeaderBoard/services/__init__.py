from .rating import calculate_rating_score as calculate_rating_score_legacy
from .rating_service import (
    calculate_rating_score,
    calculate_rating_components,
    recalculate_student_rating,
    recalculate_all_ratings,
    get_student_rating_history,
    FORMULA_VERSION
)
from .auth_service import (
    get_tokens_for_user,
    authenticate_user,
    check_user_consent,
    create_or_update_consent,
    link_student_to_user,
    assign_student_role,
    complete_consent_flow
)

__all__ = [
    'calculate_rating_score',
    'calculate_rating_components',
    'recalculate_student_rating',
    'recalculate_all_ratings',
    'get_student_rating_history',
    'FORMULA_VERSION',
    'get_tokens_for_user',
    'authenticate_user',
    'check_user_consent',
    'create_or_update_consent',
    'link_student_to_user',
    'assign_student_role',
    'complete_consent_flow',
]