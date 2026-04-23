#!/usr/bin/env python3
"""
Automated Report Generator - Lobster Edition
=============================================
Generate and deliver automated reports.

Features:
- Daily/weekly/monthly reports
- Clan activity reports
- Portfolio performance reports
- Email delivery (AgentMail)
- Discord webhook delivery
- HTML/PDF/Markdown export

Usage:
    python3 tools/auto-report.py --type daily --output report.html
    python3 tools/auto-report.py --type clan --clan "Lords of Arcadia" --email user@example.com
    python3 tools/auto-report.py --type portfolio --webhook https://discord.com/webhook/...
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

try:
    import requests
except ImportError:
    print("requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def log(message: str = "", *, enabled: bool = True) -> None:
    """Print only when human-readable output is enabled."""
    if enabled:
        print(message)


def generate_html_report(report_type: str, data: Dict[str, Any]) -> str:
    """Generate HTML report from template."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report_type.title()} Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #FF4500; border-bottom: 3px solid #FF4500; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        .stat {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 4px; min-width: 150px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #FF4500; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #FF4500; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report_type.title()} Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""

    if report_type == "daily":
        html += """
        <h2>Daily Summary</h2>
        <div class="stat">
            <div class="stat-value">""" + str(data.get("clan_members", "N/A")) + """</div>
            <div class="stat-label">Clan Members</div>
        </div>
        <div class="stat">
            <div class="stat-value">""" + str(data.get("citadel_caps", "N/A")) + """</div>
            <div class="stat-label">Citadel Caps</div>
        </div>
        <div class="stat">
            <div class="stat-value">""" + str(data.get("portfolio_value", "N/A")) + """</div>
            <div class="stat-label">Portfolio Value</div>
        </div>
"""
    elif report_type == "clan":
        html += f"""
        <h2>Clan: {data.get('clan_name', 'Unknown')}</h2>
        <div class="stat">
            <div class="stat-value">{data.get('total_members', 'N/A')}</div>
            <div class="stat-label">Total Members</div>
        </div>
        <div class="stat">
            <div class="stat-value">{data.get('total_xp', 'N/A')}</div>
            <div class="stat-label">Total XP</div>
        </div>
        <div class="stat">
            <div class="stat-value">{data.get('capped_count', 'N/A')}</div>
            <div class="stat-label">Citadel Caps</div>
        </div>

        <h3>Top Members</h3>
        <table>
            <tr><th>Rank</th><th>Member</th><th>XP</th></tr>
"""
        for index, member in enumerate(data.get("top_members", [])[:10], 1):
            html += (
                f"<tr><td>{index}</td><td>{member.get('name', 'Unknown')}</td>"
                f"<td>{member.get('total_xp', 0):,}</td></tr>\n"
            )
        html += "        </table>\n"
    elif report_type == "portfolio":
        html += f"""
        <h2>Portfolio Performance</h2>
        <div class="stat">
            <div class="stat-value">{data.get('total_value', 'N/A')}</div>
            <div class="stat-label">Total Value</div>
        </div>
        <div class="stat">
            <div class="stat-value {'positive' if data.get('profit_loss', 0) >= 0 else 'negative'}">{data.get('profit_loss', 0):,}</div>
            <div class="stat-label">Profit/Loss</div>
        </div>
        <div class="stat">
            <div class="stat-value {'positive' if data.get('roi', 0) >= 0 else 'negative'}">{data.get('roi', 0):+.2f}%</div>
            <div class="stat-label">ROI</div>
        </div>
"""

    html += """
        <div class="footer">
            <p>Generated by RS-Agent-Skill-Lobster-Edition</p>
            <p>https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(to: str, subject: str, html_content: str, *, human_mode: bool) -> bool:
    """Send email via AgentMail."""
    agentmail_script = Path("skills/agentmail/scripts/send_email.py")
    if not agentmail_script.exists():
        log("AgentMail not found, skipping email delivery", enabled=human_mode)
        return False

    try:
        subprocess.run(
            [
                sys.executable,
                str(agentmail_script),
                "--inbox",
                "duckbot@agentmail.to",
                "--to",
                to,
                "--subject",
                subject,
                "--html",
                html_content,
            ],
            check=True,
        )
        return True
    except Exception as exc:
        log(f"Failed to send email: {exc}", enabled=human_mode)
        return False


def send_discord_webhook(webhook_url: str, content: str, *, human_mode: bool) -> bool:
    """Send message to Discord webhook."""
    try:
        response = requests.post(webhook_url, json={"content": content}, timeout=10)
        return response.status_code == 204
    except Exception as exc:
        log(f"Failed to send Discord webhook: {exc}", enabled=human_mode)
        return False


def get_clan_data(clan_name: str) -> Dict[str, Any]:
    """Get clan data for report."""
    try:
        result = subprocess.run(
            [sys.executable, "tools/runescape-api.py", "--clan", clan_name, "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 or not result.stdout:
            return {}
        return json.loads(result.stdout)
    except Exception:
        return {}


def get_portfolio_data() -> Dict[str, Any]:
    """Get portfolio data for report."""
    try:
        result = subprocess.run(
            [sys.executable, "tools/portfolio-tracker.py", "--view", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 or not result.stdout:
            return {}
        return json.loads(result.stdout)
    except Exception:
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated Report Generator - Lobster Edition")
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=["daily", "weekly", "monthly", "clan", "portfolio"],
        help="Report type",
    )
    parser.add_argument("--clan", type=str, help="Clan name (for clan reports)")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--email", type=str, help="Send to email address")
    parser.add_argument("--webhook", type=str, help="Discord webhook URL")
    parser.add_argument(
        "--format",
        type=str,
        default="html",
        choices=["html", "markdown", "json"],
        help="Output format",
    )
    parser.add_argument("--json", dest="format", action="store_const", const="json", help="Alias for --format json")

    args = parser.parse_args()
    json_mode = args.format == "json"
    human_mode = not json_mode

    log(f"\nGenerating {args.type} report...", enabled=human_mode)

    data: Dict[str, Any] = {}
    if args.type == "clan" and args.clan:
        data = get_clan_data(args.clan)
        data["clan_name"] = args.clan
    elif args.type == "portfolio":
        data = get_portfolio_data()
    else:
        if args.clan:
            data["clan_data"] = get_clan_data(args.clan)
        data["portfolio_data"] = get_portfolio_data()
        data["clan_members"] = data.get("clan_data", {}).get("total_members", "N/A")
        data["citadel_caps"] = "N/A"
        data["portfolio_value"] = data.get("portfolio_data", {}).get("total_current_value", "N/A")

    html_content = None
    if args.format == "html":
        html_content = generate_html_report(args.type, data)
        content = html_content
    elif args.format == "json":
        content = json.dumps(data, indent=2)
    else:
        content = f"# {args.type.title()} Report\n\nGenerated: {datetime.now()}\n\nData: {json.dumps(data, indent=2)}"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            file.write(content)
        log(f"Report saved to: {args.output}", enabled=human_mode)

    if args.email:
        if html_content is None:
            html_content = generate_html_report(args.type, data)
        subject = f"{args.type.title()} Report - {datetime.now().strftime('%Y-%m-%d')}"
        if send_email(args.email, subject, html_content, human_mode=human_mode):
            log(f"Email sent to: {args.email}", enabled=human_mode)

    if args.webhook:
        summary = f"**{args.type.title()} Report**\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        if args.type == "clan" and data.get("total_members"):
            summary += f"Members: {data['total_members']}\n"
        if args.type == "portfolio" and data.get("total_value"):
            summary += f"Value: {data.get('total_value', 'N/A')}\n"
        if args.output:
            summary += f"\n[View Full Report]({args.output})"

        if send_discord_webhook(args.webhook, summary, human_mode=human_mode):
            log("Discord notification sent", enabled=human_mode)

    if json_mode:
        print(content)
        return

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Report type: {args.type}")
    print(f"Format: {args.format}")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


if __name__ == "__main__":
    main()
