import os
import unittest

from mac_bridge_replay import validate_server_pid


class MacTelemetryTargetTests(unittest.TestCase):
    def test_rejects_non_server_pid(self):
        with self.assertRaises(RuntimeError):
            validate_server_pid(os.getpid())

    def test_accepts_server_command_shape(self):
        import mac_bridge_replay

        original = mac_bridge_replay.server_command
        try:
            mac_bridge_replay.server_command = lambda pid: "/bin/llama-server --port 18091"
            self.assertEqual(validate_server_pid(12345), "/bin/llama-server --port 18091")
        finally:
            mac_bridge_replay.server_command = original


if __name__ == "__main__":
    unittest.main()
