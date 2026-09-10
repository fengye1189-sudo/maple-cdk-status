import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import monitor


class MonitorTests(unittest.TestCase):
    def execute(self, previous, probes, notification=True):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'status.json'
            state.write_text(json.dumps(previous))
            with patch.object(monitor, 'STATE', state), patch.object(monitor, 'probe', side_effect=probes) as probe, \
                 patch.object(monitor, 'notify', return_value=notification) as notify, patch.object(monitor.time, 'sleep'):
                result = monitor.run()
            return json.loads(state.read_text()), result, probe.call_count, notify.call_count

    def test_healthy_stays_quiet(self):
        state, code, checks, notices = self.execute({'status': 'up', 'notified_status': 'up'}, [True])
        self.assertEqual((code, checks, notices), (0, 1, 0))
        self.assertEqual(state['status'], 'up')

    def test_three_failures_alert_once(self):
        state, code, checks, notices = self.execute({'status': 'up', 'notified_status': 'up'}, [False]*3)
        self.assertEqual((code, checks, notices), (0, 3, 1))
        self.assertEqual(state['notified_status'], 'down')
        _, _, _, repeated = self.execute(state, [False]*3)
        self.assertEqual(repeated, 0)

    def test_recovery_notifies(self):
        state, code, _, notices = self.execute({'status': 'down', 'notified_status': 'down'}, [True])
        self.assertEqual((code, notices), (0, 1))
        self.assertEqual(state['notified_status'], 'up')

    def test_transient_failure_does_not_alert(self):
        _, code, checks, notices = self.execute({'status': 'up', 'notified_status': 'up'}, [False, True])
        self.assertEqual((code, checks, notices), (0, 2, 0))

    def test_failed_notification_remains_pending(self):
        state, code, _, notices = self.execute({'status': 'up', 'notified_status': 'up'}, [False]*3, False)
        self.assertEqual((code, notices), (1, 1))
        self.assertEqual(state['notified_status'], 'up')


if __name__ == '__main__':
    unittest.main()
