"""
NHS Navigator Knowledge Base
Static FAQ + guidance content for the AI chatbot.
Topics: GP registration, A&E vs GP vs 111, translation rights,
        appointment prep, prescriptions, mental health, refugee rights.
"""

NHS_KNOWLEDGE_BASE = [
    {
        "topic": "GP registration",
        "keywords": ["register", "gp", "doctor", "sign up", "family doctor", "primary care"],
        "content": """
To register with a GP (General Practitioner / family doctor) in England:
1. Find a GP surgery near you at nhs.uk/find-a-gp
2. Contact the surgery and ask to register — you do NOT need proof of address or immigration status.
3. You may be asked to fill in a registration form (GMS1).
4. You have the right to register even if you are an asylum seeker, refugee, or have no fixed address.
5. If a GP refuses to register you without good reason, contact NHS England on 0300 311 22 33.
Source: NHS England — https://www.nhs.uk/nhs-services/gps/how-to-register-with-a-gp-surgery/
"""
    },
    {
        "topic": "A&E vs GP vs 111",
        "keywords": ["emergency", "a&e", "111", "urgent", "when to go", "hospital", "ambulance", "999"],
        "content": """
When to use each service:
- 999 / A&E (Accident & Emergency): Life-threatening emergencies — chest pain, difficulty breathing, severe bleeding, unconsciousness, stroke symptoms.
- NHS 111 (call or visit 111.nhs.uk): Urgent but not life-threatening — you need medical help fast but it's not an emergency. Available 24/7, free, interpreters available.
- GP (your family doctor): Non-urgent health problems, ongoing conditions, repeat prescriptions, referrals to specialists.
- Pharmacy: Minor illnesses, advice on medicines, some treatments without a prescription.
Do NOT go to A&E for things a GP or 111 can handle — it causes long waits for everyone.
Source: NHS — https://www.nhs.uk/nhs-services/urgent-and-emergency-care-services/
"""
    },
    {
        "topic": "interpreter and translation rights",
        "keywords": ["interpreter", "translator", "translation", "language", "speak", "understand", "arabic", "farsi", "somali"],
        "content": """
You have the right to an interpreter when accessing NHS services:
- You can request a professional interpreter for any NHS appointment — GP, hospital, mental health.
- This is FREE. You should never be charged.
- You can ask for a face-to-face interpreter, telephone interpreter, or video interpreter.
- Do NOT rely on family members or children to interpret medical information — this is not best practice and you can insist on a professional.
- Tell the GP surgery or hospital in advance that you need an interpreter so they can arrange one.
- If you are refused an interpreter, you can raise a complaint with the NHS trust or PALS (Patient Advice and Liaison Service).
Source: NHS — https://www.nhs.uk/using-the-nhs/nhs-services/
"""
    },
    {
        "topic": "appointment preparation",
        "keywords": ["appointment", "prepare", "bring", "visit", "consultation", "what to bring", "what to expect"],
        "content": """
How to prepare for a GP or hospital appointment:
- Bring your NHS number if you have one (on any NHS letter).
- Bring a list of your current medications and dosages.
- Bring any relevant medical documents, test results, or letters.
- Write down your symptoms: when they started, how severe, what makes them better or worse.
- Prepare a list of questions you want to ask.
- If you need an interpreter, confirm this when booking.
- Arrive 10–15 minutes early.
- You can bring a friend or family member for support (but they should not interpret for you).
- You can ask the doctor to explain anything you don't understand — it is your right.
"""
    },
    {
        "topic": "prescriptions",
        "keywords": ["prescription", "medicine", "medication", "free prescription", "exemption", "pharmacy", "cost"],
        "content": """
About NHS prescriptions:
- Standard prescription charge in England is £9.90 per item (2024).
- You may be entitled to FREE prescriptions if you are: under 16, 16–18 and in full-time education, 60 or over, pregnant or had a baby in the last 12 months, have a qualifying medical condition (e.g. diabetes, epilepsy), receiving certain benefits (Universal Credit, Income Support, etc.).
- Asylum seekers receiving support from the Home Office are usually entitled to free prescriptions.
- Ask your GP or pharmacist if you are unsure — they can advise on exemptions.
- A Prescription Prepayment Certificate (PPC) saves money if you need more than 3 items in 3 months.
Source: NHS — https://www.nhs.uk/nhs-services/prescriptions-and-pharmacies/
"""
    },
    {
        "topic": "mental health support",
        "keywords": ["mental health", "anxiety", "depression", "stress", "trauma", "ptsd", "counselling", "therapy", "talking therapy"],
        "content": """
Mental health support available on the NHS:
- Talk to your GP first — they can refer you to local mental health services.
- IAPT (Improving Access to Psychological Therapies): Free talking therapies for anxiety and depression. You can self-refer at nhs.uk/mental-health/talking-therapies-medicine-treatments/
- Crisis support: If you are in mental health crisis, call 111 (option 2) or go to A&E.
- Samaritans: 116 123 (free, 24/7, confidential).
- Many areas have specialist services for refugees and asylum seekers with trauma/PTSD — ask your GP for a referral.
- Interpreters are available for mental health appointments.
Source: NHS — https://www.nhs.uk/mental-health/
"""
    },
    {
        "topic": "refugee and asylum seeker healthcare rights",
        "keywords": ["refugee", "asylum", "rights", "entitlement", "free", "nhs", "immigration", "visa", "undocumented"],
        "content": """
Healthcare rights for refugees and asylum seekers in England:
- Asylum seekers and refugees are entitled to FREE NHS primary care (GP) and emergency treatment.
- You do NOT need to prove immigration status to register with a GP or access emergency care.
- Secondary care (hospital treatment) is generally free for asylum seekers with an active claim and recognised refugees.
- Undocumented migrants are entitled to free emergency treatment and GP care.
- Maternity services are free regardless of immigration status.
- Dental treatment and eye tests may be free if you receive asylum support (NASS).
- You cannot be refused urgent or emergency treatment due to inability to pay.
Source: Doctors of the World — https://www.doctorsoftheworld.org.uk/
Source: NHS — https://www.nhs.uk/nhs-services/
"""
    },
    {
        "topic": "dental and eye care",
        "keywords": ["dentist", "dental", "teeth", "eye", "optician", "glasses", "vision", "sight"],
        "content": """
Dental and eye care for refugees and asylum seekers:
- NHS dental treatment: You may be entitled to free NHS dental care if you receive certain benefits or asylum support. Check at nhs.uk/find-a-dentist.
- Eye tests: Free NHS eye tests if you receive qualifying benefits or asylum support.
- Glasses: You may get a voucher towards the cost of glasses if you qualify.
- Ask your GP or local pharmacy for advice on accessing these services.
Source: NHS — https://www.nhs.uk/nhs-services/dentists/
"""
    },
    {
        "topic": "maternity services",
        "keywords": ["pregnant", "pregnancy", "maternity", "baby", "midwife", "antenatal", "birth"],
        "content": """
Maternity services for refugees and asylum seekers:
- Maternity care is FREE on the NHS regardless of immigration status.
- Register with a GP as soon as possible when pregnant — they will refer you to a midwife.
- Antenatal (before birth) and postnatal (after birth) care is included.
- Interpreters are available for all maternity appointments.
- You are entitled to a midwife and to give birth in an NHS hospital.
Source: NHS — https://www.nhs.uk/pregnancy/
"""
    },
    {
        "topic": "PALS and complaints",
        "keywords": ["complaint", "pals", "unhappy", "problem", "refused", "rights", "advocate"],
        "content": """
If you have a problem with NHS care:
- PALS (Patient Advice and Liaison Service): Every NHS trust has a PALS team. They help resolve concerns informally. Find your local PALS at nhs.uk/find-a-pals.
- If you are refused treatment or registration unfairly, PALS can help.
- You can also contact Healthwatch England or your local Healthwatch.
- For serious complaints, contact the Parliamentary and Health Service Ombudsman.
- Doctors of the World and Refugee Council can also provide advocacy support.
"""
    },
]

# Disclaimer appended to every response
DISCLAIMER = (
    "⚠️ This information is for general guidance only and does not constitute medical advice. "
    "For medical concerns, please consult a qualified healthcare professional, call NHS 111, or visit your GP."
)
