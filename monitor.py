#!/usr/bin/env python3
"""Public uptime state only. No customer or backup data is collected."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.request import Request, urlopen

HEALTH_URL = 'https://cdk.maple1189ai.com/health'
STATE = Path('status.json')


def probe():
    try:
        with urlopen(Request(HEALTH_URL, headers={'User-Agent': 'Maple-CDK-External-Monitor/1.0'}), timeout=10) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read(4096))
            return payload.get('status') == 'ok'
    except Exception:
        return False


def notify(message):
    token, chat = os.environ.get('CDK_TELEGRAM_BOT_TOKEN'), os.environ.get('CDK_TELEGRAM_CHAT_ID')
    if not token or not chat:
        return False
    try:
        request = Request('https://api.telegram.org/bot' + token + '/sendMessage',
            data=json.dumps({'chat_id': chat, 'text': message, 'disable_web_page_preview': True}).encode(),
            headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read(8192)).get('ok') is True
    except Exception:
        return False


def next_state(previous, available, now):
    status = 'up' if available else 'down'
    transition = previous.get('last_transition_at') if previous.get('status') == status else now
    return {'site': 'https://cdk.maple1189ai.com', 'status': status, 'checked_at': now,
            'last_transition_at': transition, 'notified_status': previous.get('notified_status', 'up')}


def run(test_notification=False):
    previous = json.loads(STATE.read_text()) if STATE.exists() else {}
    if not isinstance(previous, dict) or previous.get('status') not in (None, 'up', 'down'):
        raise ValueError('Invalid previous monitor state')
    available = False
    for attempt in range(3):
        if probe():
            available = True
            break
        if attempt < 2:
            time.sleep(10)
    now = datetime.now(timezone.utc).isoformat()
    current = next_state(previous, available, now)
    notification_ok = True
    if current['status'] != current['notified_status']:
        message = ('🍁 兑换站站外监控：连续 3 次无法确认网站正常，可能存在宕机或网络故障。请检查 https://cdk.maple1189ai.com 。没有重试任何付款。'
                   if not available else '🍁 兑换站站外监控：网站已恢复正常响应。请到后台查看订单与运行状态。')
        notification_ok = notify(message)
        if notification_ok:
            current['notified_status'] = current['status']
    if test_notification:
        notification_ok = notify('🍁 站外监控测试：GitHub 独立机器已成功检查兑换站。此消息用于验证手机提醒通道，不代表网站发生过故障。') and notification_ok
    # Public fields are deliberately allowlisted; never write API response bodies.
    STATE.write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': current['status'], 'notification_confirmed': notification_ok}))
    return 0 if notification_ok else 1


if __name__ == '__main__':
    try:
        raise SystemExit(run(os.environ.get('TEST_NOTIFICATION') == 'true'))
    except (ValueError, OSError):
        raise SystemExit('Monitor state could not be verified; no credentials or response contents were logged') from None
