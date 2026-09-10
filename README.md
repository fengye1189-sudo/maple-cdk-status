# 🍁 MaplePass 兑换站在线状态

[![站外巡检](https://github.com/fengye1189-sudo/maple-cdk-status/actions/workflows/uptime.yml/badge.svg)](https://github.com/fengye1189-sudo/maple-cdk-status/actions/workflows/uptime.yml)

这里只公开 https://cdk.maple1189ai.com 是否响应正常以及检查时间，最新结果见 [status.json](status.json)。不包含订单、卡密、支付卡、备份或任何登录凭据。

巡检由 GitHub 托管机器运行，计划每 5 分钟一次。连续三次探测失败才发送 Telegram 提醒，恢复后再发恢复提醒；持续相同状态不重复提醒。GitHub 定时任务可能排队、延迟或丢弃，因此这是基础站外巡检，不是保证 5 分钟内响应的 SLA。

仓库仅使用标准 Linux 托管运行器；通知凭据位于 GitHub Actions Secrets。没有开启 GitHub Pages、收费运行器或付款功能。备份在另一个私有项目中，绝不上传至此仓库。

工作流若长期未运行，需检查 GitHub Actions 是否被停用。网页工作流绿色只代表巡检执行成功，网站真正状态以 status.json 的 `status` 和 `checked_at` 为准。
