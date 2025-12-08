from drf_yasg import openapi

create_conversation_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "user_id": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="User UUID to create a direct conversation with",
        ),
    },
    required=["user_id"],
)
