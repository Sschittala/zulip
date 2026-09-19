import {$} from "jquery";
import * as z from "zod/mini";

import * as channel from "./channel.ts";
import * as dialog_widget from "./dialog_widget.ts";
import {$t} from "./i18n.ts";

const topic_title_suggestion_schema = z.object({
    drift_detected: z.boolean(),
    suggested_title: z.nullable(z.string()),
});

function show_topic_title_suggestion(suggested_title: string): void {
    const $content = $("<div>");
    $("<p>")
        .text("This conversation may have drifted from its current topic.")
        .appendTo($content);

    const $title = $("<p>");
    $("<strong>").text("Suggested title: ").appendTo($title);
    $title.append(document.createTextNode(suggested_title));
    $title.appendTo($content);

    dialog_widget.launch({
        modal_title_text: $t({defaultMessage: "Topic title suggestion"}),
        modal_content_html: $content.html(),
        modal_submit_button_text: $t({defaultMessage: "Close"}),
        close_on_submit: true,
        single_footer_button: true,
        on_click() {},
        id: "topic-title-suggestion-modal",
    });
}

export function check_topic_title(
    stream_id: number,
    topic_name: string,
): void {
    void channel.get({
        url: "/json/messages/topic-title-suggestion",
        data: {
            stream_id,
            topic_name,
        },
        success(response_data) {
            const data = topic_title_suggestion_schema.parse(response_data);

            if (data.drift_detected && data.suggested_title !== null) {
                show_topic_title_suggestion(data.suggested_title);
            }
        },
    });
}
