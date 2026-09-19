import json

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from openai import OpenAI

from zerver.lib.display_recipient import get_display_recipient
from zerver.lib.response import json_success
from zerver.lib.typed_endpoint import typed_endpoint_without_parameters
from zerver.lib.url_encoding import pm_message_url, stream_message_url
from zerver.models import Recipient, Stream, UserMessage, UserProfile


def generate_recap(messages: list[dict[str, object]]) -> str:
    if not messages:
        return "You have no unread messages."

    client = OpenAI(
        api_key=settings.TOPIC_SUMMARIZATION_API_KEY,
        base_url=settings.TOPIC_SUMMARIZATION_API_BASE,
    )

    prompt = (
        "You are generating a concise recap of unread Zulip messages. "
        "Summarize the important information, decisions, questions, and action items. "
        "Do not invent information. Keep the recap brief and easy to scan. "
        "Return plain text only. Do not use Markdown, asterisks, headings, tables, or HTML.\n\n"
        f"Unread messages:\n{json.dumps(messages)}"
    )

    response = client.chat.completions.create(
        model=settings.TOPIC_SUMMARIZATION_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    recap = response.choices[0].message.content

    if recap is None:
        return "Unable to generate recap."

    return recap


@typed_endpoint_without_parameters
def get_messages_recap(
    request: HttpRequest,
    user_profile: UserProfile,
) -> HttpResponse:
    unread_user_messages = (
        UserMessage.objects.filter(user_profile=user_profile)
        .extra(where=[UserMessage.where_unread()])
        .select_related("message", "message__sender", "message__recipient")
        .order_by("message_id")
    )

    messages: list[dict[str, object]] = []

    for user_message in unread_user_messages:
        message = user_message.message
        recipient = message.recipient

        message_data: dict[str, object] = {
            "id": message.id,
            "sender": message.sender.full_name,
            "content": message.content,
        }

        if recipient.type == Recipient.STREAM:
            stream = Stream.objects.get(id=recipient.type_id)

            url = stream_message_url(
                user_profile.realm,
                {
                    "id": message.id,
                    "stream_id": stream.id,
                    "display_recipient": stream.name,
                    "topic": message.subject,
                },
            )

            message_data.update(
                {
                    "type": "stream",
                    "channel_id": stream.id,
                    "channel": stream.name,
                    "topic": message.subject,
                    "url": url,
                }
            )

        else:
            url = pm_message_url(
                user_profile.realm,
                {
                    "id": message.id,
                    "display_recipient": get_display_recipient(recipient),
                },
            )

            message_data.update(
                {
                    "type": "direct",
                    "channel_id": None,
                    "channel": None,
                    "topic": None,
                    "url": url,
                }
            )

        messages.append(message_data)

    recap = generate_recap(messages)

    return json_success(
        request,
        {
            "unread_count": len(messages),
            "recap": recap,
            "messages": messages,
        },
    )
