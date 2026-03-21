# Documentation

Universal reference docs for the full software development lifecycle. All documents are project-agnostic, using `{PLACEHOLDER}` syntax where customization is needed.

## Directory Structure

```
docs/
├── methodology/
│   ├── ai-assisted-development.md    — AI coding workflow, vibe coding evolution, security risks
│   └── solo-dev-workflow.md          — PM, prioritization, shipping cadence for one-person teams
├── mobile/
│   └── flutter-architecture-patterns.md — Patterns from 10+ production Flutter apps
├── frontend/
│   ├── ux-design-guidelines.md       — Mobile + web UX patterns, accessibility, theming
│   └── web-ux-patterns.md            — React/Next/Vue, Core Web Vitals, responsive design
├── backend/
│   ├── api-architecture-patterns.md  — REST/GraphQL design, middleware, error handling
│   ├── database-design-guide.md      — Schema, migrations, indexing, ORM patterns
│   └── auth-implementation-guide.md  — OIDC, JWT, RBAC, social login, MFA
├── compliance/
│   ├── README.md                     — Compliance templates overview
│   ├── dpia-template.md              — Data Protection Impact Assessment
│   ├── breach-notification-template.md — Incident response plan
│   ├── processor-registry-template.md — Third-party processor documentation
│   ├── store-privacy-labels-template.md — Apple/Google privacy declarations
│   ├── privacy-policy-template.md    — User-facing privacy policy
│   └── legal-checklist.md            — TOS, cookie policy, age verification, GDPR/CCPA
├── launch/
│   └── store-submission-guide.md     — Test, review, and launch on App Store / Play Store
├── infrastructure/
│   ├── deployment-patterns.md        — Docker, VPS, serverless, SSL, zero-downtime
│   └── cost-optimization.md          — Free tiers, VPS vs cloud, budget planning
├── devops/
│   └── cicd-setup-guide.md           — GitHub Actions, Fastlane, signing automation
└── business/
    ├── monetization-patterns.md      — IAP, subscriptions, pricing, payment processing
    ├── marketing-strategy-guide.md   — ASO, launch strategy, growth tactics, demand mgmt
    └── analytics-privacy-first.md    — Event taxonomy, privacy-compliant analytics tools
```

## Principles

All docs follow these principles:

1. **Tool-agnostic** — mention tools as examples, not prescriptions
2. **Solo-dev optimized** — minimize complexity, maximize automation
3. **Privacy-by-design** — data minimization at every layer
4. **English only** — universal accessibility
5. **Actionable** — every section includes concrete guidance or templates
