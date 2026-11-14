# GravityWare v1.7.4 — Medical and Mission Control collaboration

## Included
- Astronaut dashboard: submit a request for medical review.
- Medical Review Center: authorized doctors review cases and record assessment and follow-up.
- Mission Control Center: authorized mission reviewers read medical assessments and record operational decisions.
- Reviewer access is granted through a Supabase table; users cannot grant themselves roles.

## Required database setup
1. Back up your Supabase project before changing policies.
2. Open Supabase Dashboard → SQL Editor.
3. Run `database/collaboration_setup_v1_7_4.sql` once.
4. In Supabase Authentication → Users, identify the reviewer accounts and copy their user UUIDs.
5. In SQL Editor, grant roles to the appropriate reviewer UUIDs, for example:

```sql
insert into public.reviewer_access (user_id, role, active)
values
  ('PASTE-DOCTOR-USER-UUID-HERE', 'doctor', true),
  ('PASTE-MISSION-CONTROL-USER-UUID-HERE', 'mission_control', true);
```

Use actual reviewer accounts. Do not grant reviewer roles to astronaut accounts unless that is intentionally required for a controlled demo. Never share service-role keys.

## Demo workflow
1. Sign in as an astronaut and submit a request for medical review from the Dashboard.
2. Sign out and sign in with the account assigned the `doctor` role.
3. Open Medical Review Center and save the assessment and follow-up.
4. Sign out and sign in with the account assigned the `mission_control` role.
5. Open Mission Control Center and record the operational decision and action.

## Important limitations
- This is a prototype collaboration workflow, not a live NASA integration.
- The application does not send email or push notifications; reviewers see cases when they sign in.
- The UI stores the latest medical and operational notes on each case; it is not a complete immutable clinical audit system.
- Do not use real patient/astronaut health data in this competition prototype.
- AI outputs are not diagnoses, treatment recommendations, or fitness-for-duty decisions.
- Clinical decisions belong to qualified medical professionals; operational decisions belong to authorized mission personnel.
- The SQL migration adds reviewer access and review-case tables and adds reviewer read policies to health records. Review and back up your existing Supabase policies before running it.
