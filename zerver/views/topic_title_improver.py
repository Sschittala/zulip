import json

from django.conf import settings
from openai import OpenAI
from django.http import HttpRequest, HttpResponse

from zerver.lib.response import json_success
from zerver.lib.typed_endpoint import Json, typed_endpoint
from zerver.models import Message, Recipient, Stream, UserProfile

def analyze_topic_drift(
    current_title: str,
    messages: list[dict[str, object]],
) -> dict[str, object]:
    client = OpenAI(
        api_key=settings.TOPIC_SUMMARIZATION_API_KEY,
        base_url=settings.TOPIC_SUMMARIZATION_API_BASE,
    )

    prompt = (
        "You are analyzing a Zulip conversation to determine whether its topic "
        "title still accurately describes the discussion.\n\n"
        f"Current topic title: {current_title}\n\n"
        f"Recent messages: {json.dumps(messages)}\n\n"
        "Focus especially on the MOST RECENT messages. Determine whether the "
        "recent conversation has shifted away from the current topic title. "
        "If the last 3 or more messages consistently discuss a different subject, "
        "treat that as topic drift even if older messages matched the original title. "
        "Do not flag a single unrelated message as drift. "
        "If drift is detected, suggest a short, specific title describing the "
        "new subject.\n\n"
        '{"drift_detected": false, "suggested_title": null}'

    )

    response = client.chat.completions.create(
        model=settings.TOPIC_SUMMARIZATION_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that always responds with valid JSON.",
                },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={"type": "json_object"},

    )

    content = response.choices[0].message.content

    if content is None:
        return {
            "drift_detected": False,
            "suggested_title": None,
        }

    result = json.loads(content)

    return {
        "drift_detected": bool(result.get("drift_detected", False)),
        "suggested_title": result.get("suggested_title"),
    }
@typed_endpoint
def suggest_topic_title(
    request: HttpRequest,
    user_profile: UserProfile,
    *,
    stream_id: Json[int],
    topic_name: str,
) -> HttpResponse:
    stream = Stream.objects.get(id=stream_id, realm=user_profile.realm)

    recipient = Recipient.objects.get(
        type=Recipient.STREAM,
        type_id=stream.id,
    )

    recent_messages = (
        Message.objects.filter(
            realm_id=user_profile.realm_id,
            recipient=recipient,
            subject=topic_name,
        )
        .select_related("sender")
        .order_by("-id")[:10]
    )

    messages = [
        {
            "sender": message.sender.full_name,
            "content": message.content,
        }
        for message in reversed(recent_messages)
    ]

    if len(messages) < 3:
        return json_success(
            request,
            {
                "drift_detected": False,
                "suggested_title": None,
            },
        )

    result = analyze_topic_drift(topic_name, messages)

    return json_success(request, result)
