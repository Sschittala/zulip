# Implementation

## Feature 1: Message Recap

## Backend

I implemented the message recap feature primarily in zerver/views/message_recap.py and registered the endpoint in zproject/urls.py as /json/messages/recap. The endpoint retrieves the user's unread UserMessage objects and collects information such as the sender, message content. channel, message ID, and topic. These unread messages are sent to the configured LLM through the OpenAI-compatible API. The prompt asks the model to produce a concise recap containing important information, questions, action items, and decision. The API key is stored through Zulip's development secrets rather than being hard-coded or committed to Git.

## Links to Relevant Messages

The LLM does not generate message URLs. Instead, the backend creates links using Zulip's existing URL links in zerver/lib/url_encoding.py. Stream/channel messages use stream_message_url(), while direct messages use pm_message_url(). Each message returned by the recap endpoint includes a Zulip URL pointing to the original message. This avoids relying on the LLM to construct URLs and allows users to click a message reference in the recap and navigate to its original conversation.

## Frontend

The frontend is mostly implemented in web/src/message_recap.ts and web/templates/message_recap.hbs. I added message recap as a navigation item in web/src/navigation_views.ts and added the dedicated view container in templates/zerver/app/index.html. web/src/hashchange.ts handles the #message-recap route. When the page is opened, the frontend requests /json/messages/recap, and then it displays the generated summary, unread message count, and clickable references to the original messages. The view also displays a warning that AI summaries may contain errors because AI is not usually correct every time. I integrated the view with Zulip's existing message navigation through web/src/message_view.ts and web/src/left_sidebar_navigation_area.ts, allowing users to move between message recap and the various pre-existing features that have been implemented in Zulip.

## Feature 2: Topic Title Improver

## Backenc

I implemented this feature in zerver/views/topic_title_improver.py and registered /json/messages/topic-title-suggestion in zproject/urls.py. The endpoint receives a stream ID and topic name and retrieves up to the 10 most recent messages in that topic. If fewer than three messages exist, it returns without making an LLM request. Otherwise, the recent conversation and current topic title are sent to the LLM. The prompt asks the model to determine whether recent messages have consistently shifted away from the existing title. The LLM returns a structured JSON which contains drift_detected and suggested_title. A new title is suggested only when a good meaningful drift is detected.

## Latency, Cost, and Scalability

Topic analysis is triggered after a stream/channel message is successfully posted, so the suggestion appears while the conversation context is still fresh. To limit latency and token usage, only the 10 most recent messages are analyzed and no LLM request is made for topics with fewer than three messages. This essentialy means that it only looks at a small recent portion of the conversation instead of sending the entire topic history to the AI. Calling an external LLM after every channel message could become expensive at large scale and introduces network/API latency.. A good production implementation could limit these costs through caching, rate limiting, etc to determine whether an LLM call is necessary.

## Frontend

The frontend logic is implemented in web/src/topic_title_improver.ts and is triggered from web/src/compose.ts after a stream/channel message is successfully sent. When the backend detects topic drift, the frontend displays a dialog box containing the suggested replacement title, and also gives a brief message stating that the topic is being drifted. The feature suggests a title rather than automatically renaming the topic, leaving the final decision with the user to continue with the drifted topic or the previous topic. If no drift is detected, the dialog box will not get displayed.

**Demo Video:** 
