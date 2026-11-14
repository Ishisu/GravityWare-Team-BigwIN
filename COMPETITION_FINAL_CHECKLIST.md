# Team BigwIN — NASA Space Apps 2026 final project checklist

## Official challenge fit
Selected challenge: **Create Health Monitoring Software for Astronauts on Space Missions**. The challenge asks for software that gathers health indicators and helps astronauts evaluate and act on their health status during long-duration missions. GravityWare addresses this through individual health logs, personal trend review, plain-language gravity context and experimental pattern screening.

## Judging criteria to demonstrate
The 2026 event pages describe five evaluation criteria: **Impact, Creativity, Validity, Relevance and Presentation**. Make each visible in the submission and demo:
- **Impact:** explain how understandable self-monitoring may help astronauts notice and communicate changes. Do not claim improved clinical outcomes without evidence.
- **Creativity:** show the connection between an astronaut's mission gravity profile, personal trends and plain-language education.
- **Validity:** explain data provenance, units, assumptions, limitations and why statistical flags are not diagnoses.
- **Relevance:** explicitly map features to the selected astronaut-health-monitoring challenge and its hazards (radiation, isolation/confinement, altered gravity and hostile/closed environment).
- **Presentation:** provide a working, reproducible demo, a short walkthrough, readable screenshots and a clear explanation of what is implemented versus planned.

## Data and science integrity
- Current demo readings are synthetic or manually entered; they are **not NASA astronaut medical records, live telemetry or a NASA dataset**.
- NASA Human Research Program material is used as cited scientific/educational context. Do not describe links or summaries as a live NASA data integration.
- Cite every NASA page, dataset, third-party library, image, font and other external resource used in the project/submission. Keep a source list with title, organization, URL, access date and what was used.
- Do not invent clinical thresholds. Gravity-aware labels are educational trend context, not a determination of medical normality. Do not say lunar or Martian long-duration human effects are established where direct human evidence is lacking.
- The AI screen is experimental and not clinically validated. It does not diagnose, predict disease, clear an astronaut for duty or replace flight medical protocols.
- Use only synthetic or explicitly authorized demonstration records. Remove real personal/medical identifiers from screenshots and videos.

## Security and privacy
- Never publish `.streamlit/secrets.toml`, passwords, Supabase keys, private emails or real health records.
- Use only Supabase publishable/anon key with Row Level Security; never expose service-role/secret keys.
- Test that each account can access only its own records.
- Do not claim NASA personnel can access this prototype. Doctor and mission-control collaboration is a proposed workflow unless actually implemented and authorized.

## Submission readiness
- Confirm the team is registered, selected the official challenge and all team members are listed on the project page. The 2026 site says teams may have up to six participants.
- Submit through the Team Project tab before **November 15, 2026, 11:59 p.m. local time** (verify the time shown for your registered event).
- Provide a public, accessible demo link or presentation as required by the submission form. Test links in a signed-out/private browser.
- Include: problem, target users, solution, key features, technical approach, data sources, testing, limitations, future work and team contributions.
- Confirm all original project materials have an appropriate open-source license and all third-party material is properly licensed/attributed. The participant terms say original content must be freely available or OSI-licensed; absent a specified OSI license, Apache 2.0 may apply.

## Suggested 2-minute demo sequence
1. Introduce the challenge and the astronaut self-monitoring problem.
2. Sign in to one fictional astronaut and show the saved mission profile.
3. Show a sample health record and personal trend.
4. Open Gravity-Aware Assessment and explain that it compares personal history while avoiding unsupported claims of clinical normality.
5. Open Gravity Health Education and show NASA research references.
6. Show CSV/PDF export and explain account-level data isolation.
7. Close with limitations and the next step: clinician-reviewed thresholds, validation and authorized collaboration.

## Official references checked
- Challenge: https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/
- 2026 event and submission timeline: https://www.spaceappschallenge.org/2026/
- 2026 Participant Terms and Conditions: https://www.spaceappschallenge.org/legal/
- NASA HRP hazards: https://www.nasa.gov/hrp/hazards/
- NASA HRP risks: https://www.nasa.gov/hrp/risks/

This checklist is a project aid, not a guarantee of eligibility or selection. Always follow the live official submission form and terms.
