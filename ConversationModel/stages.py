# Healthcare RCM Conversation Stages
# Based on healthcare_rcm/config/conversation_templates.yaml

PRIOR_AUTH_CONVERSATION_STAGES = {
    "1": "Introduction & Verification: Greet professionally, state your name, role, and company. Mention provider name and NPI. Clearly state purpose: prior authorization request for specific procedure. Verify you've reached the correct department.",
    "2": "Patient Demographics: Provide patient name, date of birth, and member ID. Verify active coverage and eligibility. Ensure patient is found in the system.",
    "3": "Procedure Request: State the CPT procedure code, procedure name, ICD diagnosis code, and proposed service date. Ensure the authorization request is initiated.",
    "4": "Medical Necessity: Explain clinical presentation, failed conservative treatments, duration and severity of symptoms, and impact on patient's quality of life. Address clinical criteria for approval.",
    "5": "Documentation Discussion: Ask what documentation is required, confirm submission method (fax/portal), get submission deadline and fax number. Clarify any specific forms needed.",
    "6": "Timeline & Urgency: Confirm standard turnaround time. If urgent or stat, explain urgency and request expedited review. Get expected decision date.",
    "7": "Escalation Check: If medical necessity is questioned, offer peer-to-peer with clinical director. If clinical criteria not met, request specific requirements. Document escalation path if needed.",
    "8": "Reference Number: Request and document authorization reference number. Get representative's name and ID. Get direct callback number. Repeat reference number for confirmation.",
    "9": "Next Steps Confirmation: Summarize what was discussed. Confirm next steps and timeline. Confirm notification method (phone/fax/portal). Ensure all parties are aligned.",
    "10": "Professional Close: Thank representative for their assistance. Confirm you have all necessary information. Professional goodbye. Output <END_OF_CALL> to mark that the call should end now."
}

DENIAL_MANAGEMENT_CONVERSATION_STAGES = {
    "1": "Introduction & Claim Identification: State your name, role, and company. Provide claim number, service date, and denial code. Verify claim is located in system.",
    "2": "Denial Clarification: Request detailed explanation of denial. Ask for specific reason beyond denial code. Confirm understanding of what triggered the denial.",
    "3": "Resolution Discussion: Ask about resolution options. Inquire whether resubmission or formal appeal is needed. Understand the correction process and identify path forward.",
    "4": "Documentation Requirements: Get complete list of required documents. Confirm submission method (fax/portal/mail). Get submission deadline. Clarify any specific forms or attestations needed.",
    "5": "Timeline Confirmation: Confirm reprocessing timeline. Get appeal deadline if applicable. Request expected decision date. Document all deadlines.",
    "6": "Escalation Assessment: If appeal required, get appeal process details. If peer-to-peer needed, request scheduling process. If medical review necessary, understand requirements. Document escalation path.",
    "7": "Reference Documentation: Get reference number for this inquiry. Document representative name and ID. Get direct callback number. Confirm contact for follow-up.",
    "8": "Next Steps Summary: Recap what will be submitted. Confirm timeline for submission. Confirm follow-up process. Ensure all parties are aligned.",
    "9": "Professional Close: Thank representative. Confirm next contact point. Professional goodbye. Output <END_OF_CALL> to mark that the call should end now."
}

INSURANCE_VERIFICATION_CONVERSATION_STAGES = {
    "1": "Introduction & Purpose: State your name, role, and company. State purpose: insurance verification. Verify you've reached the correct department.",
    "2": "Patient Identification: Provide patient name, date of birth, and member ID. Verify patient is found in system.",
    "3": "Coverage Verification: Confirm active coverage. Verify effective dates. Confirm plan type.",
    "4": "Benefits Inquiry: Ask about deductible (met/remaining). Ask about co-insurance percentage. Ask about out-of-pocket maximum. Verify in-network status of provider.",
    "5": "Procedure-Specific Benefits: Inquire about coverage for specific CPT code. Ask about prior authorization requirements. Get pre-certification requirements if any.",
    "6": "Documentation: Request reference number. Get representative name. Document all benefit details.",
    "7": "Professional Close: Thank representative. Confirm all information captured. Output <END_OF_CALL> to mark that the call should end now."
}


#### Create your own ####
#     --> `key` : stage_number(string)
#     --> 'value` : description_of_stage