# Updated app/service/workflow_service.py

from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_core.messages import HumanMessage, AIMessage
import json
import uuid
import re
import requests

# GraphState defines the state passed in the workflow.
class GraphState(TypedDict, total=False):
    user_input: str
    use_decision_engine: bool
    rule_validation_needed: bool
    form_type: str
    file_path: str
    extracted_data: Dict[str, Any]
    db_data: Dict[str, Any]
    combined_data: Dict[str, Any]
    validation_result: Dict[str, Any]
    error: str
    final_response: str
    conversation_id: str
    memory: Dict[str, Any]
    remaining_rules: List[Dict[str, str]]
    remaining_retrieval_rules: List[Dict[str, str]]
    rule_results: List[Any]
    overall_decision: str
    current_rule: Dict[str, str]
    current_retrieval_rule: Dict[str, str]
    continue_validation: bool
    rag_service: object
    llm:object
    validation_response:str
# ---------------------------
# New Helper Function: Load Rules
# ---------------------------

def load_retrieval_rules() -> List[Dict[str,str]]:
    retrieval_rules = [
        {
    "nigo_id": "REN.NM.004",
    "question": "What is Guarantee Period?"
  },
  {
    "nigo_id": "REN.NM.001",
    "question": "What is Current Guarantee Period, Requested Guarantee Period?"
  },
  {
    "nigo_id": "REN.NM.023",
    "question": "What is LastAnniversaryDate?"
  },
  {
    "nigo_id": "REN.NM.003",
    "question": "What is Owner FullName, FirstName, LastName??"
  },
  {
    "nigo_id": "REN.NM.002",
    "question": "What is Contract Number?"
  },
  {
    "nigo_id": "REN.NM.010",
    "question": "What is Contract Status, Ref_Contract?"
  },
#   {
#     "nigo_id": "REN.NM.005",
#     "question": "What is Signature Date, Signature Type?"
#   },
  {
    "nigo_id": "REN.NM.006",
    "question": "What is Channel, Signature?"
  },
  {
    "nigo_id": "REN.NM.012",
    "question": "What is Contract Plan Code, Ref_Product?"
  },
  {
    "nigo_id": "REN.NM.013",
    "question": "What is Issue State, Owner/Annuitant's Date of Birth, Issue Date?"
  },
  {
    "nigo_id": "REN.NM.014",
    "question": "What is Issue State, Issue Date?"
  },
#   {
#     "nigo_id": "REN.NM.015",
#     "question": "What is Guarantee Period, Owner/Annuitant DOB, Contract Issue Date?"
#   },
#   {
#     "nigo_id": "REN.NM.016",
#     "question": "What is client DOB?"
#   },
#   {
#     "nigo_id": "REN.NM.017",
#     "question": "What is Owner Name, Joint Owner Name, Contract Number, Guarantee Period, Case ID, Document Number, renewalRequestSignDate?"
#   },
#   {
#     "nigo_id": "REN.NM.018",
#     "question": "What is Channel, Printed Name?"
#   },
#   {
#     "nigo_id": "REN.NM.019",
#     "question": "What is Ownership Type, Title?"
#   },
#   {
#     "nigo_id": "REN.NM.020",
#     "question": "What is Transaction on Anniversary?"
#   },
#   {
#     "nigo_id": "REN.NM.021",
#     "question": ""
#   },
#   {
#     "nigo_id": "REN.NM.024",
#     "question": "What is Client Type, Signature Date, Ref_StalePeriod?"
#   },
#   {
#     "nigo_id": "REN.NM.022",
#     "question": "What is Client Type, Stale Period, Ref_StalePeriod?"
#   },
  {
    "nigo_id": "REN.NM.025",
    "question": "What is Issue State, guarantee period, External ID in LI State Requirement Review?"
  },
#   {
#     "nigo_id": "REN.NM.034",
#     "question": "What is Account Code, Next Anniversary Date, tdRnewDate?"
#   }
]
    return retrieval_rules
def load_rules() -> List[Dict[str, str]]:
    """
    Returns a list of rule definitions based on the mermaid flowchart.
    Each rule is represented as a dictionary with a NIGO id and a description.
    """
    rules = [
        {"nigo_id": "REN.NM.004", "description": "If Guarantee Period attribute is missing in ocr data, flag the form."},
        {"nigo_id": "REN.NM.001", "description": "If the current guarantee period is not equal to 1 year, then check whether the current period is one of 3, 4, or 5 and the requested guarantee period is one of 1, 3, 4, or 5. If this condition is not met, flag the form."},
        {"nigo_id": "REN.NM.023", "description": "After calling PolicyInfo API to retrieve LastAnniversaryDate, if it equals 2999-12-31T00:00:00, flag the form."},
        {"nigo_id": "REN.NM.003", "description": "Match for full name in db data and ocr data , if not present check of first name and last name  with the ocr name else flag the form."},
        {"nigo_id": "REN.NM.002", "description": "If Contract Number attribute is missing in OCR data or does not match the value from db data, flag the form."},
        {"nigo_id": "REN.NM.010", "description": "If Contract Status is not ACTIVE, flag the form."},
        #  {"nigo_id": "REN.NM.005", "description": "If Signature Date attribute does not match Signature Type attribute, flag the form."},
        {"nigo_id": "REN.NM.006", "description": "If the channel is not Phone and Signature Date is missing in ocr, flag the form."},
        {"nigo_id": "REN.NM.012", "description": " Extract plan code and check If Contract PlanCode is not present in db data , flag the form."},
        {"nigo_id": "REN.NM.013", "description": "If Issue State is FL and the Owner/Annuitant's age is 65 or older at Issue Date, flag the form."},
        {"nigo_id": "REN.NM.014", "description": "extract issue state and issue date and If Issue State is not MT continue, else if Issue Date is on or after 2018-01-01, flag the form."},
        # {"nigo_id": "REN.NM.015", "description": "Compare Guarantee Period against allowed limit based on the 90th birthday of the oldest owner/annuitant and 10 years after the Contract Issue Date; if outside the allowed range, flag the form."},
        # {"nigo_id": "REN.NM.016", "description": "If the Date of Birth of the owner/annuitant is not available, flag the form."},
        # {"nigo_id": "REN.NM.017", "description": "If one or more required fields (e.g., Owner Name, Joint Owner Name, Contract Number, Guarantee Period, Signatures, Dates, Good Order Date, Case ID, Document Number, renewalRequestSignDate, etc.) are missing, flag the form."},
        # {"nigo_id": "REN.NM.018", "description": "If the channel is not Phone and Printed Name is missing, flag the form."},
        # {"nigo_id": "REN.NM.019", "description": "If the contract is trust-owned and Title is missing, flag the form."},
        # # {"nigo_id": "REN.NM.020", "description": "If a transaction on Anniversary is detected via LifeCad API, flag the form."},
        # #{"nigo_id": "REN.NM.021", "description": "After validations, if not all checks are IGO, flag the form."},
        # {"nigo_id": "REN.NM.024", "description": "For client MASS, if Sign Date is outside the allowed stale period (per Ref_SlatePeriod), flag the form."},
        # # {"nigo_id": "REN.NM.022", "description": "For clients other than MASS, if the stale period condition is not met, flag the form."},
        {"nigo_id": "REN.NM.025", "description": "For Issue State NY and guarantee period 3, 4, or 5, if the External ID is invalid in the LI State Requirement Review, flag the form."},
        # {"nigo_id": "REN.NM.034", "description": "Compare the account code from accountQuote with the getTransactionDetails API; if Next Anniversary Date does not match tdRnewDate, flag the form."}
  ]
    return rules

# ---------------------------
# New Node: DB Data Fetch
# ---------------------------
def fetch_db_data_node(state: GraphState) -> GraphState:

#     db_data = {
#         "Policy Role":
# {
#             "clientRoleDetails": {
#                 "prEligibleBeneInhIra": "null",
#                 "roleId": -2,
#                 "roleIdDesc": "Beneficiary",
#                 "roleOptionId": 0,
#                 "roleOptionIdDesc": "Primary",
#                 "roleCountId": 3,
#                 "rolePercent": 100.0,
#                 "roleStatus": "C",
#                 "roleStatusDesc": "Active",
#                 "roleEffDate": "2018-01-04",
#                 "roleEndDate": "2999-12-31",
#                 "taxToNameId": -999,
#                 "taxToOptionId": -999,
#                 "taxToRoleId": -999,
#                 "relationshipId": -999,
#                 "relationshipDesc": "N/A",
#                 "cftgIndicatorInd": "null",
#                 "cftgIndicatorValue": -999,
#                 "cftgPayoutOptionValue": "null",
#                 "cftgPayoutOptionDesc": "null",
#                 "prevContactDate": "2999-12-31",
#                 "lastContactDate": "null",
#                 "nameId": 1808553805,
#                 "addressSeasonal": 0,
#                 "addressId": 8713223,
#                 "phoneId": -999
#             },
#             "clientDetail": {
#                 "client": {
#                     "nmFirstDate": "2017-12-27",
#                     "clientType": "IN",
#                     "clientTypeDesc": "Individual",
#                     "nameId": 1808553805,
#                     "companyClientId": "null",
#                     "fullName": "sarn sarams",
#                     "taxId": "878445444",
#                     "taxIdLast4": "5444",
#                     "imoIndicator": "false",
#                     "taxIdVerifiedInd": "null",
#                     "externalId": "null",
#                     "emailId": "null",
#                     "companyCode": "null",
#                     "companyName": "null",
#                     "companyAbbrName": "null",
#                     "companyCarrierCode": "null",
#                     "trustTypeId": -999,
#                     "trustTypeDesc": "None",
#                     "salute": "null",
#                     "firstName": "sarn",
#                     "middleName": "null",
#                     "lastName": "sarams",
#                     "maidName": "null",
#                     "nameSuffix": "null",
#                     "sex": "M",
#                     "sexDesc": "Male",
#                     "marriedStatus": -999,
#                     "marriedStatusDesc": "Default",
#                     "dob": "1960-01-01",
#                     "birthCity": "null",
#                     "birthStateCode": "$$",
#                     "birthStateDesc": "Default",
#                     "height": "null",
#                     "weight": 0,
#                     "smokerInd": "null",
#                     "occupation": "null",
#                     "employer": "null",
#                     "salary": 0,
#                     "jobLocation": "null",
#                     "jobStateCode": "$$",
#                     "deathDate": "null",
#                     "deathNotificationDate": "2999-12-31",
#                     "dateOfDueProof": "2999-12-31",
#                     "w8Receiptdate": "2999-12-31",
#                     "w8StatusInd": "N",
#                     "intlAnnuityInd": "null",
#                     "file": "null",
#                     "validTaxIdInd": "null"
#                 },
#                 "addresses": [
#                     {
#                         "addressId": 8713223,
#                         "addressType": "$$",
#                         "addressTypeDesc": "Default",
#                         "addressLine1": "dfgdf",
#                         "addressLine2": "null",
#                         "addressLine3": "null",
#                         "city": "topeka",
#                         "stateCode": "KS",
#                         "stateCodeDesc": "KANSAS",
#                         "zipCode": "66615",
#                         "zipSuffix": "null",
#                         "countryCode": "USA",
#                         "countryDesc": "United States",
#                         "countryShortDesc": "USA",
#                         "mailZone": "null",
#                         "zipWalkRoute": "null",
#                         "effStartDate": "2018-01-04",
#                         "effEndDate": "2999-12-31",
#                         "seasonalAddressInd": "null",
#                         "seasonalAddressIndDesc": "null",
#                         "roleAddress": "true"
#                     }
#                 ],
#                 "phones": [
#                     {
#                         "addressId": 8713223,
#                         "phoneId": -999,
#                         "phoneType": "$$",
#                         "phoneTypeDesc": "Default",
#                         "phoneNumber": "null",
#                         "phoneAreaCode": "null",
#                         "phoneExc": "null",
#                         "phoneExt": "null",
#                         "phoneSuffix": "null",
#                         "phoneCountryCode": "$$",
#                         "phoneCountryDesc": "Non Specified",
#                         "phoneCountryShortDesc": "$$",
#                         "phoneDayNight": "$$",
#                         "phoneDayNightDesc": "Any",
#                         "phoneStartDate": "null",
#                         "phoneEndDate": "null",
#                         "rolePhone": "true"
#                     }
#                 ],
#                 "addressCascadeInd": "false",
#                 "gbOptions": "null",
#                 "addNewAddressPhoneInd": "false",
#                 "addressCascadeList": "null"
#             },
#             "bankDetails": [],
#             "withholdingDetail": {
#                 "federalDollar": 0.0,
#                 "federalPercentage": 0.0,
#                 "federalTaxRatesToUseCode": 0,
#                 "federalTaxRatesToUseDesc": "Default",
#                 "federalExemption": 0,
#                 "federalFilingStatusCode": -999,
#                 "federalFilingStatusDesc": "Default",
#                 "stateDollar": 0.0,
#                 "statePercentage": 0.0,
#                 "stateTaxRatesToUseCode": 0,
#                 "stateTaxRatesToUseDesc": "Default",
#                 "stateExemption": 0,
#                 "stateFilingStatusCode": -999,
#                 "stateFilingStatusDesc": "Default",
#                 "backupDollar": 0.0,
#                 "backupPercentage": 0.0
#             }
#         },

# "Get Transaction History":
# {
#     "apiRequestHeader": {
#         "externalId": "null",
#         "externalUserId": "null",
#         "externalSystemId": "null",
#         "externalUserCompHrchyId": "null",
#         "muleCorrelationId": "null",
#         "correlationId": "null",
#         "timestamp": "null",
#         "apiRequestUUID": "bf507a4d-56cc-40c1-a3b0-92feb90c7573",
#         "apiName": "GetTransactionHistory",
#         "externalTransactionName": "null",
#         "clientCode": "null",
#         "externalUserIDValid": "false"
#     },
#     "requestParam": {
#         "itlanndate": "2999-12-31",
#         "companyid": "894039104",
#         "transType": "all",
#         "todate": "2999-12-31",
#         "top": "all",
#         "transstatus": "%",
#         "contractnumber": "571003597",
#         "inlineCount": "all",
#         "skip": "0",
#         "companyhierarchyid": "894039104",
#         "queryId": "getTransactionHistory",
#         "fromdate": "1900-01-01"
#     },
#     "status": {
#         "statusCode": "Success",
#         "statusMessage": "Request processed successfully",
#         "errors": [],
#         "policyDetails": "null"
#     },
#     "responseData": [
#         {
#             "transactionNumber": 39150090,
#             "transactionType": 25,
#             "transactionTypeCode": "HK",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2025-01-04",
#             "transactionProcessDate": "2025-01-06",
#             "transactionLastDate": "2025-01-06",
#             "transactionTaxYear": "2025",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 116868.15,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2025,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 39673159,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 16,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 39150094,
#             "transactionType": 60,
#             "transactionTypeCode": "G6",
#             "transactionTypeDesc": "Rate Renewal",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2025-01-04",
#             "transactionProcessDate": "2025-01-06",
#             "transactionLastDate": "2025-01-06",
#             "transactionTaxYear": "2025",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 116868.15,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2025,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 39673163,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 10,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 34907578,
#             "transactionType": 25,
#             "transactionTypeCode": "HK",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2024-01-04",
#             "transactionProcessDate": "2024-01-04",
#             "transactionLastDate": "2024-01-04",
#             "transactionTaxYear": "2024",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 114289.51,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2024,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 35398628,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 16,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 30642973,
#             "transactionType": 25,
#             "transactionTypeCode": "HK",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2023-01-04",
#             "transactionProcessDate": "2023-01-04",
#             "transactionLastDate": "2023-01-04",
#             "transactionTaxYear": "2023",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 111774.58,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2023,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 31103128,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 16,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 27390007,
#             "transactionType": 25,
#             "transactionTypeCode": "HK",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2022-01-04",
#             "transactionProcessDate": "2022-01-04",
#             "transactionLastDate": "2022-01-04",
#             "transactionTaxYear": "2022",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 109314.99,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2022,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 27818470,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 16,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 23301559,
#             "transactionType": 25,
#             "transactionTypeCode": "HK",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2021-01-04",
#             "transactionProcessDate": "2021-01-04",
#             "transactionLastDate": "2021-01-04",
#             "transactionTaxYear": "2021",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 106909.53,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2021,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 23721447,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 16,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 20817631,
#             "transactionType": 25,
#             "transactionTypeCode": "HK",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2020-01-04",
#             "transactionProcessDate": "2020-01-06",
#             "transactionLastDate": "2020-01-06",
#             "transactionTaxYear": "2020",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 104550.62,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2020,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 21218093,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 16,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 17177017,
#             "transactionType": 25,
#             "transactionTypeCode": "HK",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2019-01-04",
#             "transactionProcessDate": "2019-01-04",
#             "transactionLastDate": "2019-01-04",
#             "transactionTaxYear": "2019",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 102250.0,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2019,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 17491068,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 16,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 13345649,
#             "transactionType": 133,
#             "transactionTypeCode": "J8",
#             "transactionTypeDesc": "Feature Change",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2018-01-04",
#             "transactionProcessDate": "2018-01-04",
#             "transactionLastDate": "2018-01-04",
#             "transactionTaxYear": "2018",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 100000.0,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2018,
#             "charge": 0.0,
#             "restrictCharge": 3,
#             "disbNumber": 13599661,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 27,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 13345651,
#             "transactionType": 4,
#             "transactionTypeCode": "A8",
#             "transactionTypeDesc": "Issue",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2018-01-04",
#             "transactionProcessDate": "2018-01-04",
#             "transactionLastDate": "2018-01-04",
#             "transactionTaxYear": "2018",
#             "transactionAmount": 0.0,
#             "amountType": 0,
#             "amountTypeDesc": "Auto",
#             "grossAmount": 0.0,
#             "investedValueAmount": 100000.0,
#             "tlRefund": 0.0,
#             "netAmount": 0.0,
#             "isContribution": 0.0,
#             "transactionYear": 2018,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 13599664,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 0,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 4,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         },
#         {
#             "transactionNumber": 13345650,
#             "transactionType": 1,
#             "transactionTypeCode": "A2",
#             "transactionTypeDesc": "Initial Premium",
#             "transactionStatus": "D",
#             "transactionStatusDesc": "Done",
#             "transactionDate": "2018-01-04",
#             "transactionProcessDate": "2018-01-04",
#             "transactionLastDate": "2018-01-04",
#             "transactionTaxYear": "2018",
#             "transactionAmount": 100000.0,
#             "amountType": 2,
#             "amountTypeDesc": "Percentage",
#             "grossAmount": 100000.0,
#             "investedValueAmount": 100000.0,
#             "tlRefund": 0.0,
#             "netAmount": 100000.0,
#             "isContribution": 1.0,
#             "transactionYear": 2018,
#             "charge": 0.0,
#             "restrictCharge": 0,
#             "disbNumber": 13599663,
#             "policyMaturityDate": "2050-01-01",
#             "listBillDate": "null",
#             "suspenceNumber": 369166,
#             "payoutFlag": "N",
#             "netOrGrossFlag": "null",
#             "loanId": -999,
#             "archiveFlag": 0,
#             "enhBenLostInd": 0,
#             "taxAggregationCounter": 0,
#             "transactionProcessOrder": 2,
#             "dtId": "null",
#             "errorStatus": 0,
#             "oldTransactionId": -999
#         }
#     ],
#     "inlineCount": 11
# },

# "GetAccountInfo":
# {
#     "SourceSystem": "LC",
#     "ContractNumber": "571003597",
#     "ContractId": "269430",
#     "CovId": "0",
#     "OwnerName": "sarams, sarn",
#     "QualTypeCode": "Non-Qualified",
#     "QualTypeDesc": "Non-Qualified",
#     "APPLICATIONDATE": "2018-01-04T00:00:00",
#     "ProductLine": "ANNUITY",
#     "ModifiedEndowmentStatus": "0",
#     "MaturityDate": "2050-01-01T00:00:00",
#     "ProductCategory": "FIXED",
#     "ProductName": "Stable Voyage",
#     "IssueState": "KS",
#     "IssueDate": "2018-01-04T00:00:00",
#     "IssueAge": "58",
#     "ContractStatus": "ACTIVE",
#     "PlanCode": "571",
#     "ModelName": "null",
#     "eDeliveryStatus": "null",
#     "OnlineTransactionAuthorized": 0,
#     "OnlineTransactionAuthCode": 0,
#     "DeathBenefit": "Standard Death Benefit",
#     "SurrenderChargePeriod": "null",
#     "MVAProduct": "N",
#     "ProductShareClass": "null",
#     "ProductCompanyId": 39,
#     "WithdrawalChargePeriod": "null",
#     "SrcQualTypeCode": "1",
#     "SrcProductLine": "null",
#     "SrcProductCategory": "null",
#     "SrcProductName": "MassMutual Stable Voyage",
#     "SrcIssueState": "KS",
#     "SrcContractStatus": "A",
#     "SrcProductCompanyId": "571",
#     "JurisdictionStateCode": "KS",
#     "LastAnniversaryDate": "2025-01-04T00:00:00",
#     "NextAnniversaryDate": "2026-01-04T00:00:00",
#     "LastTransactionDate": "2025-01-04T00:00:00",
#     "LTCIndicator": 0,
#     "ActualOwnerName": "sarams, sarn",
#     "AnnuitantName": "sarams, sarn",
#     "OverrideOwnerName": "false"
# },

# "Get Account Quote":
# {
#     "apiRequestHeader": {
#         "externalId": "null",
#         "externalUserId":  "null",
#         "externalSystemId":  "null",
#         "externalUserCompHrchyId":  "null",
#         "muleCorrelationId":  "null",
#         "correlationId":  "null",
#         "timestamp":  "null",
#         "apiRequestUUID": "b1cbe04c-8e32-47d2-9b8c-8925930fd801",
#         "apiName": "GetAccountQuote",
#         "externalTransactionName":  "null",
#         "clientCode":  "null",
#         "externalUserIDValid":  "null"
#     },
#     "policyCommonRequest": {
#         "contractNumber": "571003597",
#         "companyId": 903908434,
#         "companyHierarchyId": 894039104,
#         "planCode": "571",
#         "policyNumber": 269430,
#         "cvgId": 0
#     },
#     "status": {
#         "statusCode": "Success",
#         "statusMessage": "Request processed successfully",
#         "errors": [],
#         "policyDetails": "null"
#     },
#     "valuationDate": "2025-04-11",
#     "accountQuoteSummary": {
#         "accountQuoteValues": [
#             {
#                 "contribution": "NA",
#                 "subContribution": "NA",
#                 "division": "3 Yr Guarantee",
#                 "chAccount": "PJ",
#                 "chDivision": "01",
#                 "units": 0.0,
#                 "value": 0.0,
#                 "balance": 117789.81,
#                 "percentage": 100.0,
#                 "fundName": "3 Year Guarantee"
#             }
#         ],
#         "totalUnits": 0.0,
#         "totalBalance": 117789.81,
#         "totalPercentage": 100.0
#     }
# },

# "getTransactionalDetail":
# {
#     "status": {
#         "statusCode": "Success",
#         "statusMessage": "Request processed successfully",
#         "errors": []
#     },
#     "transactionDetails": {
#         "result": {
#             "resultDetails": [],
#             "total": "0.0"
#         },
#         "request": {
#             "transactionType": "25",
#             "transactionTypeDesc": "Contract Anniversary",
#             "transactionDate": "2025-01-04",
#             "transactionOption": "0",
#             "total": "0.00",
#             "productPlanType": "Deferred Annuity",
#             "contribution": "NA",
#             "indicator": "None",
#             "grossDisbursement": "false",
#             "requestDetails": [],
#             "dollarTotal": "0.0",
#             "percentTotal": "0.0"
#         },
#         "accountValue": {
#             "accountValueDetails": [
#                 {
#                     "contribution": "NA",
#                     "subContribution": "NA",
#                     "chAccount": "PJ",
#                     "chDivision": "01",
#                     "division": "3 Year Guarantee",
#                     "units": "0.0",
#                     "unitValue": "0.0",
#                     "amount": "116868.15"
#                 }
#             ],
#             "total": "116868.15"
#         },
#         "fees": {
#             "charges": {
#                 "chargesDetail": [],
#                 "total": "0.0"
#             },
#             "expenses": {
#                 "expensesDetail": [],
#                 "total": "0.0"
#             },
#             "waivedCharges": {
#                 "waivedChargesDetail": [],
#                 "total": "0.0"
#             },
#             "featureFee": {
#                 "featureFeeDetail": [],
#                 "total": "0.0"
#             }
#         },
#         "disburse": {
#             "disburseDetails": [],
#             "applyToSuspense": "0",
#             "transactionLevelWithholding": {},
#             "multipleChecks": "0",
#             "replacement": "0"
#         },
#         "confirm": {
#             "additionalSoaRecipientNoOption": "0",
#             "advisorFeePayeeLimitedPowerOfAttorney": "0",
#             "advisorFeePayeeNoOption": "0",
#             "agentAgentOfRecord": "0",
#             "agentNonCommissionAgent": "0",
#             "annuitantInsuredContingent": "0",
#             "annuitantInsuredJoint": "0",
#             "annuitantInsuredPrimary": "0",
#             "annuitantBenefContingent": "0",
#             "annuitantBenefIrrevocable": "0",
#             "annuitantBenefPrimary": "0",
#             "assigneeNoOption": "0",
#             "beneficiaryContingent": "0",
#             "beneficiaryIrrevocable": "0",
#             "beneficiaryMrdDesignated": "0",
#             "beneficiaryPrimary": "0",
#             "beneficiarySecondContingent": "0",
#             "brokerDealerNoOption": "0",
#             "brokerDealerServicingAgentNoOption": "0",
#             "certificateNoOption": "0",
#             "coveredPersonDeceased": "0",
#             "coveredPersonJoint": "0",
#             "coveredPersonPrimary": "0",
#             "distributorNoOption": "0",
#             "eeErNoOption": "0",
#             "electronicProspectusNoOption": "0",
#             "executorNoOption": "0",
#             "grantorNoOption": "0",
#             "groupMasterNoOption": "0",
#             "iarLimitedPowerOfAttorney": "0",
#             "iarNoOption": "0",
#             "investmentAdvisorLimitedPowerOfAttorney": "0",
#             "investmentAdvisorNoOption": "0",
#             "leaNoOption": "0",
#             "listBillPayorNoOption": "0",
#             "marketTimerLimitedPowerOfAttorney": "0",
#             "marketTimerNoOption": "0",
#             "mutualFundCustodianNoOption": "0",
#             "neaRidLimitedPowerOfAttorney": "0",
#             "nrgNoOption": "0",
#             "ownerJointDifferentAddress": "0",
#             "ownerJointSameAddress": "0",
#             "ownerPrimary": "0",
#             "ownerBeneficiaryContingent": "0",
#             "ownerBeneficiaryIrrevocable": "0",
#             "ownerBeneficiaryPrimary": "0",
#             "ownerDeceasedPrimary": "0",
#             "ownerDeceasedSecondary": "0",
#             "payeeNoOption": "0",
#             "payeeSswNoOption": "0",
#             "payorNoOption": "0",
#             "powerOfAttorneyFullWithConfirm": "0",
#             "powerOfAttorneyFullWithoutConfirm": "0",
#             "powerOfAttorneyLimitedWithConfirm": "0",
#             "powerOfAttorneyLimitedWithoutConfirm": "0",
#             "powerOfAttorneyNoOption": "0",
#             "reapAdviceNoOption": "0",
#             "reapMrpLimitedPowerOfAttorney": "0",
#             "reapMrpNoOption": "0",
#             "referringAdvisorNoOption": "0",
#             "reg60NoOption": "0",
#             "secondaryAddresseeNoOption": "0",
#             "section72NoOption": "0",
#             "servicingAgentNoOption": "0",
#             "tpiaLimitedPowerOfAttorney": "0",
#             "tpiaNoOption": "0",
#             "telephonePrivilegeLimitedPowerOfAttorney": "0",
#             "telephonePrivilegeNoOption": "0",
#             "thirdPartyMarketerNoOption": "0",
#             "thirdPartyMarketerServicingNoOption": "0",
#             "trusteeNoOption": "0",
#             "umbMatchCardNoOption": "0",
#             "umbMatchNoCardNoOption": "0",
#             "eDeliveryJoint": "0",
#             "eDeliveryPrimary": "0"
#         },
#         "commission": {
#             "commissionDetails": [],
#             "total": "0.0"
#         },
#         "miscellaneous": {
#             "originalUser": "BATCH",
#             "status": "Done",
#             "oldTransactionNumber": "",
#             "batchNumber": "None",
#             "errorCode": "No Error.",
#             "systemDate": "2025-01-06",
#             "processingDate": "2025-01-06",
#             "undoDate": "1900-01-01",
#             "returnOfPremium": "Default",
#             "waiveReason": "Default",
#             "imageNumber": "",
#             "updateUser": "BATCH",
#             "relatedTransactionNumber": "",
#             "distributorTxnId": "",
#             "waiveCharges": "false",
#             "waiveBonusRecapture": "false",
#             "waiverInEffect": "false",
#             "waiveEiAdjustment": "false",
#             "waiveProductLimits": "false",
#             "abandonedDB": "false",
#             "waiveMVA": "false",
#             "waiveDeathBenefitInterest": "false",
#             "waiveFutureChargesForTxn": "false",
#             "waiveRedemptionFee": "false",
#             "keepFaceAmountConstant": "false",
#             "waiveMailCharge": "false",
#             "suppressCommission": "false",
#             "waiveFundFee": "false",
#             "suppressTaxReporting": "false",
#             "suppressCheck": "false",
#             "suppressConfirm": "false",
#             "NumOfAdvancePayments": "0",
#             "percentCompReduction": "0.0",
#             "deathReqtReceived": "1900-01-01",
#             "calcDbInterestThroughDate": "2025-01-06",
#             "advisorConsulation": "Unknown",
#             "freqForConfigSchedEvent": "Default"
#         },
#         "agent": {
#             "agentDetails": []
#         },
#         "payout": {
#             "variableRemainingIRSInvestment": "0.0",
#             "variableRemainingYTDExclusion": "0.0",
#             "fixedRemainingIRSInvestment": "0.0",
#             "fixedRemainingYTDExclusion": "N/A:"
#         },
#         "loan": {
#             "loanId": "",
#             "originalLoanId": "",
#             "repaymentMode": "",
#             "repaymentDurationYears": "",
#             "eftLoanRepaymentsFlag": "false"
#         },
#         "premiumHistory": {
#             "premiumHistoryDetails": [],
#             "copyPremiumHistoryFromContractNumber": ""
#         },
#         "AdditionalDetails": {
#             "Transaction": {
#                 "Pre-TEFRA Portion Basis": "0.0",
#                 "Pre-TEFRA Portion Gain": "0.0",
#                 "Pre-July86 Portion Basis": "0.0",
#                 "12/31/86 Account Value": "0.0",
#                 "12/31/88 Account Value": "0.0",
#                 "Post88 Contirbutions": "0.0",
#                 "Total": "0.00"
#             },
#             "Policy Summary(After Transaction)": {
#                 "Aggregate Pre-TEFRA Basis": "0.0",
#                 "Aggregate Pre-TEFRA Gain": "0.0",
#                 "Aggregate Pre-July86 Basis": "0.0",
#                 "Aggregate 12/31/86 Account Value": "0.0",
#                 "Aggregate 12/31/88 Account Value": "0.0",
#                 "Aggregate Post88 Contirbutions": "0.0",
#                 "Aggregate Total": "100000.0"
#             },
#             "Current Tax Year": "0",
#             "Current Contribution Amount": "0.0",
#             "Previous Tax Year": "0",
#             "Previous Contribution Amount": "0.0",
#             "Source Of Funds": "Cash Contribution",
#             "Contribution": "NA",
#             "Current Year Paymnet Type": "Cash Contribution",
#             "Previous Year Paymnet Type": "Cash Contribution"
#         }
#     }
# }
#     }
#     state["db_data"] = db_data
#     return state

# def fetch_db_data_node(state: GraphState) -> GraphState:
    """

    """
    try:
        # Extract contract number from OCR data
        if "extracted_data" not in state or not state["extracted_data"]:
            state["error"] = "Missing extracted data for API requests"
            return state
            
        contract_number = state["extracted_data"].get("ContractNumber")
        if not contract_number:
            state["error"] = "Contract number not found in OCR data"
            return state
            
        # Initialize dictionary to store API responses
        db_data = {}
        
        # Define base URLs and headers
        base_url = "https://qa-lcapi.se2.com/lcapigateway/integration/api"  # Replace with actual base URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic dGhha3VyMzpXZWxjb21lQDEyMzQ="  # Replace with actual auth method
        }
        
        # 1. POST request to get Policy Role information
        policy_role_url = f"{base_url}/policy/getPolicyRoles"
        # params = {
        #     contract_number
        # }
        policy_role_payload = {
            'contractNumber': contract_number,
            'companyId': "894039104"  # Example company ID
        }
        
        try:
            policy_role_response = requests.get(
                policy_role_url, 
                headers=headers, 
                params=policy_role_payload,
                timeout=30
            )
            policy_role_response.raise_for_status()
            db_data["Policy Role"] = policy_role_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Policy Role data: {str(e)}")
            # Continue with other requests even if this one fails
        
        # 2. POST request to get Transaction History
        transaction_history_url = f"{base_url}/transaction/getTransactionHistory"
        transaction_history_payload = {
            "contractNumber": contract_number,
            "companyId": "894039104",
          
        }
        
        try:
            transaction_history_response = requests.get(
                transaction_history_url, 
                headers=headers, 
                params=transaction_history_payload,
                timeout=30
            )
            transaction_history_response.raise_for_status()
              # Find the latest transaction from transaction history if available


            latest_transaction = None
            try:
                transactions = transaction_history_response.json().get("responseData", [])
                if transactions:
                    # Sort by transaction date in descending order
                    sorted_transactions = sorted(
                        transactions, 
                        key=lambda x: x.get("transactionDate", "1900-01-01"), 
                        reverse=True
                    )
                    latest_transaction = sorted_transactions[0]
                    db_data["Get Transaction History"]=latest_transaction
            except Exception as e:
                print(f"Error finding latest transaction: {str(e)}")



            # db_data["Get Transaction History"] = transaction_history_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Transaction History data: {str(e)}")
        
        # 3. GET request to get Account Info
        account_info_url = "https://qa-esbsvcs.se2.com/api/lifecadservices/policy/mass/accountinfo"
        
        params={
                   'contractnumber': contract_number
                }
        print(params)
        print("hitting api")
        try:
            account_info_response = requests.get(
                account_info_url, 
                # headers=headers,
                params=params,
                timeout=30
            )
            print("account Info Url try")
            account_info_response.raise_for_status()
            db_data["GetAccountInfo"] = account_info_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Account Info data: {str(e)}")
        
        # 4. POST request to get Account Quote
        account_quote_url = f"{base_url}/transaction/getAccountQuote"
        account_quote_payload = {
         
                "contractNumber": contract_number,
                "companyId": 894039104,
                # "companyHierarchyId": 894039104,
                # "planCode": db_data.get("GetAccountInfo", {}).get("PlanCode", "571")
            
        }
        
        try:
            account_quote_response = requests.get(
                account_quote_url, 
                headers=headers, 
                params=account_quote_payload,
                timeout=30
            )
            account_quote_response.raise_for_status()
            db_data["Get Account Quote"] = account_quote_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Account Quote data: {str(e)}")
        
        # 5. POST request to get Transaction Details
      
        
        transaction_detail_url = f"{base_url}/transaction/getTransactionDetail"
        transaction_detail_payload = {
            "contractNumber": str(contract_number),
            "companyId": "894039104",
            # "transactionNumber": latest_transaction.get("transactionNumber") if latest_transaction else None
        }
        
        try:
            
            transaction_detail_response = requests.get(
                    transaction_detail_url, 
                    headers=headers, 
                    params=transaction_detail_payload,
                    timeout=30
                )
            transaction_detail_response.raise_for_status()
            db_data["getTransactionalDetail"] = transaction_detail_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Transaction Detail data: {str(e)}")
        
        # Check if we have at least some data
        if not db_data:
            state["error"] = "Failed to retrieve any data from APIs"
            return state
            
        # Store the fetched data in the state
        state["db_data"] = db_data
        return state
        
    except Exception as e:
        state["error"] = f"Error in fetch_db_data_node: {str(e)}"
        return state



# ---------------------------
# New Node: Embed Data
# ---------------------------
def embed_data_node(state: GraphState) -> GraphState:
    """
    Node to ingest OCR and DB data into their separate vector stores using the RAG service.
    It converts the OCR and DB data into text separately and calls the ingestion methods.
    Afterwards, it loads the remaining rules into the state.
    """
    if "extracted_data" not in state or "db_data" not in state:
        state["error"] = "Missing extracted_data or db_data for embedding"
        return state
    try:
        # Convert OCR and DB data to text separately.
        ocr_text = json.dumps(state["extracted_data"], indent=2)
        db_text = json.dumps(state["db_data"], indent=2)
        print("1")
        print("2")
        
        # Ingest OCR data into the OCR vector store.
        success_ocr = state["rag_service"].ingest_ocr_text(ocr_text)
        
        # Ingest DB data into the DB vector store.
        success_db = state["rag_service"].ingest_db_text(db_text)

        print("3")
        print("4")
        
        if not success_ocr or not success_db:
            state["error"] = "Error embedding OCR or DB data"
            return state
        
        # Load the rules into state.
        state["remaining_rules"] = load_rules()
        state["remaining_retrieval_rules"] = load_retrieval_rules()
        state["rule_results"] = []
        return state
    except Exception as e:
        state["error"] = f"Exception in embed_data_node: {str(e)}"
        return state

# ---------------------------
# New Node: Rule Validation Loop
# ---------------------------
def validate_rule_node(state: GraphState) -> GraphState:
    """
    Node that processes a single rule from the remaining_rules.
    Retrieves context from two vector databases (OCR and DB) using the rule's description,
    then calls the LLM with a prompt that includes both retrieval outputs.
    """
    # If no rules remain, mark overall decision as IGO.
    if "remaining_rules" not in state or len(state["remaining_rules"]) == 0:
        state["overall_decision"] = "IGO"
        return state

    # Pop the next rule to validate.
    current_rule = state["remaining_rules"].pop(0)
    current_retrieval_rule = state["remaining_retrieval_rules"].pop(0)
    state["current_rule"] = current_rule
    state["current_retrieval_rule"] = current_retrieval_rule

    # Retrieve relevant data from the separate vector databases using the rule's description.
    try:
        # Retrieve OCR data using the dedicated FAISS index for OCR data.
        relevant_ocr_data = state["rag_service"].retrieve_ocr(current_retrieval_rule["question"], k=5)
        # Retrieve DB data using the dedicated FAISS index for DB data.
        relevant_db_data = state["rag_service"].retrieve_db(current_retrieval_rule["question"], k=5)
        print("5")
    except Exception as e:
        state["error"] = f"Error during vector retrieval: {str(e)}"
        return state

    # Construct a prompt that combines the rule with both retrieval outputs.
    prompt_template = """
You are a rule validating agent which determines if a user policy should be renewed or not.
User submits a form whose data you will receive which is labelled as 'OCR Data' and you will receive already existing data for that policy which is labelled as 'DB Data'.
You have to validate rules against OCR data (new data from user) and DB data (existing user and policy data).

Rule: {rule_description}

OCR Data:
{ocr_data}

DB Data:
{db_data}

Instruction: Based on the above information, does the combined data satisfy the rule?
- If the data satisfies the rule, reply with "OK".
- Otherwise, reply with "NIGO", including the NIGO id ({nigo_id}) and a brief explanation of why the rule failed.

Return your response strictly as JSON in one of these formats:
{{ "decision": "OK" }}
or
{{ "decision": "NIGO", "nigo_id": "{nigo_id}", "reason": "Explanation of why the rule failed" }}
"""
    print("5.1")
    
    # Format the prompt with simpler data representation to avoid potential JSON formatting issues
    try:
        # Convert the retrieved data to a more readable format
        ocr_data_str = json.dumps(relevant_ocr_data, indent=2, ensure_ascii=False)
        db_data_str = json.dumps(relevant_db_data, indent=2, ensure_ascii=False)
        
        formatted_prompt = prompt_template.format(
            rule_description=current_rule["description"],
            ocr_data=ocr_data_str,
            db_data=db_data_str,
            nigo_id=current_rule["nigo_id"]
        )
        print("5.2 - Prompt formatted successfully")
    except Exception as e:
        state["error"] = f"Error formatting prompt: {str(e)}"
        return state
    
    print("6")
    try:
        print("7")
        # Use the LLM with temperature set to 0.1 for more deterministic responses
        llm = state["llm"]
        
        # If the LLM has a temperature parameter, try to set it
        if hasattr(llm, "temperature"):
            original_temp = llm.temperature
            llm.temperature = 0.1
            print("7.1 - Set temperature to 0.1")
            print("original temperature is " ,original_temp)
        
        # Invoke the LLM with the formatted prompt
        response = llm.invoke(formatted_prompt)
        print("8")
        
        # Reset temperature if we changed it
        if hasattr(llm, "temperature") and original_temp is not None:
            llm.temperature = original_temp
        
        # Parse the LLM's JSON response
        try:
            if hasattr(response, 'content'):
                # For newer LLM interfaces that return a message object
                response_text = response.content
                state["validation_response"] = response_text
                # Clean the response text to ensure it's valid JSON
                cleaned_response = response_text.strip()
                # Remove any markdown code block markers if present
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                decision_result = json.loads(cleaned_response)
            else:
                # For older LLM interfaces that return a string
                response_text = str(response)
                state["validation_response"] = response_text
                # Clean the response text
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                decision_result = json.loads(cleaned_response)
            
            print("8.1 - Successfully parsed JSON response")
        except json.JSONDecodeError as e:
            # If JSON parsing fails, create a fallback response
            print(f"8.2 - JSON parsing error: {e}")
            print(f"Response was: {response_text}")
            
            # Try to extract decision from text
            if "NIGO" in response_text:
                decision_result = {
                    "decision": "NIGO",
                    "nigo_id": current_rule["nigo_id"],
                    "reason": "Failed to parse exact reason, but rule validation failed."
                }
            else:
                decision_result = {"decision": "OK"}
            
            state["validation_response"] = json.dumps(decision_result)
        
        state.setdefault("rule_results", []).append(decision_result)
        print("9")
        
        # If a NIGO decision is returned, update state accordingly and stop further validation.
        if decision_result.get("decision", "").upper() == "NIGO":
            state["overall_decision"] = "NIGO"
            state["failed_rule"] = current_rule
            state["nigo_details"] = decision_result
            state["continue_validation"] = False
        else:
            state["continue_validation"] = True
        return state
    except Exception as e:
        state["error"] = f"Error in validate_rule_node: {str(e)}"
        return state

# ---------------------------
# New Node: Final Decision
# ---------------------------

# ---------------------------
# Original Nodes (Tool Selector, OCR, LLM Response, etc.)
# ---------------------------
class WorkflowService:
    """
    Service for orchestrating workflows using LangGraph.
    This updated version includes new nodes for DB fetching, embedding, and rule validation.
    """
    def __init__(self, llm, rag_service, ocr_service):

        self.llm = llm
        self.rag_service = rag_service
        self.ocr_service = ocr_service
        self.workflow = self._create_workflow()
        # Dictionary to store conversation memories keyed by conversation ID
        self.conversations = {}

    def final_decision_node(self,state: GraphState) -> GraphState:
        """
        Node to produce the final output.
        If overall_decision is NIGO, set final_response with NIGO details.
        Otherwise, mark the form as IGO.
        """
        user_input = state["user_input"]
        conversation_id = state.get("conversation_id")
        memory = self.get_or_create_memory(conversation_id)
        # If no form validation is required, simply generate a response based on conversation history.

        memory_vars = memory.load_memory_variables({})
        history = memory_vars.get("history", "")
        if hasattr(history, "__iter__") and not isinstance(history, str):
            history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in history])
        else:
            history_str = str(history)

        if state.get("overall_decision") == "NIGO":
            promt_template= """
                         Give the provided llm_Response to the humanize way such that you are chating with someone. Keep the chat small and concise.
                        . State the NIGO id or IGO id also If present
                        {validation_response}

                        Here is the conversation so far
                        {history}
            """
            response =state["llm"].invoke(promt_template.format(validation_response=state["validation_response"],history=history))
            content = response.content if hasattr(response, 'content') else str(response)
            memory.save_context({"input": user_input}, {"output": content})
            # memory.save_context({"input": user_input}, {"output": content})
            state["final_response"] = content
        else:
            promt_template= """ We got the IGO response for the provided Data. All the rules validates and renewals for the form uploaded is succed.
                        You have to give response that such that you are an agent and tell the client that renewals is succed. Used the below data for getting the client name
                        {extracted_data}
                        Your Name is MASS.AI
                        Use Emojis also

                        Here is the conversation so far
                        {history}
            """
            response =state["llm"].invoke(promt_template.format(extracted_data=state["extracted_data"],history=history))
            content = response.content if hasattr(response, 'content') else str(response)
            memory.save_context({"input": user_input}, {"output": content})
            state["final_response"] = content
        return state


    def _tool_selector(self, state: GraphState) -> GraphState:
        if "error" in state:
            return state
        if not state.get("use_decision_engine", False):
            return state
        user_input = state["user_input"]
        prompt = ChatPromptTemplate.from_template("""
        You are an assistant that helps decide whether a user query requires form validation.
        User query: {user_input}
        Does this query appear to be asking about validating or processing a form, document, 
        or extracting data from a file? Answer with 'yes' or 'no'.
        """)
        try:
            response = self.llm.invoke(prompt.format_messages(user_input=user_input))
            content = response.content if hasattr(response, 'content') else str(response)
            rule_validation_needed = "yes" in content.lower()
            form_type = "generic"
            if "renewal" in user_input.lower():
                form_type = "renewals"
            elif "withdrawal" in user_input.lower():
                form_type = "withdrawals"
            return {**state, "rule_validation_needed": rule_validation_needed, "form_type": form_type}
        except Exception as e:
            return {**state, "error": f"Error in tool selector: {str(e)}"}

    def _rule_validation_entry(self, state: GraphState) -> GraphState:
        """
        This node is kept for backward compatibility.
        It extracts file path information (if any) from the user input.
        """
        if "error" in state:
            return state
        user_input = state["user_input"]
        file_path_match = re.search(r'file[:\s]+([^\s,\.]+)', user_input)
        file_path = file_path_match.group(1) if file_path_match else "test_form.pdf"
        return {**state, "file_path": file_path}

    def _ocr_node(self, state: GraphState) -> GraphState:
    # If 'extracted_data' exists and is not None, simply return the state.
        if state.get("extracted_data") is not None:
            return state
       
        # Otherwise, define the hard-coded extracted data.
        extracted_data_test = {
            "ContractNumber": 571003597,
            "EmailAddress": "meandme@gmail.com",
            "GuaranteePeriod": "3 year",
            "OwnerName": "sarams sarn",
            "OwnerSignatureDate": "26/3/25",
            "PhoneNumber": "1-866-645-2362"
        }
       
        # Return the new state with the extracted data added.
        return {**state, "extracted_data": extracted_data_test}
        if "error" in state:
            return state
        file_path = state.get("file_path", "test_form.pdf")
        form_type = state.get("form_type", "generic")
        try:
            if file_path == "test_form.pdf":
                extracted_data = self.ocr_service.extract_test_data(form_type)
            else:
                extracted_data = self.ocr_service.extract_form_data(file_path)
            if "error" in extracted_data:
                return {**state, "error": extracted_data["error"]}
            return {**state, "extracted_data": extracted_data}
        except Exception as e:
            return {**state, "error": f"Error in OCR processing: {str(e)}"}

    def _llm_response(self, state: GraphState) -> GraphState:
        if "error" in state:
            return {**state, "final_response": f"I encountered an error: {state['error']}"}
        user_input = state["user_input"]
        conversation_id = state.get("conversation_id")
        memory = self.get_or_create_memory(conversation_id)
        # If no form validation is required, simply generate a response based on conversation history.
        try:
            memory_vars = memory.load_memory_variables({})
            history = memory_vars.get("history", "")
            if hasattr(history, "__iter__") and not isinstance(history, str):
                history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in history])
            else:
                history_str = str(history)
            prompt = ChatPromptTemplate.from_template("""
            You are a helpful AI assistant.
            This is the conversation so far:
            {history}
            User: {input}
            Assistant:
            """)
            response = self.llm.invoke(prompt.format_messages(history=history, input=user_input))
            content = response.content if hasattr(response, 'content') else str(response)
            memory.save_context({"input": user_input}, {"output": content})
            return {**state, "final_response": content}
        except Exception as inner_e:
            return {**state, "final_response": f"I couldn't process your request: {str(inner_e)}"}

    def get_or_create_memory(self, conversation_id):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationBufferMemory(
                memory_key="history",
                return_messages=True,
                ai_prefix="Assistant",
                human_prefix="Human"
            )
            print(f"Created new memory for conversation {conversation_id}")
        return self.conversations[conversation_id]

    def _router(self, state: GraphState) -> str:
        # If rule validation is not needed, go directly to llm_response.
        if "error" in state:
            return "llm_response"
        if state.get("rule_validation_needed", False):
            # For form validation, start with OCR extraction.
            return "ocr_node"
        else:
            return "llm_response"

    # New routing for the validation branch
    def _post_ocr_router(self, state: GraphState) -> str:
        # After OCR, proceed to DB fetch.
        if "error" in state:
            return "llm_response"
        return "db_fetch"

    def _post_db_router(self, state: GraphState) -> str:
        # After fetching DB data, proceed to embedding.
        if "error" in state:
            return "llm_response"
        return "embed_data"

    def _post_embed_router(self, state: GraphState) -> str:
        # After embedding, go to rule validation loop.
        if "error" in state:
            return "llm_response"
        return "validate_rule"

    def _validation_router(self, state: GraphState) -> str:
        # If validation should continue and there are remaining rules, loop;
        # Otherwise, proceed to final decision.
        if "error" in state:
            return "llm_response"
        if state.get("continue_validation", False) and state.get("remaining_rules"):
            return "validate_rule"
        else:
            return "final_decision"

    def _create_workflow(self):
        workflow = StateGraph(GraphState)
        # Add nodes for the normal branch
        workflow.add_node("tool_selector", self._tool_selector)
        workflow.add_node("llm_response", self._llm_response)
        # Add nodes for the validation branch
        workflow.add_node("rule_validation_entry", self._rule_validation_entry)  # Retained for file extraction if needed.
        workflow.add_node("ocr_node", self._ocr_node)
        workflow.add_node("db_fetch", fetch_db_data_node)
        workflow.add_node("embed_data", embed_data_node)
        workflow.add_node("validate_rule", validate_rule_node)
        workflow.add_node("final_decision", self.final_decision_node)

        # Conditional edges from tool_selector:
        workflow.add_conditional_edges(
            "tool_selector",
            self._router,
            {
                "ocr_node": "ocr_node",
                "llm_response": "llm_response"
            }
        )
        # From rule_validation_entry (if used) to ocr_node
        workflow.add_edge("rule_validation_entry", "ocr_node")
        # From ocr_node to db_fetch:
        workflow.add_edge("ocr_node", "db_fetch")
        # From db_fetch to embed_data:
        workflow.add_edge("db_fetch", "embed_data")
        # From embed_data to validate_rule:
        workflow.add_edge("embed_data", "validate_rule")
        # Conditional edge from validate_rule: loop if continue_validation is True and rules remain, else go to final_decision.
        workflow.add_conditional_edges(
            "validate_rule",
            self._validation_router,
            {
                "validate_rule": "validate_rule",
                "final_decision": "final_decision"
            }
        )
        # Set entry point as tool_selector.
        workflow.set_entry_point("tool_selector")
        return workflow.compile()

    def process_message(self, user_input, use_decision_engine=False, conversation_id=None,ocr_data=None):
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        print(ocr_data)
        initial_state = {
            "user_input": user_input,
            "use_decision_engine": use_decision_engine,
            "conversation_id": conversation_id,
            # Optionally, include form identifier if available:
            "extracted_data":ocr_data,
            "form_identifier": "sample_form_id",
            "rag_service": self.rag_service,
            "llm":self.llm
        }
        print(initial_state)
        try:
            result = self.workflow.invoke(initial_state)
            return {
                "input": user_input,
                "output": result.get("final_response", "Sorry, I couldn't process your request."),
                "conversation_id": conversation_id,
                "type": "text"
            }
        except Exception as e:
            print(f"Error in workflow: {e}")
            return {
                "input": user_input,
                "output": f"I encountered an error: {str(e)}",
                "conversation_id": conversation_id,
                "type": "error",
                "error": str(e)
            }
