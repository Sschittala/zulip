import {$} from "jquery";
import * as z from "zod/mini";

import render_message_recap from "../templates/message_recap.hbs";

import * as channel from "./channel.ts";
import * as left_sidebar_navigation_area from "./left_sidebar_navigation_area.ts";
import * as rendered_markdown from "./rendered_markdown.ts";
import * as views_util from "./views_util.ts";

const recap_response_schema = z.object({
    unread_count: z.number(),
    recap: z.string(),
    messages: z.array(
        z.object({
            id: z.number(),
            sender: z.string(),
            content: z.string(),
            type: z.string(),
            channel_id: z.nullable(z.number()),
            channel: z.nullable(z.string()),
            topic: z.nullable(z.string()),
            url: z.string(),
        }),
    ),
});

let hide_other_views_callback: (() => void) | undefined;
let visible = false;
export function is_visible(): boolean {
    return visible;
}

export function show(): void {
    if (hide_other_views_callback !== undefined) {
        hide_other_views_callback();
    }

    views_util.handle_message_view_deactivated(
        left_sidebar_navigation_area.highlight_message_recap_view,
    );

    const $view = $("#message-recap-view");
    const $pane = $("#message-recap-pane");

    $("#message_feed_container").hide();
    $view.show();
    visible = true;

    $pane.html(`
        <div class="message-recap-loading">
            <h1>Message Recap</h1>
            <p>Generating recap of your unread messages...</p>
        </div>
    `);

    void channel.get({
        url: "/json/messages/recap",
        data: {},
        success(response_data) {
            const data = recap_response_schema.parse(response_data);

            const recap_html = render_message_recap({
                recap: data.recap,
                unread_count: data.unread_count,
                messages: data.messages,
            });

            $pane.html(`
                <div class="message-recap-page">
                    <h1>Message Recap</h1>
                    ${recap_html}
                    <p><em>AI summaries may have errors.</em></p>
                </div>
            `);

            $pane.addClass("rendered_markdown");
            rendered_markdown.update_elements($pane);
        },
    });
}

export function hide(): void {
    if (!visible) {
        return;
    }

    $("#message-recap-view").hide();
    $("#message_feed_container").show();
    visible = false;
}

export function initialize({
    hide_other_views,
}: {
    hide_other_views: () => void;
}): void {
    hide_other_views_callback = hide_other_views;
}
