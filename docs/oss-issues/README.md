# OSS Rules of Play Issues Analysis

This document tracks the 11 open issues reported by `sap-ospo-bot` regarding OSS Rules of Play violations.

**Reference:** https://sap.github.io/fosstars-rating-core/oss_rules_of_play_rating.html

---

## Summary

| Issue | Rule ID | Problem | Status | Fix Difficulty |
|-------|---------|---------|--------|----------------|
| #12 | rl-vulnerability_alerts-1 | Vulnerability alerts not enabled | Open | Easy (GitHub settings) |
| #7 | rl-license_file-2 | License not in allowed list | Open | Needs decision |
| #3 | rl-reuse_tool-2 | No LICENSES directory | Open | Easy |
| #8 | rl-reuse_tool-1 | README doesn't mention REUSE | Open | Easy |
| #9 | rl-reuse_tool-3 | Not registered in REUSE | Open | Medium |
| #10 | rl-reuse_tool-4 | Not REUSE compliant | Open | Medium |
| #1 | rl-assigned_teams-4 | No team with push privileges | Open | Admin only |
| #2 | rl-assigned_teams-5 | Team privileges issue | Open | Admin only |
| #4 | rl-assigned_teams-2 | Team privileges issue | Open | Admin only |
| #5 | rl-assigned_teams-3 | Not enough admins | Open | Admin only |
| #6 | rl-assigned_teams-1 | Team privileges issue | Open | Admin only |

---

## Detailed Analysis

### 1. Vulnerability Alerts (Issue #12)

**Problem:** GitHub vulnerability alerts are not enabled.

**Fix:** 
1. Go to repository Settings → Security & analysis
2. Enable "Dependabot alerts"
3. Enable "Dependabot security updates"

**Owner Required:** Repository admin

---

### 2. License Issues (Issue #7)

**Problem:** GPL-3.0 is not in SAP's allowed license list.

**Current License:** GPL-3.0 (GNU General Public License v3)

**SAP Allowed Licenses (typically):**
- Apache-2.0
- MIT
- BSD-2-Clause
- BSD-3-Clause

**Options:**
1. **Change to Apache-2.0** (most common for SAP projects) - Requires consent from all contributors
2. **Request exception** from SAP OSPO
3. **Keep GPL-3.0** if there's a business reason

**Owner Required:** Legal/OSPO decision

---

### 3. REUSE Compliance (Issues #3, #8, #9, #10)

**What is REUSE?**
REUSE is a specification to make licensing information machine-readable. See: https://reuse.software/

**Required Changes:**

#### 3.1 Create LICENSES directory (Issue #3)
```
LICENSES/
└── GPL-3.0-only.txt   (or Apache-2.0.txt if license changes)
```

#### 3.2 Add REUSE badge to README (Issue #8)
Add to README.md:
```markdown
[![REUSE status](https://api.reuse.software/badge/github.com/emartech/loyalty-contact-migration-verifier)](https://api.reuse.software/info/github.com/emartech/loyalty-contact-migration-verifier)
```

#### 3.3 Register with REUSE (Issue #9)
- Run REUSE lint tool: `reuse lint`
- Fix any compliance issues
- See https://reuse.software/tutorial/

#### 3.4 Add SPDX headers to all files (Issue #10)
Add to each source file:
```python
# SPDX-FileCopyrightText: 2024 SAP Emarsys
# SPDX-License-Identifier: GPL-3.0-only
```

**Tool to help:**
```bash
pip install reuse
reuse lint          # Check compliance
reuse download GPL-3.0-only  # Download license to LICENSES/
reuse addheader --license GPL-3.0-only --copyright "SAP Emarsys" src/**/*.py
```

---

### 4. Team/Admin Issues (Issues #1, #2, #4, #5, #6)

**Problems:**
- No team with push privileges
- Not enough admins on GitHub

**Fix:** These require GitHub organization admin access:
1. Create or assign a team to the repository with push access
2. Ensure at least 2 admins are assigned

**Owner Required:** GitHub organization admin (emartech)

---

## Recommended Action Plan

### Phase 1: Quick Wins (Can do now)
- [ ] Enable vulnerability alerts (Issue #12)
- [ ] Create LICENSES directory with license file (Issue #3)

### Phase 2: REUSE Compliance
- [ ] Add SPDX headers to all Python files (Issue #10)
- [ ] Add REUSE badge to README (Issue #8)
- [ ] Run `reuse lint` and fix issues (Issue #9)

### Phase 3: Requires Decision/Admin
- [ ] Decide on license (GPL-3.0 vs Apache-2.0) (Issue #7)
- [ ] Request admin to fix team assignments (Issues #1, #2, #4, #5, #6)

---

## References

- [SAP OSS Rules of Play](https://sap.github.io/fosstars-rating-core/oss_rules_of_play_rating.html)
- [REUSE Specification](https://reuse.software/)
- [REUSE Tutorial](https://reuse.software/tutorial/)
- [SPDX License List](https://spdx.org/licenses/)
