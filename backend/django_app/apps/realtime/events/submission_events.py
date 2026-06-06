"""
WebSocket event type constants for the submission channel.

The value doubles as the Channels message ``type`` key and maps to the handler
method ``SubmissionConsumer.submission_update``. Do not change the value without
renaming the matching consumer method and updating the frontend.
"""


class SubmissionEvents:
    SUBMISSION_UPDATE = "submission_update"
