"""Reject messages that could misroute work or falsely advance receipt state."""
from copy import deepcopy
import unittest

from tools.mailbox import validate


MESSAGE = {
    "id": "agent1-0001", "sequence": 1, "sent_at": "2026-10-18T01:00:00Z",
    "kind": "request", "task": "geometry-v1", "in_reply_to": None,
    "summary": "Implement the approved geometry API.", "body": ["See the architecture."],
    "commits": [], "paths": ["src/geometry/"], "checks": [], "needs_reply": True,
}
ENVELOPE = {
    "protocol_version": 1, "from": "agent1", "to": "agent2", "branch": "agent1",
    "last_sequence": 1, "ack_sequence": 0, "messages": [MESSAGE],
}


class ProtocolTests(unittest.TestCase):
    def rejected(self, change):
        value = deepcopy(ENVELOPE)
        change(value)
        with self.assertRaises(ValueError):
            validate(value, "agent1")

    def test_accept_valid_request(self):
        validate(deepcopy(ENVELOPE), "agent1")

    def test_accept_empty_unstarted_mailbox(self):
        value = deepcopy(ENVELOPE)
        value.update(last_sequence=0, messages=[])
        validate(value, "agent1")

    def test_reject_wrong_recipient(self):
        self.rejected(lambda value: value.update(to="agent1"))

    def test_reject_sequence_gap(self):
        self.rejected(lambda value: value["messages"][0].update(sequence=2, id="agent1-0002"))

    def test_reject_wrong_sender_id(self):
        self.rejected(lambda value: value["messages"][0].update(id="agent2-0001"))

    def test_reject_receipt_boolean(self):
        self.rejected(lambda value: value.update(ack_sequence=True))

    def test_reject_repository_escape(self):
        for path in ("../outside", "/outside"):
            with self.subTest(path=path):
                self.rejected(lambda value: value["messages"][0].update(paths=[path]))

    def test_reject_invalid_timestamp(self):
        for timestamp in ("yesterdayZ", "2026-10-18Z", "2026-10-18T01:00:00+03:00"):
            with self.subTest(timestamp=timestamp):
                self.rejected(lambda value: value["messages"][0].update(sent_at=timestamp))

    def test_reject_unrecognized_fields(self):
        self.rejected(lambda value: value.update(delivered=True))

    def test_reject_reply_to_own_message(self):
        self.rejected(lambda value: value["messages"][0].update(in_reply_to="agent1-0001"))

    def test_reject_bad_commit_reference(self):
        self.rejected(lambda value: value["messages"][0].update(commits=["HEAD"]))

    def test_reject_mismatched_last_sequence(self):
        self.rejected(lambda value: value.update(last_sequence=2))


if __name__ == "__main__":
    unittest.main()
