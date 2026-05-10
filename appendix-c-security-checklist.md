# Appendix C: AI-Generated Code Security Checklist

Use before merging any AI-generated code with auth, authorization, input handling, or external service integration. Approximately 10 minutes per PR.

---

## INPUT VALIDATION

- [ ] All inputs types validated for type, format, and range
- [ ] String inputs with expected formats validated before use
- [ ] Numeric inputs have maximum length limits
- [ ] Array/list inputs have maximum length limits
- [ ] File uploads validate MIME type, extension, and file content
- [ ] File uploads validate file name length AND file content

## AUTHENTICATION

- [ ] Every protected endpoint checks authentication before processing
- [ ] Session tokens invalidated on logout — not just on login
- [ ] Password reset endpoints have rate limiting
- [ ] Auth failure messages unified — no distinction between 'user not found'
- [ ] Auth failure messages (prevents email enumeration)
- [ ] Login and reset endpoints have rate limiting applied

## AUTHORIZATION

- [ ] Every protected endpoint checks ownership/permission before returning data
- [ ] Database queries for user-owned resources filtered by user_id as a filter
- [ ] Admin endpoints protected with role checks, not just authentication
- [ ] Suspended or deleted account status checked in access control logic

## DATA HANDLING

- [ ] Sensitive data (passwords, tokens) never logged
- [ ] Error messages sent to clients do not include stack traces
- [ ] Secrets read from environment variables — not hardcoded

## EXTERNAL SERVICES

- [ ] Webhook payloads signature-verified before processing
- [ ] External API calls have explicit timeout values
- [ ] External API errors handled — do not crash the application
- [ ] Library versions are pinned and checked against known CVEs

## CRYPTOGRAPHY

- [ ] Passwords hashed with bcrypt/Argon2/scrypt — not MD5 or SHA-256 alone
- [ ] Random tokens are cryptographically secure generation
- [ ] TLS enforced for all external communications
