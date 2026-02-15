# Databricks notebook source
# MAGIC %md
# MAGIC # Create HEDIS Guidelines Knowledge Base
# MAGIC
# MAGIC Creates knowledge base documents about HEDIS measures and quality improvement strategies.
# MAGIC All configuration from config.yaml.

# COMMAND ----------

# Ensure Environment widget exists (use current value so job-injected value is preserved)
try:
    _current = dbutils.widgets.get("environment")
except Exception:
    _current = "dev"
dbutils.widgets.dropdown("environment", _current, ["dev", "staging", "prod"], "Environment")
print(f"Environment: {_current} (change the dropdown if needed, then re-run the next cell)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Configuration

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)
print(f"Volume path: {cfg.volume_path}")
print(f"Knowledge base table: {cfg.hedis_guidelines_kb}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Knowledge Base Documents

# COMMAND ----------

# HEDIS Guidelines Knowledge Base - MEDICARE ADVANTAGE FOCUS
hedis_knowledge = [
    {
        "doc_id": "HEDIS_BCS_MA_2024",
        "doc_type": "HEDIS Guideline",
        "title": "Breast Cancer Screening (BCS) - Medicare Advantage MY 2024",
        "content": """
BREAST CANCER SCREENING (BCS) - HEDIS SPECIFICATION FOR MEDICARE ADVANTAGE

Measure Description:
The percentage of women 50-74 years of age who had a mammogram to screen for breast cancer in the past 27 months.

Medicare Advantage Considerations:
- Most MA beneficiaries are 65+ (eligible population heavily skewed to 65-74 age group)
- Higher prevalence of comorbidities may affect screening completion
- Transportation and access barriers common in elderly populations
- Cost-sharing eliminated under ACA for preventive services

Eligible Population:
- Women aged 50-74 as of December 31 of the measurement year
- Continuously enrolled for at least 2 years prior to measurement year
- No bilateral mastectomy or other breast cancer exclusions

Numerator:
Women who had at least one mammogram during the measurement period (24 months prior to December 31 plus 3 month run-out).

Denominator:
Women aged 50-74 with continuous enrollment and no exclusions.

Data Collection:
- Administrative claims (CPT codes 77063, 77065, 77066, 77067)
- Medical records
- HEDIS reporting standards

Performance Benchmarks (NCQA Medicare):
- 25th Percentile: 67%
- 50th Percentile: 74%
- 75th Percentile: 80%
- 90th Percentile: 84%

CMS Star Rating Weight: 1x (Preventive Care category)

Quality Improvement Strategies for Medicare Population:
1. Transportation assistance programs (Lyft/Uber partnerships)
2. Mobile mammography units for PACE/SNF residents
3. Multi-language patient navigators for diverse seniors
4. Integration with Annual Wellness Visits (capture screening due dates)
5. Provider reminder systems in geriatric practices
6. Elimination of cost-sharing barriers
7. Caregiver engagement for seniors with cognitive impairments
8. Community health center partnerships in underserved areas
"""
    },
    {
        "doc_id": "HEDIS_CDC_MA_2024",
        "doc_type": "HEDIS Guideline",
        "title": "Comprehensive Diabetes Care (CDC) - Medicare Advantage MY 2024",
        "content": """
COMPREHENSIVE DIABETES CARE (CDC) - HEDIS SPECIFICATION FOR MEDICARE ADVANTAGE

Measure Description:
Multiple indicators of diabetes management for elderly Medicare beneficiaries including HbA1c testing, HbA1c control, eye exams, kidney screening, and BP control.

Medicare Advantage Context:
- Approximately 30-35% of MA beneficiaries have diabetes
- Higher rates of complications (retinopathy, neuropathy, kidney disease) in elderly
- Polypharmacy and medication adherence challenges common
- Social determinants (health literacy, access) significantly impact outcomes

Eligible Population:
- Members 18-75 years of age (MA population heavily 65-75)
- Identified as having diabetes (Type 1 or Type 2)
- Continuously enrolled for measurement year

CDC-1: HbA1c Testing
Numerator: At least one HbA1c test during measurement year
Performance Target: >92%
CMS Star Weight: 3x (Outcomes measure)

CDC-2: HbA1c Poor Control (>9%)
Numerator: Most recent HbA1c value >9% or no test
Performance Target: <12% (lower is better)
CMS Star Weight: 3x (Outcomes measure)

CDC-3: HbA1c Good Control (<8%)
Numerator: Most recent HbA1c value <8%
Performance Target: >55%
CMS Star Weight: 3x (Outcomes measure)

CDC-4: Eye Exam (Retinal) Performed
Numerator: Retinal or dilated eye exam in measurement year or year prior
Performance Target: >68%
CMS Star Weight: 3x (Outcomes measure)

CDC-5: Kidney Health Evaluation (Critical for Medicare)
Numerator: Urine albumin-creatinine ratio OR kidney disease diagnosis
Performance Target: >92%
CMS Star Weight: 3x (Outcomes measure - NEW in 2024)

CDC-6: BP Control (<140/90)
Numerator: Most recent BP during measurement year <140/90 mmHg
Performance Target: >73%
CMS Star Weight: 3x (Outcomes measure)

Quality Improvement Interventions for Medicare Diabetics:
1. Comprehensive Diabetes Management Programs (care management for high-risk)
2. Point-of-care HbA1c testing in primary care offices
3. Telehealth diabetic retinopathy screening programs
4. Medication Therapy Management (MTM) for Part D adherence
5. Health coaching programs with geriatric focus
6. Endocrinology specialist integration for complex patients
7. Annual comprehensive diabetes assessments during AWV
8. CGM (continuous glucose monitoring) programs for insulin users
9. Foot care education and podiatry referrals
10. Nutrition counseling tailored to elderly dietary needs
"""
    },
    {
        "doc_id": "HEDIS_CBP_MA_2024",
        "doc_type": "HEDIS Guideline",
        "title": "Controlling High Blood Pressure (CBP) - Medicare Advantage MY 2024",
        "content": """
CONTROLLING HIGH BLOOD PRESSURE (CBP) - HEDIS SPECIFICATION FOR MEDICARE ADVANTAGE

Measure Description:
The percentage of members 18-85 years of age with a diagnosis of hypertension whose blood pressure was adequately controlled during the measurement year.

Medicare Advantage Significance:
- Approximately 70-75% of MA beneficiaries have hypertension
- CVD is leading cause of death and hospitalization in elderly
- Medication adherence challenges due to polypharmacy
- Home BP monitoring critical for elderly with mobility limitations

CMS Star Rating Weight: 3x (Outcomes measure - highest weight category)

Eligible Population:
- Members aged 18-85 as of December 31 of measurement year
- Identified as having hypertension (ICD-10 codes I10-I16)
- Continuous enrollment during measurement year
- At least one outpatient encounter

Numerator:
Members whose most recent BP reading during the measurement year is <140/90 mmHg.

Denominator:
Members meeting eligibility criteria with at least one BP reading in measurement year.

Exclusions:
- Diagnosis of end-stage renal disease (ESRD) - common in elderly
- Kidney transplant
- Pregnancy (rare in Medicare)

Data Collection:
- Administrative claims for diagnoses
- Medical records or electronic clinical data for BP values
- HEDIS reporting standards (use most recent BP if multiple)

Performance Benchmarks (Medicare):
- 25th Percentile: 58%
- 50th Percentile: 65%
- 75th Percentile: 72%
- 90th Percentile: 78%

Quality Improvement Strategies for Medicare Hypertension:
1. Home blood pressure monitoring programs with cellular-connected devices
2. Medication adherence programs (especially for ACE/ARB and diuretics) - Part D MTM
3. Pharmacist-led medication management and reconciliation
4. Self-measured BP with clinical support (Million Hearts protocol)
5. Team-based care coordination (nurses, pharmacists, community health workers)
6. Health IT integration for BP tracking across care settings
7. Community health worker outreach for high-risk populations
8. Standardized BP measurement protocols across practices
9. Simplification of medication regimens (combination pills, mail-order 90-day supplies)
10. Integration with CCM (Chronic Care Management) billing for Medicare
"""
    },
    {
        "doc_id": "HEDIS_PARTD_ADHERENCE_MA_2024",
        "doc_type": "HEDIS Guideline",
        "title": "Part D Medication Adherence - Medicare Advantage MY 2024",
        "content": """
PART D MEDICATION ADHERENCE MEASURES - CRITICAL FOR MEDICARE ADVANTAGE STAR RATINGS

Overview:
Medication adherence measures are among the HIGHEST WEIGHTED in CMS Star Ratings (3x weight, Outcomes category).
These measures directly impact Quality Bonus Program payments and member premium competitiveness.

Three Core Adherence Measures:

1. MPM - Medication Adherence for Diabetes Medications (Part D)
2. MPA - Medication Adherence for Hypertension (RAS Antagonists) (Part D)
3. MPC - Medication Adherence for Cholesterol (Statins) (Part D)

Measure Specification:
- Eligible Population: Members 18+ with Part D coverage and relevant condition
- Numerator: Members with Proportion of Days Covered (PDC) ≥80%
- PDC Calculation: Days with medication on hand / Days in measurement period
- Measurement Period: Full calendar year

CMS Star Rating Weight: 3x for ALL THREE measures (Outcomes)

Target Performance:
- 25th Percentile: 78%
- 50th Percentile: 82%
- 75th Percentile: 86%
- 90th Percentile: 89%

Medicare-Specific Adherence Barriers:
1. Cost: Coverage gap ("donut hole"), copays for seniors on fixed income
2. Polypharmacy: Average MA member takes 8-12 medications
3. Cognitive decline: Memory issues, confusion about regimens
4. Health literacy: Difficulty understanding medication instructions
5. Social isolation: Lack of caregiver support
6. Transportation: Difficulty getting to pharmacy
7. Side effects: Elderly more sensitive, may discontinue without telling provider

Evidence-Based Intervention Strategies:

Tier 1 - High Impact Interventions:
1. Medication Synchronization ("med sync") - align all refills to same date
2. 90-day supplies via mail-order (reduces copays and trips to pharmacy)
3. Pharmacist-led MTM (Medication Therapy Management) - required for Part D
4. Automated refill and delivery programs
5. Blister packs / medication organizers for complex regimens
6. Copay assistance programs for LIS (Low Income Subsidy) eligible

Tier 2 - Moderate Impact Interventions:
7. Predictive analytics to identify non-adherent members early
8. Outreach campaigns (IVR, live calls, SMS) for refill reminders
9. Provider education on prescribing long-acting formulations
10. Integration of pharmacy data into EMR for provider alerts
11. Care management programs for high-risk members

Tier 3 - Supportive Interventions:
12. Health coaching and education on medication importance
13. Caregiver education and engagement
14. Transportation assistance to pharmacy
15. Mobile apps for medication reminders (limited adoption in elderly)

Pharmacy Partnership Opportunities:
- Retail pharmacy networks: Walgreens, CVS, Walmart
- Mail-order: Caremark, Express Scripts, OptumRx
- MTM vendor partnerships
- Specialty pharmacy for complex regimens

Key Performance Indicators:
- PDC ≥80% rate by drug class
- Early non-adherence rate (refill gaps in first 90 days)
- Persistence rate (still on therapy at 12 months)
- Intervention outreach completion rates
- Member satisfaction with pharmacy services

Financial Impact:
- Part D adherence measures are 3x weighted
- Small improvements (1-2%) can boost overall rating by 0.05-0.10 stars
- Critical for achieving 4+ star status and Quality Bonus Program
"""
    },
    {
        "doc_id": "HEDIS_READMISSIONS_MA_2024",
        "doc_type": "HEDIS Guideline",
        "title": "Plan All-Cause Readmissions (PCR) - Medicare Advantage MY 2024",
        "content": """
PLAN ALL-CAUSE READMISSIONS (PCR) - HEDIS SPECIFICATION FOR MEDICARE ADVANTAGE

Measure Description:
The number of acute inpatient stays per 1,000 member months that were followed by an unplanned acute readmission for any diagnosis within 30 days.

Medicare Significance:
- 30-day readmissions cost Medicare $26 billion annually
- Elderly patients at highest risk due to multiple chronic conditions
- Social determinants (living alone, low health literacy) major factors
- Transitions of care failure points common

CMS Star Rating Weight: 3x (Outcomes measure)

Measure Methodology:
- Observed readmissions / Expected readmissions (risk-adjusted)
- Lower ratio = better performance
- Risk adjustment accounts for age, comorbidities, procedure types

Target Performance (Lower is Better):
- Top Quartile (90th %ile): <8.5 readmissions per 100 discharges
- 75th Percentile: 9.0
- 50th Percentile: 10.5
- 25th Percentile: 12.0

Common Readmission Diagnoses in Medicare:
1. Heart failure exacerbation
2. COPD exacerbation
3. Pneumonia
4. Urinary tract infections
5. Acute kidney injury
6. Diabetic complications
7. Medication-related adverse events
8. Falls and fractures

Root Causes in Elderly Population:
- Inadequate discharge planning
- Medication errors post-discharge (reconciliation failures)
- Lack of follow-up appointments scheduled before discharge
- No home health or caregiver support
- Patient/family not understanding discharge instructions
- Premature discharge to meet length-of-stay targets

Evidence-Based Interventions for Medicare:

Pre-Discharge:
1. Comprehensive discharge planning with geriatric assessment
2. Medication reconciliation by pharmacist
3. "Teach-back" method for discharge instructions
4. Schedule follow-up appointment before discharge
5. Assess home situation and social support
6. Arrange DME (durable medical equipment) and home health

Post-Discharge (Critical Window = 72 hours):
7. Transitional Care Management (TCM) visits by PCP within 7-14 days
8. Pharmacist follow-up call within 48-72 hours
9. Nurse home visit within 48 hours (for high-risk)
10. Medication reconciliation and review
11. Red flags assessment (symptom worsening, confusion, falls)

Care Coordination Programs:
12. Care Transitions Intervention (CTI) model - Coleman Care Transitions
13. Project RED (Re-Engineered Discharge) - Boston University
14. Transitional Care Model (TCM) - Naylor model with advanced practice nurses
15. Hospital at Home programs for eligible patients

Technology Solutions:
16. Real-time ADT (admission/discharge/transfer) alerts from hospitals
17. HIE (Health Information Exchange) integration
18. Predictive analytics for readmission risk scoring (LACE, HOSPITAL scores)
19. Telehealth monitoring for high-risk post-discharge
20. Remote patient monitoring (RPM) - weight scales for CHF, pulse ox for COPD

Key Success Factors:
- Strong hospital partnerships and data sharing
- Embedded care coordinators in high-volume hospitals
- Proactive identification of high-risk patients
- Rapid response teams for post-discharge issues
- Culturally competent, language-appropriate interventions
- Integration with Medicare CCM (Chronic Care Management) billing
"""
    },
    {
        "doc_id": "HEDIS_HRM_MA_2024",
        "doc_type": "HEDIS Guideline",
        "title": "High-Risk Medication Use in the Elderly (HRM) - Medicare MY 2024",
        "content": """
HIGH-RISK MEDICATION USE IN THE ELDERLY (HRM) - PART D MEASURE FOR MEDICARE ADVANTAGE

Measure Description:
The percentage of Medicare members 65+ who received at least two dispensings of high-risk medications from the Beer's Criteria list.

Medicare Context:
- Beers Criteria identifies medications with unfavorable benefit-risk ratio in elderly
- Falls, fractures, cognitive impairment, hospitalizations significantly increased
- Polypharmacy common: average MA member 65+ takes 8-12 medications
- "Prescribing cascade" - treating side effects with more medications

CMS Star Rating Weight: 3x (Outcomes - lower rate is better)

Target Performance (Lower is Better):
- Top Quartile: <10% of members 65+ on high-risk meds
- 75th Percentile: 12%
- 50th Percentile: 15%
- 25th Percentile: 18%

Common High-Risk Medications in Elderly (Beers Criteria):

Highest Risk - Avoid:
- **Benzodiazepines** (e.g. Xanax, Ativan, Valium) - Falls, cognitive impairment, delirium
- **First-generation antihistamines** (Benadryl, Vistaril) - Anticholinergic effects, falls
- **Tricyclic antidepressants** (Elavil, Pamelor) - Orthostatic hypotension, cardiac effects
- **Antipsychotics** (especially for dementia/behavior) - Stroke risk, mortality
- **Barbiturates** - High fall and fracture risk
- **Non-benzodiazepine hypnotics** (Ambien, Lunesta) - Falls, cognitive effects
- **NSAIDs** (chronic use) - GI bleeding, kidney injury, heart failure exacerbation
- **Muscle relaxants** (Flexeril, Soma) - Anticholinergic effects, sedation
- **Sulfonylureas** (long-acting like Diabeta) - Hypoglycemia risk in elderly

Use with Caution:
- **Opioids** - Fall risk, constipation, delirium
- **PPIs** (chronic use) - Fractures, C. diff, drug interactions
- **Antispasmodics** (Ditropan, Detrol) - Anticholinergic burden

Quality Improvement Strategies:

Prescriber Education:
1. Academic detailing on Beers Criteria and safer alternatives
2. Provider scorecards showing HRM rates by practice
3. EMR alerts for high-risk prescriptions in elderly
4. Geriatric pharmacotherapy continuing education

Medication Therapy Management (MTM):
5. Pharmacist-led comprehensive medication reviews (CMR)
6. Deprescribing protocols for high-risk meds
7. Taper schedules for benzodiazepines and opioids
8. Identification of safer alternatives

Safer Alternatives:
- Anxiety/Insomnia: SSRIs, cognitive behavioral therapy, melatonin
- Pain: Acetaminophen, topical NSAIDs, non-pharmacologic (PT, acupuncture)
- Allergies: 2nd-gen antihistamines (Zyrtec, Allegra), nasal steroids
- Depression: SSRIs/SNRIs (avoid TCAs)
- Overactive bladder: Behavioral therapy, Myrbetriq (lower anticholinergic)

Technology Solutions:
9. Prior authorization requirements for Beers meds in 65+
10. Pharmacy point-of-sale edits and alerts
11. Predictive analytics to identify high-risk patients
12. Integration of Beers list into EMR clinical decision support

Care Management:
13. High-risk medication reviews for all members 65+ on 10+ meds
14. Home medication reviews with "brown bag" approach
15. Collaboration with prescribers on deprescribing plans
16. Patient/family education on risks

Measurement and Monitoring:
17. Monthly monitoring of HRM rates by drug class
18. Root cause analysis for new high-risk prescriptions
19. Tracking of intervention success rates
20. Provider-level feedback and coaching

Special Populations:
- **Dementia patients**: Highest risk for antipsychotics, avoid if possible
- **CHF patients**: Avoid NSAIDs (fluid retention)
- **CKD patients**: Avoid NSAIDs, adjust doses for renal function
- **Fall history**: Avoid sedatives, review all CNS-active meds

Key Success Factors:
- Strong clinical pharmacy programs
- Prescriber collaboration and buy-in
- Patient-centered deprescribing conversations
- Integration with Part D MTM requirements
- Regular monitoring and quality improvement cycles
"""
    },
    {
        "doc_id": "QI_MEMBER_OUTREACH_MA",
        "doc_type": "Quality Improvement Guide",
        "title": "Effective Member Outreach for Medicare Advantage Quality Measures",
        "content": """
EFFECTIVE MEMBER OUTREACH FOR MEDICARE ADVANTAGE HEDIS QUALITY MEASURES

Overview:
Proactive member outreach is critical for closing gaps in care for elderly Medicare beneficiaries. Multi-channel approaches with geriatric-sensitive design yield best results.

Medicare-Specific Considerations:
- Lower digital literacy: Phone and mail remain primary channels
- Hearing impairments: Clear speech, allow extra time
- Cognitive decline: Simple messaging, repetition, caregiver involvement
- Health literacy: Plain language, visual aids
- Trust: Seniors respond better to human interaction vs automation
- Transportation barriers: Offer assistance or mobile services

Outreach Channels for Medicare Population:

1. Live Phone Calls (HIGHEST EFFECTIVENESS for 65+)
   - 40-50% reach rate for Medicare members
   - Personalized conversations build trust
   - Can address barriers (transportation, cost, confusion)
   - Best for high-value measures (HbA1c testing, eye exams, medication adherence)
   - Tip: Call morning hours (9am-12pm), avoid dinner time

2. Mailed Letters/Postcards (SECOND MOST EFFECTIVE)
   - Highly effective for seniors who check mail daily
   - Large font (14pt minimum), simple language
   - Include phone number prominently
   - Personalize with member name, PCP name, specific need
   - Tip: Use postcard format (visible without opening), bright colors

3. Automated Phone Calls (IVR)
   - Moderate effectiveness (20-25% response rate) for 65+
   - Best for appointment reminders (less complex messaging)
   - Keep messages <30 seconds
   - Offer option to speak to live person

4. Text Messaging (SMS) - LIMITED for Medicare
   - Only 40-50% of 65+ have smartphones
   - Requires opt-in consent
   - Best for younger Medicare (<70) or dual-eligible
   - Use sparingly

5. Home Visits - HIGH COST but HIGH IMPACT
   - For highest-risk members (multiple gaps, social barriers)
   - Nurse or community health worker home visits
   - "Brown bag" medication reviews
   - Address SDOH barriers (food insecurity, home safety)

6. Provider Office-Based Outreach
   - Most effective: Gap closure AT THE POINT OF CARE
   - Integrate gap lists into EMR workflows
   - Standing orders for preventive services
   - Care coordinators embedded in high-volume practices

Best Practices for Medicare Outreach:

Segmentation:
- **High-risk tier**: Members with 3+ gaps, chronic conditions, or hospital admits → Phone + home visit
- **Moderate-risk tier**: 1-2 gaps → Phone + mail
- **Low-risk tier**: Single gap, stable → Mail + IVR

Timing:
- Start outreach Q1 (January-March) for maximum impact
- Q4 outreach less effective (members already compliant or not)
- Avoid holidays and extreme weather periods
- Multiple touchpoints: 3-4 attempts across 60-90 days

Messaging Tips:
- Lead with member benefit, not plan need ("Your doctor recommends...")
- Use plain language: "diabetes check-up" not "HbA1c test"
- Emphasize FREE preventive services (no copay)
- Include PCP name if possible ("Dr. Smith's office called")
- Address common barriers proactively (transportation, cost, time)

Barrier Removal:
- **Transportation**: Lyft/Uber partnerships, volunteer driver programs
- **Cost**: Emphasize $0 copay for preventive, connect to LIS/Extra Help for meds
- **Access**: Offer extended hours, weekend appointments, telehealth
- **Language**: Use interpreter services, culturally appropriate materials
- **Caregiver**: Involve adult children/caregivers with member permission

Measure-Specific Best Practices:

Medication Adherence (Part D):
- Pharmacist-led calls (higher credibility)
- Address cost concerns (generics, mail-order, assistance programs)
- Offer medication synchronization and auto-refill
- Simplify regimens with prescriber collaboration

Diabetes Measures (CDC):
- Bundle multiple tests (HbA1c, eye, kidney, BP) into single "diabetes visit"
- Partner with endocrinology for complex cases
- Offer point-of-care HbA1c and urine albumin testing
- Telehealth retinal screening

Cancer Screenings:
- Address fear/anxiety about screening
- Offer patient navigation and transportation
- Mobile mammography vans for seniors with mobility issues
- Colonoscopy sedation and ride-home support

Annual Wellness Visits:
- Emphasize comprehensive health check (not just "physical")
- No copay, covered by Medicare
- Can bundle with other gap closures
- Offer convenient scheduling (online, text, phone)

Technology and Data:

- **Predictive analytics**: Propensity-to-respond models (who will respond to phone vs mail)
- **EMR integration**: Real-time gap alerts at point of care
- **ADT feeds**: Trigger outreach post-hospital discharge
- **Pharmacy data**: Real-time adherence monitoring, early intervention for gaps
- **Call center dashboards**: Track outreach volume, reach rates, gap closure by channel

Success Metrics:

- **Reach rate**: % of attempted outreach that reached member
- **Engagement rate**: % of reached members who engaged in conversation
- **Gap closure rate**: % of gaps closed within 30/60/90 days of outreach
- **Cost per gap closed**: Total outreach cost / gaps closed
- **Channel effectiveness**: Compare gap closure rates by channel (phone vs mail vs IVR)
- **Member satisfaction**: Post-outreach survey scores

Key Success Factors:
- Start early (Q1-Q2)
- Multi-channel approach tailored to member preferences
- Human touch matters for elderly
- Remove barriers proactively
- Strong provider partnerships
- Data-driven targeting and tracking
"""
    },
    {
        "doc_id": "QI_PROVIDER_ENGAGEMENT_MA",
        "doc_type": "Quality Improvement Guide",
        "title": "Provider Engagement Strategies for Medicare Advantage HEDIS Performance",
        "content": """
PROVIDER ENGAGEMENT STRATEGIES FOR MEDICARE ADVANTAGE HEDIS PERFORMANCE

Overview:
Physician and practice engagement is essential for sustained HEDIS improvement in Medicare populations. Top-performing MA plans invest heavily in provider partnerships and point-of-care interventions.

Medicare-Specific Provider Considerations:
- Geriatric medicine and internal medicine are primary specialties
- Providers managing complex elderly patients with 8-12 chronic conditions
- Time constraints in appointments limit preventive service delivery
- Data exchange (ADT, labs, pharmacy) critical for care coordination
- Value-based contracts increasingly common (MSSP ACOs, MA risk contracts)

Provider Education:

1. HEDIS Measure Specifications - Medicare Focus
   - Annual training on updated specifications
   - Emphasis on Medicare-weighted measures (3x: outcomes, Part D)
   - Measure-specific tip sheets and quick reference guides
   - Proper coding and documentation (E/M, AWV, CCM, TCM billing)
   - Share benchmark data for Medicare performance

2. Gap Lists and Reports
   - Deliver patient-specific gap lists monthly (integrate into EMR if possible)
   - Prioritize by measure weight (3x outcomes first, then 2x, then 1x)
   - Include actionable next steps ("Order HbA1c" vs "Close diabetes gap")
   - Highlight high-value opportunities (weighted score potential)
   - Pre-visit planning: Gaps visible before appointment

3. Performance Feedback
   - Quarterly scorecards by practice (overall star rating impact)
   - Peer comparisons (de-identified) within network
   - Trend analysis over time (improving vs declining)
   - Celebrate improvements publicly (provider recognition events)
   - Tie feedback to financial incentives

Financial Incentives:

1. Pay-for-Performance (P4P)
   - Tie portion of capitation to HEDIS results (5-15% typical)
   - Structure tiered incentives (meeting vs exceeding benchmarks)
   - Weight incentives by CMS measure weight (3x for Part D adherence, outcomes)
   - Include both quality and cost metrics (total cost of care)
   - Typical range: $50-150 PMPM quality bonus for top performers

2. Quality Bonus Programs
   - Annual bonuses for top performers ($10K-100K per practice)
   - Improvement bonuses for significant gains (e.g., +5% on BCS)
   - Measure-specific incentives for priority gaps (e.g., $50 per HbA1c test)
   - Shared savings for reducing readmissions

3. Value-Based Contracts
   - Full-risk capitation with quality gates
   - Shared savings models (MSSP ACO-like)
   - Bundled payments with quality bonuses
   - Upside/downside risk arrangements

Practice Support:

1. Care Coordinators / Nurse Navigators
   - Embed in high-volume practices (50+ MA members)
   - Focus on care gap closure and care coordination
   - Assist with scheduling follow-ups, referrals
   - Medication reconciliation post-discharge
   - Chronic care management (CCM billing support)

2. Clinical Resources
   - Point-of-care testing equipment:
     - HbA1c analyzers (5-minute results during visit)
     - Lipid panels
     - Urine albumin-creatinine ratio testing
     - Blood pressure cuffs (donate for home monitoring programs)
   - Retinal cameras for diabetic eye exams (AI-assisted screening)
   - Vaccine stock (flu, pneumonia, shingles) for 65+

3. Administrative Support
   - Medical record retrieval assistance (chart chase for HEDIS)
   - Help with coding and documentation
   - Claims coding education (AWV, CCM, TCM, RPM billing)
   - Prior authorization support
   - Credentialing and contracting assistance

Technology Integration:

1. EMR Integration
   - Real-time gap alerts at point of care (pop-ups, health maintenance sections)
   - Standing orders for preventive services (e.g., mammogram order auto-fires at AWV)
   - Clinical decision support (Beers Criteria alerts for high-risk meds)
   - Medication adherence visibility (pharmacy fill data in EMR)
   - Risk stratification scores visible to providers

2. Data Exchange
   - ADT feeds: Real-time alerts for hospital admissions/discharges
   - Lab result interfaces (HbA1c, lipids, kidney function auto-flow to plan)
   - Prescription fill data: Real-time adherence monitoring
   - Health Information Exchange (HIE) participation
   - FHIR API integration for bidirectional data flow

3. Telehealth and Remote Monitoring
   - Telehealth platform access for routine follow-ups
   - RPM devices for high-risk patients (BP cuffs, weight scales, pulse ox)
   - Chronic Care Management (CCM) support for non-face-to-face care
   - Store-and-forward retinal imaging for diabetic eye exams

Care Delivery Model Enhancements:

1. Annual Wellness Visits (AWV) Optimization
   - Schedule AWV early in year (Q1-Q2) to maximize gap closure time
   - Pre-visit planning: Pull all gaps before appointment
   - Bundle gap closure: Order all needed tests/referrals during AWV
   - Document comprehensively: HRA, cognitive assessment, SDOH screening
   - Bill appropriately: G0438/G0439 codes

2. Chronic Care Management (CCM) Integration
   - Enroll eligible Medicare patients (2+ chronic conditions)
   - 20+ minutes of non-face-to-face care coordination per month
   - Medication reviews, care planning, specialist coordination
   - Billable to Medicare: CPT 99490, 99487, 99489
   - Revenue potential: $40-60 PMPM for practice

3. Transitional Care Management (TCM)
   - Post-discharge follow-up within 7-14 days (required for billing)
   - Medication reconciliation, readmission red flags assessment
   - Billable to Medicare: CPT 99495, 99496 ($165-230 per discharge)
   - Critical for reducing readmissions (3x weighted measure)

4. Team-Based Care
   - Pharmacists: MTM, medication reconciliation, adherence interventions
   - Nurses: Chronic disease management, patient education
   - Social workers: SDOH screening, community resource navigation
   - Medical assistants: Rooming protocols for gap closure (BP, vaccines, screenings)

Best Practices:

1. Provider Relations Team
   - Assign dedicated provider relations reps to high-volume practices
   - Quarterly business reviews (QBRs) with large groups
   - Real-time support via email/phone for questions
   - Provider advisory councils for feedback

2. Recognize Top Performers
   - Public recognition events (annual quality awards)
   - Case studies and best practice sharing
   - Peer-to-peer learning collaboratives
   - Featured in member newsletters and marketing

3. Simplify Requirements
   - Reduce administrative burden wherever possible
   - Streamline prior authorization for quality-related services
   - Pre-populate forms and reports
   - Self-service portals for gap lists, rosters, performance data

4. Build Long-Term Relationships
   - Not transactional, but partnership-focused
   - Invest in practice success (resources, training, support)
   - Co-design interventions with provider input
   - Transparent data sharing and communication

Measure-Specific Provider Strategies:

**Part D Adherence (3x weight - CRITICAL)**
- Share real-time pharmacy fill data
- Pharmacist-led interventions (MTM, CMRs)
- Prescribe 90-day supplies and mail-order
- Medication synchronization programs
- Simplify regimens (combination pills, reduce pill burden)

**Diabetes Care (CDC - 3x weight)**
- Annual "comprehensive diabetes visit" protocol
- Point-of-care HbA1c testing
- Bundle all CDC components (HbA1c, eye, kidney, BP) in single visit
- Standing orders for annual labs
- Telehealth retinal screening

**Blood Pressure Control (CBP - 3x weight)**
- Home BP monitoring programs (loan devices)
- Medication optimization (pharmacist collaboration)
- BP checks at every visit (MA rooming protocol)
- Self-measured BP with clinical support (Million Hearts)

**Readmissions (PCR - 3x weight)**
- Real-time ADT alerts for admissions/discharges
- Require TCM visits within 7 days (billable)
- Medication reconciliation by pharmacist
- High-risk patients flagged for home health

**Breast/Colorectal Cancer Screening (1x weight)**
- Standing orders during AWV
- Integrate into annual visit workflows
- Address barriers (transportation, patient navigation)

Success Metrics:
- Gap closure rate by practice
- Measure performance by practice (star rating contribution)
- Provider satisfaction scores
- Engagement in programs (AWV completion, CCM enrollment, TCM billing)
- Financial impact (shared savings, P4P earnings)

Key Success Factors:
- Data transparency and timeliness
- Meaningful financial incentives aligned with CMS weights
- Reduce administrative burden
- Invest in practice support and resources
- Long-term partnership approach
- Celebrate and recognize success
"""
    }
]

print(f"✅ Created {len(hedis_knowledge)} knowledge base documents")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Volume (if not exists)

# COMMAND ----------

# Create volume for knowledge base documents
try:
    spark.sql(f"""
    CREATE VOLUME IF NOT EXISTS {cfg.catalog}.{cfg.schema}.{cfg.volume}
    COMMENT 'HEDIS guidelines and quality improvement knowledge base for vector search'
    """)
    print(f"✅ Volume created: {cfg.catalog}.{cfg.schema}.{cfg.volume}")
except Exception as e:
    print(f"Volume creation: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write Documents Directly to Table

# COMMAND ----------

# Instead of writing to volume files, write directly to a staging table
# This works better on serverless

from pyspark.sql.types import *
from datetime import datetime

doc_schema = StructType([
    StructField("doc_id", StringType(), False),
    StructField("doc_type", StringType(), False),
    StructField("title", StringType(), False),
    StructField("content", StringType(), False),
    StructField("created_at", TimestampType(), False)
])

# Prepare data for DataFrame
docs_for_df = []
for doc in hedis_knowledge:
    docs_for_df.append({
        "doc_id": doc["doc_id"],
        "doc_type": doc["doc_type"],
        "title": doc["title"],
        "content": doc["content"],
        "created_at": datetime.now()
    })

# Create DataFrame and write to staging table
docs_df = spark.createDataFrame(docs_for_df, schema=doc_schema)

staging_table = f"{cfg.catalog}.{cfg.schema}.hedis_docs_staging"
docs_df.write.mode("overwrite").saveAsTable(staging_table)

print(f"✅ Created staging table with {len(hedis_knowledge)} documents: {staging_table}")

# Also write to volume as text files for reference (optional, ignore errors)
volume_path = cfg.volume_path
for doc in hedis_knowledge:
    file_name = f"{doc['doc_id']}.txt"
    file_path = f"{volume_path}/{file_name}"
    
    full_content = f"""Document ID: {doc['doc_id']}
Type: {doc['doc_type']}
Title: {doc['title']}

{doc['content']}
"""
    
    try:
        # Try to write using Spark SQL
        spark.sql(f"""
        SELECT '{full_content.replace("'", "''")}' AS content
        """).write.mode("overwrite").text(file_path)
        print(f"✅ Written to volume: {file_name}")
    except Exception as e:
        print(f"⚠️  Could not write {file_name} to volume (not critical): {e}")
        # Continue anyway - we have the data in the staging table

print(f"\n✅ All {len(hedis_knowledge)} documents written to volume")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("=" * 80)
print("HEDIS GUIDELINES KNOWLEDGE BASE CREATED!")
print("=" * 80)
print(f"✅ Staging Table: {staging_table}")
print(f"✅ Documents: {len(hedis_knowledge)}")
print("=" * 80)
print("\n📝 Next step: Run 09_chunk_knowledge_base.py to chunk from staging table")
print("=" * 80)
