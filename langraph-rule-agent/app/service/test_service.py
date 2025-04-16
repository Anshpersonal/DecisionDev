from app.service.rag_service import RAGService
import json

def fetch_db_data_node() :
    db_data = {
        "Policy Role":
{
            "clientRoleDetails": {
                "prEligibleBeneInhIra": "null",
                "roleId": -2,
                "roleIdDesc": "Beneficiary",
                "roleOptionId": 0,
                "roleOptionIdDesc": "Primary",
                "roleCountId": 3,
                "rolePercent": 100.0,
                "roleStatus": "C",
                "roleStatusDesc": "Active",
                "roleEffDate": "2018-01-04",
                "roleEndDate": "2999-12-31",
                "taxToNameId": -999,
                "taxToOptionId": -999,
                "taxToRoleId": -999,
                "relationshipId": -999,
                "relationshipDesc": "N/A",
                "cftgIndicatorInd": "null",
                "cftgIndicatorValue": -999,
                "cftgPayoutOptionValue": "null",
                "cftgPayoutOptionDesc": "null",
                "prevContactDate": "2999-12-31",
                "lastContactDate": "null",
                "nameId": 1808553805,
                "addressSeasonal": 0,
                "addressId": 8713223,
                "phoneId": -999
            },
            "clientDetail": {
                "client": {
                    "nmFirstDate": "2017-12-27",
                    "clientType": "IN",
                    "clientTypeDesc": "Individual",
                    "nameId": 1808553805,
                    "companyClientId": "null",
                    "fullName": "sarn sarams",
                    "taxId": "878445444",
                    "taxIdLast4": "5444",
                    "imoIndicator": "false",
                    "taxIdVerifiedInd": "null",
                    "externalId": "null",
                    "emailId": "null",
                    "companyCode": "null",
                    "companyName": "null",
                    "companyAbbrName": "null",
                    "companyCarrierCode": "null",
                    "trustTypeId": -999,
                    "trustTypeDesc": "None",
                    "salute": "null",
                    "firstName": "sarn",
                    "middleName": "null",
                    "lastName": "sarams",
                    "maidName": "null",
                    "nameSuffix": "null",
                    "sex": "M",
                    "sexDesc": "Male",
                    "marriedStatus": -999,
                    "marriedStatusDesc": "Default",
                    "dob": "1960-01-01",
                    "birthCity": "null",
                    "birthStateCode": "$$",
                    "birthStateDesc": "Default",
                    "height": "null",
                    "weight": 0,
                    "smokerInd": "null",
                    "occupation": "null",
                    "employer": "null",
                    "salary": 0,
                    "jobLocation": "null",
                    "jobStateCode": "$$",
                    "deathDate": "null",
                    "deathNotificationDate": "2999-12-31",
                    "dateOfDueProof": "2999-12-31",
                    "w8Receiptdate": "2999-12-31",
                    "w8StatusInd": "N",
                    "intlAnnuityInd": "null",
                    "file": "null",
                    "validTaxIdInd": "null"
                },
                "addresses": [
                    {
                        "addressId": 8713223,
                        "addressType": "$$",
                        "addressTypeDesc": "Default",
                        "addressLine1": "dfgdf",
                        "addressLine2": "null",
                        "addressLine3": "null",
                        "city": "topeka",
                        "stateCode": "KS",
                        "stateCodeDesc": "KANSAS",
                        "zipCode": "66615",
                        "zipSuffix": "null",
                        "countryCode": "USA",
                        "countryDesc": "United States",
                        "countryShortDesc": "USA",
                        "mailZone": "null",
                        "zipWalkRoute": "null",
                        "effStartDate": "2018-01-04",
                        "effEndDate": "2999-12-31",
                        "seasonalAddressInd": "null",
                        "seasonalAddressIndDesc": "null",
                        "roleAddress": "true"
                    }
                ],
                "phones": [
                    {
                        "addressId": 8713223,
                        "phoneId": -999,
                        "phoneType": "$$",
                        "phoneTypeDesc": "Default",
                        "phoneNumber": "null",
                        "phoneAreaCode": "null",
                        "phoneExc": "null",
                        "phoneExt": "null",
                        "phoneSuffix": "null",
                        "phoneCountryCode": "$$",
                        "phoneCountryDesc": "Non Specified",
                        "phoneCountryShortDesc": "$$",
                        "phoneDayNight": "$$",
                        "phoneDayNightDesc": "Any",
                        "phoneStartDate": "null",
                        "phoneEndDate": "null",
                        "rolePhone": "true"
                    }
                ],
                "addressCascadeInd": "false",
                "gbOptions": "null",
                "addNewAddressPhoneInd": "false",
                "addressCascadeList": "null"
            },
            "bankDetails": [],
            "withholdingDetail": {
                "federalDollar": 0.0,
                "federalPercentage": 0.0,
                "federalTaxRatesToUseCode": 0,
                "federalTaxRatesToUseDesc": "Default",
                "federalExemption": 0,
                "federalFilingStatusCode": -999,
                "federalFilingStatusDesc": "Default",
                "stateDollar": 0.0,
                "statePercentage": 0.0,
                "stateTaxRatesToUseCode": 0,
                "stateTaxRatesToUseDesc": "Default",
                "stateExemption": 0,
                "stateFilingStatusCode": -999,
                "stateFilingStatusDesc": "Default",
                "backupDollar": 0.0,
                "backupPercentage": 0.0
            }
        },

"Get Transaction History":
{
    "apiRequestHeader": {
        "externalId": "null",
        "externalUserId": "null",
        "externalSystemId": "null",
        "externalUserCompHrchyId": "null",
        "muleCorrelationId": "null",
        "correlationId": "null",
        "timestamp": "null",
        "apiRequestUUID": "bf507a4d-56cc-40c1-a3b0-92feb90c7573",
        "apiName": "GetTransactionHistory",
        "externalTransactionName": "null",
        "clientCode": "null",
        "externalUserIDValid": "false"
    },
    "requestParam": {
        "itlanndate": "2999-12-31",
        "companyid": "894039104",
        "transType": "all",
        "todate": "2999-12-31",
        "top": "all",
        "transstatus": "%",
        "contractnumber": "571003597",
        "inlineCount": "all",
        "skip": "0",
        "companyhierarchyid": "894039104",
        "queryId": "getTransactionHistory",
        "fromdate": "1900-01-01"
    },
    "status": {
        "statusCode": "Success",
        "statusMessage": "Request processed successfully",
        "errors": [],
        "policyDetails": "null"
    },
    "responseData": [
        {
            "transactionNumber": 39150090,
            "transactionType": 25,
            "transactionTypeCode": "HK",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2025-01-04",
            "transactionProcessDate": "2025-01-06",
            "transactionLastDate": "2025-01-06",
            "transactionTaxYear": "2025",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 116868.15,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2025,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 39673159,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 16,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 39150094,
            "transactionType": 60,
            "transactionTypeCode": "G6",
            "transactionTypeDesc": "Rate Renewal",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2025-01-04",
            "transactionProcessDate": "2025-01-06",
            "transactionLastDate": "2025-01-06",
            "transactionTaxYear": "2025",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 116868.15,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2025,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 39673163,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 10,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 34907578,
            "transactionType": 25,
            "transactionTypeCode": "HK",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2024-01-04",
            "transactionProcessDate": "2024-01-04",
            "transactionLastDate": "2024-01-04",
            "transactionTaxYear": "2024",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 114289.51,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2024,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 35398628,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 16,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 30642973,
            "transactionType": 25,
            "transactionTypeCode": "HK",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2023-01-04",
            "transactionProcessDate": "2023-01-04",
            "transactionLastDate": "2023-01-04",
            "transactionTaxYear": "2023",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 111774.58,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2023,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 31103128,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 16,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 27390007,
            "transactionType": 25,
            "transactionTypeCode": "HK",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2022-01-04",
            "transactionProcessDate": "2022-01-04",
            "transactionLastDate": "2022-01-04",
            "transactionTaxYear": "2022",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 109314.99,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2022,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 27818470,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 16,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 23301559,
            "transactionType": 25,
            "transactionTypeCode": "HK",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2021-01-04",
            "transactionProcessDate": "2021-01-04",
            "transactionLastDate": "2021-01-04",
            "transactionTaxYear": "2021",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 106909.53,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2021,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 23721447,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 16,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 20817631,
            "transactionType": 25,
            "transactionTypeCode": "HK",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2020-01-04",
            "transactionProcessDate": "2020-01-06",
            "transactionLastDate": "2020-01-06",
            "transactionTaxYear": "2020",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 104550.62,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2020,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 21218093,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 16,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 17177017,
            "transactionType": 25,
            "transactionTypeCode": "HK",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2019-01-04",
            "transactionProcessDate": "2019-01-04",
            "transactionLastDate": "2019-01-04",
            "transactionTaxYear": "2019",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 102250.0,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2019,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 17491068,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 16,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 13345649,
            "transactionType": 133,
            "transactionTypeCode": "J8",
            "transactionTypeDesc": "Feature Change",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2018-01-04",
            "transactionProcessDate": "2018-01-04",
            "transactionLastDate": "2018-01-04",
            "transactionTaxYear": "2018",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 100000.0,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2018,
            "charge": 0.0,
            "restrictCharge": 3,
            "disbNumber": 13599661,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 27,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 13345651,
            "transactionType": 4,
            "transactionTypeCode": "A8",
            "transactionTypeDesc": "Issue",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2018-01-04",
            "transactionProcessDate": "2018-01-04",
            "transactionLastDate": "2018-01-04",
            "transactionTaxYear": "2018",
            "transactionAmount": 0.0,
            "amountType": 0,
            "amountTypeDesc": "Auto",
            "grossAmount": 0.0,
            "investedValueAmount": 100000.0,
            "tlRefund": 0.0,
            "netAmount": 0.0,
            "isContribution": 0.0,
            "transactionYear": 2018,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 13599664,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 0,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 4,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        },
        {
            "transactionNumber": 13345650,
            "transactionType": 1,
            "transactionTypeCode": "A2",
            "transactionTypeDesc": "Initial Premium",
            "transactionStatus": "D",
            "transactionStatusDesc": "Done",
            "transactionDate": "2018-01-04",
            "transactionProcessDate": "2018-01-04",
            "transactionLastDate": "2018-01-04",
            "transactionTaxYear": "2018",
            "transactionAmount": 100000.0,
            "amountType": 2,
            "amountTypeDesc": "Percentage",
            "grossAmount": 100000.0,
            "investedValueAmount": 100000.0,
            "tlRefund": 0.0,
            "netAmount": 100000.0,
            "isContribution": 1.0,
            "transactionYear": 2018,
            "charge": 0.0,
            "restrictCharge": 0,
            "disbNumber": 13599663,
            "policyMaturityDate": "2050-01-01",
            "listBillDate": "null",
            "suspenceNumber": 369166,
            "payoutFlag": "N",
            "netOrGrossFlag": "null",
            "loanId": -999,
            "archiveFlag": 0,
            "enhBenLostInd": 0,
            "taxAggregationCounter": 0,
            "transactionProcessOrder": 2,
            "dtId": "null",
            "errorStatus": 0,
            "oldTransactionId": -999
        }
    ],
    "inlineCount": 11
},

"GetAccountInfo":
{
    "SourceSystem": "LC",
    "ContractNumber": "571003597",
    "ContractId": "269430",
    "CovId": "0",
    "OwnerName": "sarams, sarn",
    "QualTypeCode": "Non-Qualified",
    "QualTypeDesc": "Non-Qualified",
    "APPLICATIONDATE": "2018-01-04T00:00:00",
    "ProductLine": "ANNUITY",
    "ModifiedEndowmentStatus": "0",
    "MaturityDate": "2050-01-01T00:00:00",
    "ProductCategory": "FIXED",
    "ProductName": "Stable Voyage",
    "IssueState": "KS",
    "IssueDate": "2018-01-04T00:00:00",
    "IssueAge": "58",
    "ContractStatus": "ACTIVE",
    "PlanCode": "571",
    "ModelName": "null",
    "eDeliveryStatus": "null",
    "OnlineTransactionAuthorized": 0,
    "OnlineTransactionAuthCode": 0,
    "DeathBenefit": "Standard Death Benefit",
    "SurrenderChargePeriod": "null",
    "MVAProduct": "N",
    "ProductShareClass": "null",
    "ProductCompanyId": 39,
    "WithdrawalChargePeriod": "null",
    "SrcQualTypeCode": "1",
    "SrcProductLine": "null",
    "SrcProductCategory": "null",
    "SrcProductName": "MassMutual Stable Voyage",
    "SrcIssueState": "KS",
    "SrcContractStatus": "A",
    "SrcProductCompanyId": "571",
    "JurisdictionStateCode": "KS",
    "LastAnniversaryDate": "2025-01-04T00:00:00",
    "NextAnniversaryDate": "2026-01-04T00:00:00",
    "LastTransactionDate": "2025-01-04T00:00:00",
    "LTCIndicator": 0,
    "ActualOwnerName": "sarams, sarn",
    "AnnuitantName": "sarams, sarn",
    "OverrideOwnerName": "false"
},

"Get Account Quote":
{
    "apiRequestHeader": {
        "externalId": "null",
        "externalUserId":  "null",
        "externalSystemId":  "null",
        "externalUserCompHrchyId":  "null",
        "muleCorrelationId":  "null",
        "correlationId":  "null",
        "timestamp":  "null",
        "apiRequestUUID": "b1cbe04c-8e32-47d2-9b8c-8925930fd801",
        "apiName": "GetAccountQuote",
        "externalTransactionName":  "null",
        "clientCode":  "null",
        "externalUserIDValid":  "null"
    },
    "policyCommonRequest": {
        "contractNumber": "571003597",
        "companyId": 903908434,
        "companyHierarchyId": 894039104,
        "planCode": "571",
        "policyNumber": 269430,
        "cvgId": 0
    },
    "status": {
        "statusCode": "Success",
        "statusMessage": "Request processed successfully",
        "errors": [],
        "policyDetails": "null"
    },
    "valuationDate": "2025-04-11",
    "accountQuoteSummary": {
        "accountQuoteValues": [
            {
                "contribution": "NA",
                "subContribution": "NA",
                "division": "3 Yr Guarantee",
                "chAccount": "PJ",
                "chDivision": "01",
                "units": 0.0,
                "value": 0.0,
                "balance": 117789.81,
                "percentage": 100.0,
                "fundName": "3 Year Guarantee"
            }
        ],
        "totalUnits": 0.0,
        "totalBalance": 117789.81,
        "totalPercentage": 100.0
    }
},

"getTransactionalDetail":
{
    "status": {
        "statusCode": "Success",
        "statusMessage": "Request processed successfully",
        "errors": []
    },
    "transactionDetails": {
        "result": {
            "resultDetails": [],
            "total": "0.0"
        },
        "request": {
            "transactionType": "25",
            "transactionTypeDesc": "Contract Anniversary",
            "transactionDate": "2025-01-04",
            "transactionOption": "0",
            "total": "0.00",
            "productPlanType": "Deferred Annuity",
            "contribution": "NA",
            "indicator": "None",
            "grossDisbursement": "false",
            "requestDetails": [],
            "dollarTotal": "0.0",
            "percentTotal": "0.0"
        },
        "accountValue": {
            "accountValueDetails": [
                {
                    "contribution": "NA",
                    "subContribution": "NA",
                    "chAccount": "PJ",
                    "chDivision": "01",
                    "division": "3 Year Guarantee",
                    "units": "0.0",
                    "unitValue": "0.0",
                    "amount": "116868.15"
                }
            ],
            "total": "116868.15"
        },
        "fees": {
            "charges": {
                "chargesDetail": [],
                "total": "0.0"
            },
            "expenses": {
                "expensesDetail": [],
                "total": "0.0"
            },
            "waivedCharges": {
                "waivedChargesDetail": [],
                "total": "0.0"
            },
            "featureFee": {
                "featureFeeDetail": [],
                "total": "0.0"
            }
        },
        "disburse": {
            "disburseDetails": [],
            "applyToSuspense": "0",
            "transactionLevelWithholding": {},
            "multipleChecks": "0",
            "replacement": "0"
        },
        "confirm": {
            "additionalSoaRecipientNoOption": "0",
            "advisorFeePayeeLimitedPowerOfAttorney": "0",
            "advisorFeePayeeNoOption": "0",
            "agentAgentOfRecord": "0",
            "agentNonCommissionAgent": "0",
            "annuitantInsuredContingent": "0",
            "annuitantInsuredJoint": "0",
            "annuitantInsuredPrimary": "0",
            "annuitantBenefContingent": "0",
            "annuitantBenefIrrevocable": "0",
            "annuitantBenefPrimary": "0",
            "assigneeNoOption": "0",
            "beneficiaryContingent": "0",
            "beneficiaryIrrevocable": "0",
            "beneficiaryMrdDesignated": "0",
            "beneficiaryPrimary": "0",
            "beneficiarySecondContingent": "0",
            "brokerDealerNoOption": "0",
            "brokerDealerServicingAgentNoOption": "0",
            "certificateNoOption": "0",
            "coveredPersonDeceased": "0",
            "coveredPersonJoint": "0",
            "coveredPersonPrimary": "0",
            "distributorNoOption": "0",
            "eeErNoOption": "0",
            "electronicProspectusNoOption": "0",
            "executorNoOption": "0",
            "grantorNoOption": "0",
            "groupMasterNoOption": "0",
            "iarLimitedPowerOfAttorney": "0",
            "iarNoOption": "0",
            "investmentAdvisorLimitedPowerOfAttorney": "0",
            "investmentAdvisorNoOption": "0",
            "leaNoOption": "0",
            "listBillPayorNoOption": "0",
            "marketTimerLimitedPowerOfAttorney": "0",
            "marketTimerNoOption": "0",
            "mutualFundCustodianNoOption": "0",
            "neaRidLimitedPowerOfAttorney": "0",
            "nrgNoOption": "0",
            "ownerJointDifferentAddress": "0",
            "ownerJointSameAddress": "0",
            "ownerPrimary": "0",
            "ownerBeneficiaryContingent": "0",
            "ownerBeneficiaryIrrevocable": "0",
            "ownerBeneficiaryPrimary": "0",
            "ownerDeceasedPrimary": "0",
            "ownerDeceasedSecondary": "0",
            "payeeNoOption": "0",
            "payeeSswNoOption": "0",
            "payorNoOption": "0",
            "powerOfAttorneyFullWithConfirm": "0",
            "powerOfAttorneyFullWithoutConfirm": "0",
            "powerOfAttorneyLimitedWithConfirm": "0",
            "powerOfAttorneyLimitedWithoutConfirm": "0",
            "powerOfAttorneyNoOption": "0",
            "reapAdviceNoOption": "0",
            "reapMrpLimitedPowerOfAttorney": "0",
            "reapMrpNoOption": "0",
            "referringAdvisorNoOption": "0",
            "reg60NoOption": "0",
            "secondaryAddresseeNoOption": "0",
            "section72NoOption": "0",
            "servicingAgentNoOption": "0",
            "tpiaLimitedPowerOfAttorney": "0",
            "tpiaNoOption": "0",
            "telephonePrivilegeLimitedPowerOfAttorney": "0",
            "telephonePrivilegeNoOption": "0",
            "thirdPartyMarketerNoOption": "0",
            "thirdPartyMarketerServicingNoOption": "0",
            "trusteeNoOption": "0",
            "umbMatchCardNoOption": "0",
            "umbMatchNoCardNoOption": "0",
            "eDeliveryJoint": "0",
            "eDeliveryPrimary": "0"
        },
        "commission": {
            "commissionDetails": [],
            "total": "0.0"
        },
        "miscellaneous": {
            "originalUser": "BATCH",
            "status": "Done",
            "oldTransactionNumber": "",
            "batchNumber": "None",
            "errorCode": "No Error.",
            "systemDate": "2025-01-06",
            "processingDate": "2025-01-06",
            "undoDate": "1900-01-01",
            "returnOfPremium": "Default",
            "waiveReason": "Default",
            "imageNumber": "",
            "updateUser": "BATCH",
            "relatedTransactionNumber": "",
            "distributorTxnId": "",
            "waiveCharges": "false",
            "waiveBonusRecapture": "false",
            "waiverInEffect": "false",
            "waiveEiAdjustment": "false",
            "waiveProductLimits": "false",
            "abandonedDB": "false",
            "waiveMVA": "false",
            "waiveDeathBenefitInterest": "false",
            "waiveFutureChargesForTxn": "false",
            "waiveRedemptionFee": "false",
            "keepFaceAmountConstant": "false",
            "waiveMailCharge": "false",
            "suppressCommission": "false",
            "waiveFundFee": "false",
            "suppressTaxReporting": "false",
            "suppressCheck": "false",
            "suppressConfirm": "false",
            "NumOfAdvancePayments": "0",
            "percentCompReduction": "0.0",
            "deathReqtReceived": "1900-01-01",
            "calcDbInterestThroughDate": "2025-01-06",
            "advisorConsulation": "Unknown",
            "freqForConfigSchedEvent": "Default"
        },
        "agent": {
            "agentDetails": []
        },
        "payout": {
            "variableRemainingIRSInvestment": "0.0",
            "variableRemainingYTDExclusion": "0.0",
            "fixedRemainingIRSInvestment": "0.0",
            "fixedRemainingYTDExclusion": "N/A:"
        },
        "loan": {
            "loanId": "",
            "originalLoanId": "",
            "repaymentMode": "",
            "repaymentDurationYears": "",
            "eftLoanRepaymentsFlag": "false"
        },
        "premiumHistory": {
            "premiumHistoryDetails": [],
            "copyPremiumHistoryFromContractNumber": ""
        },
        "AdditionalDetails": {
            "Transaction": {
                "Pre-TEFRA Portion Basis": "0.0",
                "Pre-TEFRA Portion Gain": "0.0",
                "Pre-July86 Portion Basis": "0.0",
                "12/31/86 Account Value": "0.0",
                "12/31/88 Account Value": "0.0",
                "Post88 Contirbutions": "0.0",
                "Total": "0.00"
            },
            "Policy Summary(After Transaction)": {
                "Aggregate Pre-TEFRA Basis": "0.0",
                "Aggregate Pre-TEFRA Gain": "0.0",
                "Aggregate Pre-July86 Basis": "0.0",
                "Aggregate 12/31/86 Account Value": "0.0",
                "Aggregate 12/31/88 Account Value": "0.0",
                "Aggregate Post88 Contirbutions": "0.0",
                "Aggregate Total": "100000.0"
            },
            "Current Tax Year": "0",
            "Current Contribution Amount": "0.0",
            "Previous Tax Year": "0",
            "Previous Contribution Amount": "0.0",
            "Source Of Funds": "Cash Contribution",
            "Contribution": "NA",
            "Current Year Paymnet Type": "Cash Contribution",
            "Previous Year Paymnet Type": "Cash Contribution"
        }
    }
}
    }
   
    return db_data



import json

# Assuming rag_service is correctly implemented and imported.
class TestService:
    def __init__(self, rag_service):
        self.rag_service = rag_service
        self.rules = [
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
    "question": "What is FullName, FirstName, LastName?"
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
  {
    "nigo_id": "REN.NM.015",
    "question": "What is Guarantee Period, Owner/Annuitant DOB, Contract Issue Date?"
  },
  {
    "nigo_id": "REN.NM.016",
    "question": "What is Owner/Annuitant DOB?"
  },
  {
    "nigo_id": "REN.NM.017",
    "question": "What is Owner Name, Joint Owner Name, Contract Number, Guarantee Period, Case ID, Document Number, renewalRequestSignDate?"
  },
  {
    "nigo_id": "REN.NM.018",
    "question": "What is Channel, Printed Name?"
  },
  {
    "nigo_id": "REN.NM.019",
    "question": "What is Ownership Type, Title?"
  },
  {
    "nigo_id": "REN.NM.020",
    "question": "What is Transaction on Anniversary?"
  },
#   {
#     "nigo_id": "REN.NM.021",
#     "question": ""
#   },
  {
    "nigo_id": "REN.NM.024",
    "question": "What is Client Type, Signature Date, Ref_StalePeriod?"
  },
  {
    "nigo_id": "REN.NM.022",
    "question": "What is Client Type, Stale Period, Ref_StalePeriod?"
  },
  {
    "nigo_id": "REN.NM.025",
    "question": "What is Issue State, Renewal Period, External ID in LI State Requirement Review?"
  },
  {
    "nigo_id": "REN.NM.034",
    "question": "What is Account Code, Next Anniversary Date, tdRnewDate?"
  }  ]


    def embed_data_node(self):
        try:
            db_data = fetch_db_data_node()
            db_text = json.dumps(db_data, indent=2)
            success_db = self.rag_service.ingest_db_text(db_text)
            return success_db
        except Exception as e:
            return f"Exception in embed_data_node: {str(e)}"

    def validate_rule_node(self, rule: str):
        try:
            relevant_db_data = self.rag_service.retrieve_db(rule, k=5)
            return relevant_db_data
        except Exception as e:
            return f"Exception in validate_rule_node: {str(e)}"

    def test_all_rules(self):
        results = {}
        embedding_success = self.embed_data_node()
        if embedding_success is not True:
            return {"error": "Data embedding failed", "details": embedding_success}

        for rule in self.rules:
            rule_id = rule['nigo_id']
            rule_description = rule['question']
            retrieved_data = self.validate_rule_node(rule_description)
            results[rule_id] = retrieved_data
        return results


# Example usage:
if __name__ == '__main__':
    rag_service = RAGService()  # initialize your rag_service correctly here
    test_service = TestService(rag_service)

    rules = [
       
        {"nigo_id": "REN.NM.004", "description": "If Guarantee Period attribute is missing in ocr data, flag the form."},
        {"nigo_id": "REN.NM.001", "description": "If the current guarantee period is not equal to 1 year, then check whether the current period is one of 3, 4, or 5 and the requested guarantee period is one of 1, 3, 4, or 5. If this condition is not met, flag the form."},
        {"nigo_id": "REN.NM.023", "description": "After calling PolicyInfo API to retrieve LastAnniversaryDate, if it equals 2999-12-31T00:00:00, flag the form."},
        {"nigo_id": "REN.NM.003", "description": "Match for full name in db data and ocr data , if not present check of first name and last name  with the ocr name else flag the form."},
        {"nigo_id": "REN.NM.002", "description": "If Contract Number attribute is missing in OCR data or does not match the value from db data, flag the form."},
        {"nigo_id": "REN.NM.010", "description": "If Contract Status is not valid per Ref_Contract, flag the form."},
        # {"nigo_id": "REN.NM.005", "description": "If Signature Date attribute does not match Signature Type attribute, flag the form."},
        {"nigo_id": "REN.NM.006", "description": "If the channel is not Phone and Signature is missing in ocr, flag the form."},
        {"nigo_id": "REN.NM.012", "description": "If Contract PlanCode is not present or not configured in Ref_Product, flag the form."},
        {"nigo_id": "REN.NM.013", "description": "If Issue State is FL and the Owner/Annuitant's age is 65 or older at Issue Date, flag the form."},
        {"nigo_id": "REN.NM.014", "description": "If Issue State is MT and Issue Date is on or after 2018-01-01, flag the form."},
        {"nigo_id": "REN.NM.015", "description": "Compare Guarantee Period against allowed limit based on the 90th birthday of the oldest owner/annuitant and 10 years after the Contract Issue Date; if outside the allowed range, flag the form."},
        {"nigo_id": "REN.NM.016", "description": "If the Date of Birth of the owner/annuitant is not available, flag the form."},
        {"nigo_id": "REN.NM.017", "description": "If one or more required fields (e.g., Owner Name, Joint Owner Name, Contract Number, Guarantee Period, Signatures, Dates, Good Order Date, Case ID, Document Number, renewalRequestSignDate, etc.) are missing, flag the form."},
        {"nigo_id": "REN.NM.018", "description": "If the channel is not Phone and Printed Name is missing, flag the form."},
        {"nigo_id": "REN.NM.019", "description": "If the contract is trust-owned and Title is missing, flag the form."},
        {"nigo_id": "REN.NM.020", "description": "If a transaction on Anniversary is detected via LifeCad API, flag the form."},
        {"nigo_id": "REN.NM.021", "description": "After validations, if not all checks are IGO, flag the form."},
        {"nigo_id": "REN.NM.024", "description": "For client MASS, if Sign Date is outside the allowed stale period (per Ref_SlatePeriod), flag the form."},
        {"nigo_id": "REN.NM.022", "description": "For clients other than MASS, if the stale period condition is not met, flag the form."},
        {"nigo_id": "REN.NM.025", "description": "For Issue State NY and renewal periods 3, 4, or 5, if the External ID is invalid in the LI State Requirement Review, flag the form."},
        {"nigo_id": "REN.NM.034", "description": "Compare the account code from accountQuote with the getTransactionDetails API; if Next Anniversary Date does not match tdRnewDate, flag the form."}
  ]

    result = test_service.test_all_rules(rules)
    print(json.dumps(result, indent=2))


