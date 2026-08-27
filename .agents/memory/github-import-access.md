---
name: GitHub import access
description: Environment-specific guidance for importing a repository through the authenticated GitHub connector.
---

When importing a repository through the authenticated GitHub connector, use the connector proxy rather than relying on a direct git pull. The proxy may return 403 for CI metadata under `.github/` even when application files are readable; that metadata is not required to run the app and can be skipped during import.

**Why:** Direct network cloning timed out in this environment, while the authenticated connector successfully provided the repository tree and runtime files.

**How to apply:** Reattach the authorized GitHub connection if needed, fetch the tree, copy application/runtime files, and omit blocked CI metadata and local secret configuration files.