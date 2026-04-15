# Password Reset and Account Unlock SOP

## When to Use This SOP
Use this process when a user forgets password, is locked out after failed attempts, or cannot pass MFA due to device change.

## Identity Verification
Before any account action, verify user identity using two factors:
1. Employee ID or corporate email.
2. Manager name or last successful login location.

## Password Reset Steps
1. Open IAM admin portal and locate user account.
2. Confirm account is active and not under security hold.
3. Trigger temporary password reset.
4. Force password change at next login.
5. Ask user to sign in and set a compliant password.

## Account Unlock Steps
If account is locked, clear lockout status in IAM portal.
Check recent failed login source before unlock.
If login attempts come from unknown location, escalate to Security.

## MFA Recovery
If user changed phone, remove old MFA device mapping.
Guide user through re-enrollment with authenticator app.
For urgent access, issue one-time bypass code with approval.

## SLA Targets
Password reset: within 15 minutes during service hours.
Account unlock: within 10 minutes after identity verification.
MFA recovery: within 30 minutes.
