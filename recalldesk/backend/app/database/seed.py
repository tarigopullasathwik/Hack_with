"""
Seed realistic synthetic demo data into SQLite and pre-load Hindsight memory banks.

Run: python -m app.database.seed
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datetime import datetime, timezone, timedelta
from app.database.db import engine, SessionLocal
from app.models import (
    Customer, CustomerPlan, CustomerStatus,
    Ticket, TicketStatus, TicketPriority, TicketCategory,
    Message, MessageRole,
    KnowledgeArticle, ArticleCategory,
    DemoScenario,
)
from app.database.db import Base

Base.metadata.create_all(bind=engine)
db = SessionLocal()


# ─── Helper ──────────────────────────────────────────────────────────────────
def ago(days: int, hours: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days, hours=hours)


# ─── Clear existing data ──────────────────────────────────────────────────────
for model in [Message, Ticket, DemoScenario, KnowledgeArticle, Customer]:
    db.query(model).delete()
db.commit()
print("Cleared existing data.")


# ─── Customers ────────────────────────────────────────────────────────────────
customers = [
    Customer(
        id="cust-001",
        name="Sarah Mitchell",
        email="sarah.mitchell@vertexlabs.io",
        company="Vertex Labs",
        plan=CustomerPlan.BUSINESS,
        status=CustomerStatus.ACTIVE,
        browser="Chrome 124",
        operating_system="Windows 11",
        product_version="4.2.1",
        workspace_size="28 members",
        profile_notes="Primary admin for Vertex Labs workspace. High-value customer, Business plan.",
        preferences=json.dumps({"communication": "email", "escalation_preference": "human_first"}),
    ),
    Customer(
        id="cust-002",
        name="Marcus Chen",
        email="marcus.chen@techflow.com",
        company="TechFlow Solutions",
        plan=CustomerPlan.ENTERPRISE,
        status=CustomerStatus.ACTIVE,
        browser="Firefox 125",
        operating_system="macOS Sonoma",
        product_version="4.2.1",
        workspace_size="150 members",
        profile_notes="DevOps lead. Manages SSO and API integrations. Critical enterprise customer.",
        preferences=json.dumps({"communication": "slack", "preferred_contact": "morning"}),
    ),
    Customer(
        id="cust-003",
        name="Priya Sharma",
        email="priya.sharma@growthco.io",
        company="GrowthCo",
        plan=CustomerPlan.STARTER,
        status=CustomerStatus.ACTIVE,
        browser="Safari 17",
        operating_system="macOS Ventura",
        product_version="4.1.9",
        workspace_size="8 members",
        profile_notes="Marketing director. Often reports notification issues.",
        preferences=json.dumps({"communication": "email"}),
    ),
    Customer(
        id="cust-004",
        name="James Okonkwo",
        email="james.o@finbridge.co",
        company="FinBridge Capital",
        plan=CustomerPlan.BUSINESS,
        status=CustomerStatus.ACTIVE,
        browser="Edge 124",
        operating_system="Windows 10",
        product_version="4.2.0",
        workspace_size="45 members",
        profile_notes="Finance team admin. Multiple billing issues on record.",
        preferences=json.dumps({"communication": "phone", "billing_contact": "direct"}),
    ),
    Customer(
        id="cust-005",
        name="Elena Rodriguez",
        email="elena.r@designstudio.mx",
        company="Design Studio MX",
        plan=CustomerPlan.STARTER,
        status=CustomerStatus.ACTIVE,
        browser="Chrome 123",
        operating_system="macOS",
        product_version="4.2.1",
        workspace_size="5 members",
        profile_notes="Creative director. Frequent file sync issues.",
        preferences=json.dumps({}),
    ),
    Customer(
        id="cust-006",
        name="David Park",
        email="david.park@nexoratest.io",
        company="NexoraTest Inc",
        plan=CustomerPlan.FREE,
        status=CustomerStatus.ACTIVE,
        browser="Chrome 124",
        operating_system="Linux",
        product_version="4.2.1",
        workspace_size="2 members",
        profile_notes="Developer testing integration APIs.",
        preferences=json.dumps({}),
    ),
    Customer(
        id="cust-007",
        name="Aisha Thompson",
        email="aisha.t@cloudworks.ai",
        company="CloudWorks AI",
        plan=CustomerPlan.BUSINESS,
        status=CustomerStatus.ACTIVE,
        browser="Chrome 124",
        operating_system="Windows 11",
        product_version="4.2.1",
        workspace_size="32 members",
        profile_notes="Operations lead. SSO issues due to company policy changes.",
        preferences=json.dumps({"communication": "email"}),
    ),
    Customer(
        id="cust-008",
        name="Robert Kim",
        email="robert.kim@manufactura.co",
        company="Manufactura Co",
        plan=CustomerPlan.STARTER,
        status=CustomerStatus.ACTIVE,
        browser="Chrome 122",
        operating_system="Windows 10",
        product_version="4.1.8",
        workspace_size="12 members",
        profile_notes="IT manager. Permission and workspace config issues.",
        preferences=json.dumps({}),
    ),
    Customer(
        id="cust-009",
        name="Fatima Al-Hassan",
        email="fatima.h@meridian.ae",
        company="Meridian Group",
        plan=CustomerPlan.ENTERPRISE,
        status=CustomerStatus.ACTIVE,
        browser="Safari 17",
        operating_system="macOS",
        product_version="4.2.1",
        workspace_size="200 members",
        profile_notes="Enterprise account manager. High-priority customer.",
        preferences=json.dumps({"escalation_preference": "direct_call"}),
    ),
    Customer(
        id="cust-010",
        name="Tom Briggs",
        email="tom.briggs@localagency.uk",
        company="Local Agency UK",
        plan=CustomerPlan.FREE,
        status=CustomerStatus.ACTIVE,
        browser="Firefox 124",
        operating_system="Windows 11",
        product_version="4.2.0",
        workspace_size="3 members",
        profile_notes="New customer, few interactions.",
        preferences=json.dumps({}),
    ),
]
for c in customers:
    db.add(c)
db.commit()
print(f"Inserted {len(customers)} customers.")


# ─── Knowledge Base Articles ───────────────────────────────────────────────
articles = [
    KnowledgeArticle(
        id="kb-001",
        title="Payment Failure: How to Resolve Billing Issues",
        category=ArticleCategory.BILLING,
        content=(
            "Payment failures on Nexora Workspace can occur due to expired cards, "
            "incomplete billing profiles, or bank authorization issues. "
            "Common resolution: update billing profile, verify card details, retry payment. "
            "If the issue persists after profile update, contact your bank or use a different card."
        ),
        tags="payment,billing,card,failure,upgrade",
        troubleshooting_steps=json.dumps([
            "Verify card expiry date and billing address",
            "Update billing profile in Settings > Billing",
            "Clear browser cache and cookies",
            "Retry payment in an incognito/private window",
            "Try a different payment method",
            "Check for bank authorization hold",
        ]),
        common_causes=json.dumps([
            "Expired credit card",
            "Incomplete billing address",
            "Bank fraud detection block",
            "3D Secure authentication failure",
        ]),
        escalation_triggers=json.dumps(["Dispute over charged amount", "Unauthorized charge"]),
    ),
    KnowledgeArticle(
        id="kb-002",
        title="Login Issues and Password Reset",
        category=ArticleCategory.LOGIN,
        content=(
            "If you cannot log in to Nexora Workspace, start by using the password reset flow. "
            "If SSO is enabled on your account, you must use your company's identity provider. "
            "Browser extensions can sometimes block authentication. "
            "MFA issues: ensure your authenticator app time is synchronized."
        ),
        tags="login,password,reset,access,locked,mfa",
        troubleshooting_steps=json.dumps([
            "Use 'Forgot Password' on the login page",
            "Check for MFA/2FA issues (time sync on authenticator app)",
            "Disable browser extensions temporarily",
            "Try in incognito/private window",
            "Clear browser cache and cookies",
            "Check if account is locked (contact admin)",
        ]),
        common_causes=json.dumps([
            "Forgotten password",
            "MFA token out of sync",
            "Browser extension interference",
            "Account locked after failed attempts",
        ]),
        escalation_triggers=json.dumps(["Suspected account compromise", "Admin locked account"]),
    ),
    KnowledgeArticle(
        id="kb-003",
        title="SSO Configuration and Troubleshooting",
        category=ArticleCategory.SSO,
        content=(
            "Nexora Workspace supports SAML 2.0 and OIDC SSO. "
            "Common issues: certificate expiry, misconfigured callback URLs, attribute mapping errors. "
            "To reconnect SSO: go to Settings > Security > SSO and re-authenticate your identity provider. "
            "Test with a non-admin account before rolling out."
        ),
        tags="sso,saml,oidc,authentication,oauth,identity",
        troubleshooting_steps=json.dumps([
            "Verify SSO certificate is not expired",
            "Check callback/redirect URLs match exactly",
            "Verify attribute mapping (email, name, groups)",
            "Re-initiate OAuth handshake from Settings > Security > SSO",
            "Test with a test user account first",
            "Review IDP logs for error codes",
        ]),
        common_causes=json.dumps([
            "Expired SAML certificate",
            "Incorrect redirect URI",
            "Attribute mapping mismatch",
            "IDP policy change",
        ]),
        escalation_triggers=json.dumps(["All users locked out", "Certificate rotation needed"]),
    ),
    KnowledgeArticle(
        id="kb-004",
        title="File Synchronization Problems",
        category=ArticleCategory.FILE_SYNC,
        content=(
            "File sync issues in Nexora Workspace are often caused by network connectivity, "
            "conflicting edits, or storage quota exceeded. "
            "Force a manual sync via the workspace sidebar. "
            "Conflicts show as duplicate files with '(conflict)' suffix."
        ),
        tags="sync,files,conflict,upload,download,storage",
        troubleshooting_steps=json.dumps([
            "Check storage quota in Settings > Storage",
            "Force manual sync: workspace sidebar > Sync Now",
            "Check network connectivity and proxy settings",
            "Resolve conflict files (keep latest or merge)",
            "Disable then re-enable desktop sync client",
            "Check file size limits (max 5GB per file on Business plan)",
        ]),
        common_causes=json.dumps([
            "Storage quota exceeded",
            "Network interruption during sync",
            "Concurrent edit conflicts",
            "Outdated desktop client version",
        ]),
        escalation_triggers=json.dumps(["Data loss suspected", "Corruption detected"]),
    ),
    KnowledgeArticle(
        id="kb-005",
        title="API and Integration Failures",
        category=ArticleCategory.API,
        content=(
            "Nexora Workspace API uses OAuth 2.0. API errors are often caused by expired tokens, "
            "incorrect scopes, or rate limiting. "
            "Regenerate API keys from Settings > API > Manage Keys. "
            "Check rate limits: 100 req/min on Starter, 1000 req/min on Business."
        ),
        tags="api,integration,oauth,token,webhook,rate limit,key",
        troubleshooting_steps=json.dumps([
            "Verify API key is active (Settings > API > Manage Keys)",
            "Check OAuth token expiry and refresh flow",
            "Verify API scopes match required permissions",
            "Check rate limit headers in response",
            "Regenerate API key if compromised",
            "Re-authorize OAuth connection",
        ]),
        common_causes=json.dumps([
            "Expired OAuth token",
            "Missing API scope",
            "Rate limit exceeded",
            "API key revoked or rotated",
        ]),
        escalation_triggers=json.dumps(["Security breach suspected", "Webhook delivery failures > 24h"]),
    ),
    KnowledgeArticle(
        id="kb-006",
        title="Workspace Permissions and Access Control",
        category=ArticleCategory.PERMISSIONS,
        content=(
            "Permission issues often occur after role changes or workspace reorganization. "
            "Admins can manage roles in Settings > Members. "
            "Inherited permissions from groups override individual settings. "
            "Guest users have read-only access by default."
        ),
        tags="permissions,access,role,admin,member,guest",
        troubleshooting_steps=json.dumps([
            "Check user role in Settings > Members",
            "Verify group membership and inherited permissions",
            "Re-add user to workspace if removed",
            "Clear permission cache (Admin panel > Cache > Clear)",
            "Check if workspace is in lockdown mode",
        ]),
        common_causes=json.dumps([
            "Role accidentally changed",
            "Group membership removed",
            "Workspace restructuring",
            "Admin privilege revoked",
        ]),
        escalation_triggers=json.dumps(["Admin locked out", "Accidental mass permission change"]),
    ),
    KnowledgeArticle(
        id="kb-007",
        title="Subscription Upgrade and Downgrade",
        category=ArticleCategory.SUBSCRIPTION,
        content=(
            "Upgrades are immediate; downgrades take effect at the next billing cycle. "
            "Data is never deleted during downgrade but access to premium features is suspended. "
            "Proration applies for mid-cycle upgrades. "
            "Upgrade at Settings > Billing > Change Plan."
        ),
        tags="subscription,upgrade,downgrade,plan,billing,proration",
        troubleshooting_steps=json.dumps([
            "Navigate to Settings > Billing > Change Plan",
            "Verify payment method is valid before upgrading",
            "Complete billing profile if not already done",
            "Check for pending invoice before plan change",
            "Contact billing if proration appears incorrect",
        ]),
        common_causes=json.dumps([
            "Incomplete billing profile blocking upgrade",
            "Expired payment method",
            "Confusion about proration",
        ]),
        escalation_triggers=json.dumps(["Charged incorrectly after plan change"]),
    ),
    KnowledgeArticle(
        id="kb-008",
        title="Notification Settings and Delivery Issues",
        category=ArticleCategory.NOTIFICATIONS,
        content=(
            "Nexora Workspace sends notifications via in-app, email, and optional Slack/Teams integration. "
            "If notifications are not arriving: check notification preferences, spam folder, and DND schedule. "
            "Email notifications require a verified email address."
        ),
        tags="notifications,email,slack,teams,alerts,digest",
        troubleshooting_steps=json.dumps([
            "Check notification preferences in Settings > Notifications",
            "Verify email address is confirmed",
            "Check spam/junk folder",
            "Disable Do Not Disturb schedule if set",
            "Re-authorize Slack/Teams integration",
            "Check firewall/email filter rules",
        ]),
        common_causes=json.dumps([
            "Notifications turned off in settings",
            "Email in spam folder",
            "Do Not Disturb schedule active",
            "Integration token expired",
        ]),
        escalation_triggers=json.dumps(["Critical alert delivery failure"]),
    ),
    KnowledgeArticle(
        id="kb-009",
        title="Account Access and Security",
        category=ArticleCategory.ACCOUNT,
        content=(
            "Account security issues include locked accounts, suspicious login alerts, "
            "and unauthorized access concerns. "
            "Enable 2FA at Settings > Security > Two-Factor Authentication. "
            "Review active sessions at Settings > Security > Active Sessions."
        ),
        tags="account,security,locked,2fa,mfa,suspicious,access",
        troubleshooting_steps=json.dumps([
            "Review active sessions (Settings > Security > Active Sessions)",
            "Change password immediately if compromise suspected",
            "Enable 2FA if not already active",
            "Check login history for unrecognized access",
            "Revoke all sessions and log in fresh",
        ]),
        common_causes=json.dumps([
            "Phishing attack",
            "Weak password reused from breach",
            "Shared credentials",
            "Device stolen/lost",
        ]),
        escalation_triggers=json.dumps(["Confirmed unauthorized access", "Data exfiltration suspected"]),
    ),
    KnowledgeArticle(
        id="kb-010",
        title="Workspace Configuration and Setup",
        category=ArticleCategory.PERMISSIONS,
        content=(
            "Initial workspace setup includes configuring teams, channels, and integrations. "
            "Common first-time issues: email domain not verified, SSO not configured, "
            "seats limit reached, or workspace URL taken. "
            "Use the Setup Wizard at Settings > Workspace > Setup."
        ),
        tags="setup,configuration,workspace,domain,seats,onboarding",
        troubleshooting_steps=json.dumps([
            "Complete workspace setup wizard",
            "Verify company email domain",
            "Configure SSO before inviting users (if applicable)",
            "Set workspace name and URL",
            "Configure default notification settings",
            "Assign admin roles",
        ]),
        common_causes=json.dumps([
            "Incomplete initial setup",
            "Domain not verified",
            "SSO config incomplete",
        ]),
        escalation_triggers=json.dumps(["Enterprise migration failing"]),
    ),
    KnowledgeArticle(
        id="kb-011",
        title="Clearing Browser Cache for Nexora Workspace",
        category=ArticleCategory.LOGIN,
        content=(
            "Clearing browser cache resolves many display and authentication glitches. "
            "Chrome: Settings > Privacy > Clear Browsing Data > select Cached images and files + Cookies. "
            "Note: this is a general troubleshooting step and does NOT fix underlying billing or account issues."
        ),
        tags="cache,browser,clear,chrome,firefox,safari,cookies",
        troubleshooting_steps=json.dumps([
            "Chrome: Ctrl+Shift+Delete > Cached images and Cookies > Clear data",
            "Firefox: Ctrl+Shift+Delete > Cache > Clear Now",
            "Safari: Develop > Empty Caches",
            "Reload page after clearing",
        ]),
        common_causes=json.dumps([
            "Stale authentication token in cache",
            "Outdated JS bundle cached",
        ]),
        escalation_triggers=json.dumps([]),
    ),
]
for a in articles:
    db.add(a)
db.commit()
print(f"Inserted {len(articles)} knowledge articles.")


# ─── Historical tickets and interactions ──────────────────────────────────────

tickets_data = [
    # Sarah Mitchell — Scenario 1: Recurring billing (MAIN DEMO CUSTOMER)
    Ticket(
        id="TKT-SM001",
        customer_id="cust-001",
        title="Payment failed during Business plan upgrade",
        description="Credit card declined when attempting to upgrade from Starter to Business plan.",
        category=TicketCategory.BILLING,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.HIGH,
        resolution="Updated billing profile with correct billing address; payment succeeded.",
        resolution_steps=json.dumps([
            "Cleared browser cache (FAILED — did not resolve payment)",
            "Updated billing profile with correct billing address",
            "Retried payment — succeeded",
        ]),
        failed_steps=json.dumps(["Clear browser cache"]),
        successful_step="Update billing profile with correct billing address",
        created_at=ago(25),
        updated_at=ago(24),
        resolved_at=ago(24),
    ),
    Ticket(
        id="TKT-SM002",
        customer_id="cust-001",
        title="Slack integration stopped sending notifications",
        description="Slack notifications for workspace activity stopped arriving after workspace rename.",
        category=TicketCategory.INTEGRATION,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.MEDIUM,
        resolution="Re-authorized Slack OAuth connection. Notifications resumed.",
        resolution_steps=json.dumps([
            "Checked notification settings (looked fine)",
            "Re-authorized Slack OAuth integration",
            "Notifications resumed",
        ]),
        failed_steps=json.dumps([]),
        successful_step="Re-authorize Slack OAuth integration from Settings > Integrations > Slack",
        created_at=ago(12),
        updated_at=ago(11),
        resolved_at=ago(11),
    ),
    Ticket(
        id="TKT-SM003",
        customer_id="cust-001",
        title="Annual subscription renewal payment failing",
        description="Cannot process annual renewal payment — getting 'Payment declined' error.",
        category=TicketCategory.BILLING,
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        created_at=ago(0, 2),  # 2 hours ago (current)
        updated_at=ago(0, 2),
    ),

    # Marcus Chen — Scenario 2: Repeated integration failure
    Ticket(
        id="TKT-MC001",
        customer_id="cust-002",
        title="SSO SAML certificate expired — all users locked out",
        description="SAML certificate expired, company-wide SSO login failure.",
        category=TicketCategory.LOGIN,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.CRITICAL,
        resolution="Renewed SAML certificate on IDP, re-uploaded to Nexora SSO settings.",
        resolution_steps=json.dumps([
            "Verified certificate expiry — confirmed expired",
            "Renewed certificate on Okta IDP",
            "Uploaded new certificate to Nexora Settings > Security > SSO",
            "Tested with 3 users — confirmed working",
        ]),
        successful_step="Renew SAML certificate on IDP and re-upload to Nexora SSO",
        created_at=ago(60),
        resolved_at=ago(59),
    ),
    Ticket(
        id="TKT-MC002",
        customer_id="cust-002",
        title="API integration rate limiting causing CI/CD failures",
        description="Automated deployments failing due to API rate limit errors (429).",
        category=TicketCategory.API,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.HIGH,
        resolution="Implemented exponential backoff; upgraded to Enterprise API tier.",
        successful_step="Implement exponential backoff and upgrade API tier",
        created_at=ago(30),
        resolved_at=ago(29),
    ),
    Ticket(
        id="TKT-MC003",
        customer_id="cust-002",
        title="SSO SAML authentication failing again for new employee batch",
        description="New employees cannot authenticate via SSO — existing employees unaffected.",
        category=TicketCategory.LOGIN,
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        created_at=ago(0, 1),
        updated_at=ago(0, 1),
    ),

    # James Okonkwo — Scenario 3: Escalation after failed troubleshooting
    Ticket(
        id="TKT-JO001",
        customer_id="cust-004",
        title="Invoices not generating for Business plan",
        description="Monthly invoices not appearing in billing dashboard for 2 months.",
        category=TicketCategory.BILLING,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.HIGH,
        resolution="Billing webhook was disabled; re-enabled invoice generation.",
        successful_step="Re-enable billing webhook in admin panel",
        created_at=ago(45),
        resolved_at=ago(44),
    ),
    Ticket(
        id="TKT-JO002",
        customer_id="cust-004",
        title="Double-charged for January subscription",
        description="Invoice shows two charges for the same billing period.",
        category=TicketCategory.BILLING,
        status=TicketStatus.ESCALATED,
        priority=TicketPriority.CRITICAL,
        resolution=None,
        escalation_reason="Billing dispute requires manual refund processing by billing team",
        escalated_to="billing_team",
        created_at=ago(5),
    ),

    # Priya Sharma — Notification issues
    Ticket(
        id="TKT-PS001",
        customer_id="cust-003",
        title="Email notifications going to spam",
        description="All Nexora email notifications routed to spam folder.",
        category=TicketCategory.NOTIFICATIONS,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.LOW,
        resolution="Added nexora.cloud domain to email allowlist.",
        successful_step="Add notifications@nexora.cloud to email allowlist/whitelist",
        created_at=ago(20),
        resolved_at=ago(19),
    ),
    Ticket(
        id="TKT-PS002",
        customer_id="cust-003",
        title="In-app notification bell showing incorrect count",
        description="Notification count badge shows 99+ but inbox is empty.",
        category=TicketCategory.NOTIFICATIONS,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.LOW,
        resolution="Cleared notification cache; count reset correctly.",
        successful_step="Clear notification cache via Profile menu > Settings > Clear Cache",
        created_at=ago(8),
        resolved_at=ago(7),
    ),

    # Elena Rodriguez — File sync
    Ticket(
        id="TKT-ER001",
        customer_id="cust-005",
        title="Files not syncing to desktop client",
        description="Desktop sync client shows 'Sync Paused' for 3 days.",
        category=TicketCategory.FILE_SYNC,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.MEDIUM,
        resolution="Storage quota was exceeded; archived old projects to free space.",
        successful_step="Archive old projects to free storage quota",
        created_at=ago(15),
        resolved_at=ago(14),
    ),
]
for t in tickets_data:
    db.add(t)
db.commit()
print(f"Inserted {len(tickets_data)} tickets.")


# ─── Demo Scenarios ────────────────────────────────────────────────────────────

scenarios = [
    DemoScenario(
        id="demo-001",
        name="Scenario 1: Recurring Billing Memory",
        description=(
            "Sarah Mitchell returns with a new billing issue. "
            "The agent recalls her previous payment failure and that cache-clearing FAILED "
            "but billing profile update WORKED. Demonstrates memory-driven personalization."
        ),
        customer_id="cust-001",
        scenario_type="recurring_billing",
        sort_order=1,
        turns=json.dumps([
            {
                "role": "user",
                "content": "Hi, I'm having trouble with my subscription renewal payment. It keeps getting declined.",
                "delay_ms": 500,
            },
            {
                "role": "user",
                "content": "I tried it three times and it fails every time. Is there something wrong with my account?",
                "delay_ms": 3000,
            },
            {
                "role": "user",
                "content": "Okay I updated the billing profile like you suggested. It worked! Payment went through.",
                "delay_ms": 5000,
            },
        ]),
        memory_checkpoints=json.dumps({
            "turn_1": "Should recall previous billing issue and avoid recommending cache clearing",
            "turn_3": "Should retain that billing profile update resolved recurring billing issue again",
        }),
    ),
    DemoScenario(
        id="demo-002",
        name="Scenario 2: Integration Failure Pattern",
        description=(
            "Marcus Chen reports SSO issues with new employees. "
            "Agent recalls previous SAML certificate fix and applies same solution proactively."
        ),
        customer_id="cust-002",
        scenario_type="integration_failure",
        sort_order=2,
        turns=json.dumps([
            {
                "role": "user",
                "content": "Hey, we have SSO issues again. New employees hired this week can't log in.",
                "delay_ms": 500,
            },
            {
                "role": "user",
                "content": "Existing employees are fine, only the new ones. It worked fine last week.",
                "delay_ms": 3000,
            },
            {
                "role": "user",
                "content": "We checked the certificate — it's valid. But the attribute mapping might be the issue.",
                "delay_ms": 4000,
            },
            {
                "role": "user",
                "content": "Yes! Updating the attribute mapping for the email field fixed it. All new users can log in now.",
                "delay_ms": 3000,
            },
        ]),
        memory_checkpoints=json.dumps({
            "turn_1": "Should recall previous SAML certificate issue and resolution",
            "turn_4": "Should retain new pattern: attribute mapping issue affects new users",
        }),
    ),
    DemoScenario(
        id="demo-003",
        name="Scenario 3: Escalation with Memory Handoff",
        description=(
            "James Okonkwo reports another billing dispute. "
            "Agent recalls previous double-charge escalation and immediately escalates "
            "with full context, generating a handoff summary that includes history."
        ),
        customer_id="cust-004",
        scenario_type="escalation",
        sort_order=3,
        turns=json.dumps([
            {
                "role": "user",
                "content": "I've been charged twice again this month. This is the second time this has happened.",
                "delay_ms": 500,
            },
            {
                "role": "user",
                "content": "I need this resolved urgently. My finance team is asking questions.",
                "delay_ms": 3000,
            },
        ]),
        memory_checkpoints=json.dumps({
            "turn_1": "Should immediately recognize pattern of billing disputes for this customer",
            "turn_2": "Should escalate with complete context including previous escalation",
        }),
    ),
]
for s in scenarios:
    db.add(s)
db.commit()
print(f"Inserted {len(scenarios)} demo scenarios.")


# ─── Pre-seed Hindsight memory banks for demo customers ───────────────────────

def seed_hindsight():
    """Pre-load historical memories into Hindsight for demo customers."""
    try:
        from app.config import get_settings
        from app import hindsight as mem
        import asyncio

        settings = get_settings()

        print("Initializing Hindsight for seeding...")
        success = asyncio.run(mem.init_hindsight(
            llm_provider=settings.HINDSIGHT_LLM_PROVIDER,
            llm_model=settings.HINDSIGHT_LLM_MODEL,
            llm_api_key=settings.get_hindsight_llm_key(),
            embedded=settings.HINDSIGHT_EMBEDDED,
            base_url=settings.HINDSIGHT_BASE_URL,
            hindsight_api_key=settings.HINDSIGHT_API_KEY,
        ))

        if not success:
            print("Hindsight not available — skipping memory seeding (will work without it).")
            return

        # Sarah Mitchell — cust-001
        mem.create_bank("cust-001", "Sarah Mitchell", "business")
        sarah_memories = [
            (
                "Sarah Mitchell reported payment failure when upgrading from Starter to Business plan on Nexora Workspace. "
                "Troubleshooting step attempted: clearing browser cache — this DID NOT WORK and did not resolve the payment issue. "
                "SUCCESSFUL RESOLUTION: Updating billing profile with correct billing address fixed the payment issue. "
                "Sarah confirmed the fix worked.",
                "support_ticket:TKT-SM001",
                ago(24),
            ),
            (
                "Sarah Mitchell's Slack integration stopped sending notifications after workspace rename. "
                "Resolution: Re-authorized Slack OAuth integration from Settings > Integrations > Slack. "
                "Notifications resumed immediately after re-authorization. Customer confirmed resolved.",
                "support_ticket:TKT-SM002",
                ago(11),
            ),
            (
                "Customer profile: Sarah Mitchell uses Chrome 124 on Windows 11. "
                "She is the primary workspace admin for Vertex Labs (28 members, Business plan). "
                "She prefers email communication. Workspace running Nexora v4.2.1.",
                "customer_profile",
                ago(30),
            ),
        ]
        for content, ctx, ts in sarah_memories:
            mem.retain("cust-001", content, context=ctx, timestamp=ts,
                       metadata={"customer_name": "Sarah Mitchell", "plan": "business"})
        print("Seeded Sarah Mitchell memories.")

        # Marcus Chen — cust-002
        mem.create_bank("cust-002", "Marcus Chen", "enterprise")
        marcus_memories = [
            (
                "Marcus Chen reported SAML certificate expiry causing company-wide SSO lockout on Nexora Workspace. "
                "SUCCESSFUL RESOLUTION: Renewed SAML certificate on Okta IDP and re-uploaded to Nexora Settings > Security > SSO. "
                "Confirmed working for all 150 users after fix.",
                "support_ticket:TKT-MC001",
                ago(59),
            ),
            (
                "Marcus Chen's API integration was hitting rate limits (HTTP 429) causing CI/CD pipeline failures. "
                "Resolution: Implemented exponential backoff in client code and upgraded to Enterprise API tier. "
                "Rate limit raised from 1000/min to 10000/min.",
                "support_ticket:TKT-MC002",
                ago(29),
            ),
            (
                "Customer profile: Marcus Chen is DevOps lead at TechFlow Solutions (150 members, Enterprise plan). "
                "Uses Firefox 125 on macOS Sonoma. Heavy API user. Prefers Slack communication in mornings. "
                "Manages SSO (Okta SAML) and CI/CD integrations.",
                "customer_profile",
                ago(65),
            ),
        ]
        for content, ctx, ts in marcus_memories:
            mem.retain("cust-002", content, context=ctx, timestamp=ts,
                       metadata={"customer_name": "Marcus Chen", "plan": "enterprise"})
        print("Seeded Marcus Chen memories.")

        # James Okonkwo — cust-004
        mem.create_bank("cust-004", "James Okonkwo", "business")
        james_memories = [
            (
                "James Okonkwo reported invoices not generating for 2 months. "
                "SUCCESSFUL RESOLUTION: Billing webhook was disabled; re-enabled invoice generation in admin panel.",
                "support_ticket:TKT-JO001",
                ago(44),
            ),
            (
                "James Okonkwo reported being double-charged for January subscription — two charges for same billing period. "
                "This issue was ESCALATED to billing team for manual refund processing. "
                "Billing dispute — cannot be resolved by support agent, requires billing team intervention.",
                "support_ticket:TKT-JO002",
                ago(5),
            ),
            (
                "Customer profile: James Okonkwo is finance team admin at FinBridge Capital (45 members, Business plan). "
                "Uses Edge 124 on Windows 10. Has experienced multiple billing issues. "
                "Prefers phone communication. Direct billing contact.",
                "customer_profile",
                ago(50),
            ),
        ]
        for content, ctx, ts in james_memories:
            mem.retain("cust-004", content, context=ctx, timestamp=ts,
                       metadata={"customer_name": "James Okonkwo", "plan": "business"})
        print("Seeded James Okonkwo memories.")

        # Priya Sharma — cust-003
        mem.create_bank("cust-003", "Priya Sharma", "starter")
        mem.retain(
            "cust-003",
            "Priya Sharma had email notifications going to spam. Fixed by adding nexora.cloud to email allowlist. "
            "Also had notification count badge showing incorrect count — fixed by clearing notification cache.",
            context="support_history",
            timestamp=ago(10),
            metadata={"customer_name": "Priya Sharma", "plan": "starter"},
        )
        print("Seeded Priya Sharma memories.")

        # Elena Rodriguez — cust-005
        mem.create_bank("cust-005", "Elena Rodriguez", "starter")
        mem.retain(
            "cust-005",
            "Elena Rodriguez experienced file sync issues — desktop sync client showed 'Sync Paused'. "
            "Root cause: storage quota exceeded. Resolution: archived old projects to free storage space. "
            "She is on Starter plan with 50GB storage limit.",
            context="support_history",
            timestamp=ago(14),
            metadata={"customer_name": "Elena Rodriguez", "plan": "starter"},
        )
        print("Seeded Elena Rodriguez memories.")

        mem.shutdown_hindsight()
        print("Hindsight seeding complete.")

    except Exception as e:
        print(f"Hindsight seeding error (non-fatal): {e}")


db.close()
print("\nDatabase seeding complete.")
print("Run seed_hindsight() to pre-load Hindsight memory banks (requires LLM API key).")

if __name__ == "__main__":
    seed_hindsight()
