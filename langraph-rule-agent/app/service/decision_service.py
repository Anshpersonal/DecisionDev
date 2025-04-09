# app/service/decision_service.py - Service for decision service integration

import requests
from requests.auth import HTTPBasicAuth
import json
import os
from app.config import Config
from app.model.rule_model import Tool

config = Config()

class DecisionService:
    """Base class for decision services"""
    
    def __init__(self):
        """Initialize decision service"""
        self.server_url = ""
        self.username = ""
        self.password = ""
        self.is_connected = False
    
    def invoke_decision_service(self, ruleset_path, decision_inputs):
        """
        Invoke a decision service
        
        Args:
            ruleset_path (str): Path to the ruleset
            decision_inputs (dict): Input parameters for the decision
            
        Returns:
            dict: Result of the decision service invocation
        """
        raise NotImplementedError("Subclasses must implement invoke_decision_service")

class ODMService(DecisionService):
    """Service for IBM Operational Decision Manager"""
    
    def __init__(self):
        """Initialize ODM service"""
        super().__init__()
        self.server_url = config.ODM_SERVER_URL
        self.username = config.ODM_USERNAME
        self.password = config.ODM_PASSWORD
        
        if not self.server_url.startswith("http://") and not self.server_url.startswith("https://"):
            self.server_url = "http://" + self.server_url
        
        self.trace = { 
            "__TraceFilter__": {
                "none": True,
                "infoTotalRulesFired": True,
                "infoRulesFired": True
            }
        }
        
        self.is_connected = self._check_odm_server()
    
    def _check_odm_server(self):
        """Check if the ODM server is available"""
        print(f"Checking connection to ODM Server: {self.server_url}/res/api/v1/ruleapps")
        
        try:
            response = requests.get(
                f"{self.server_url}/res/api/v1/ruleapps",
                json={},
                auth=HTTPBasicAuth(self.username, self.password)
            )
            
            if response.status_code != 200:
                print(f"Unable to reach Decision Server console, status: {response.status_code}")
                return False
            
            response = requests.get(
                f"{self.server_url}/DecisionService",
                json={},
                auth=HTTPBasicAuth(self.username, self.password)
            )
            
            if response.status_code != 200:
                print(f"Unable to reach Decision Server Runtime, status: {response.status_code}")
                return False
            else:
                print("Connection with ODM Server is OK")
                return True
        except requests.exceptions.RequestException as e:
            print(f"Unable to reach ODM Runtime: {e}")
            return False
    
    def invoke_decision_service(self, ruleset_path, decision_inputs):
        """
        Invoke an ODM decision service
        
        Args:
            ruleset_path (str): Path to the ruleset
            decision_inputs (dict): Input parameters for the decision
            
        Returns:
            dict: Result of the decision service invocation
        """
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        params = {**decision_inputs, **self.trace}
        
        try:
            response = requests.post(
                f"{self.server_url}/DecisionService/rest{ruleset_path}",
                headers=headers,
                json=params,
                auth=HTTPBasicAuth(self.username, self.password)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request error, status: {response.status_code}")
                return {"error": f"Request error, status: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"An error occurred when invoking the Decision Service: {str(e)}"}

class ADSService(DecisionService):
    """Service for IBM Automation Decision Services"""
    
    def __init__(self):
        """Initialize ADS service"""
        super().__init__()
        self.server_url = config.ADS_SERVER_URL
        self.user_id = config.ADS_USER_ID
        self.zen_api_key = config.ADS_ZEN_APIKEY
        
        if self.server_url and not self.server_url.startswith("https://"):
            self.server_url = "https://" + self.server_url
        
        self.is_connected = self._check_ads_server()
    
    def _check_ads_server(self):
        """Check if the ADS server is available"""
        if not self.server_url or not self.user_id or not self.zen_api_key:
            print("ADS configuration incomplete")
            return False
        
        print(f"Check connection to ADS Server: {self.server_url}")
        
        try:
            path = "/ads/runtime/api/v1/about"
            full_path = f"{self.server_url}{path}"
            
            response = requests.get(full_path, verify=False)
            
            if response.status_code == 200:
                print("Connection with ADS Server is OK")
                return True
            else:
                print(f"Error checking ADS server: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Unable to reach ADS Runtime: {e}")
            return False
    
    def invoke_decision_service(self, ruleset_path, decision_inputs):
        """
        Invoke an ADS decision service
        
        Args:
            ruleset_path (str): Path to the ruleset
            decision_inputs (dict): Input parameters for the decision
            
        Returns:
            dict: Result of the decision service invocation
        """
        if not self.is_connected:
            return {"error": "Not connected to ADS server"}
        
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'ZenApiKey {self.zen_api_key}'
        }
        
        path = "/ads/runtime/api/v1/deploymentSpaces/embedded/decisions/"
        full_path = f"{self.server_url}{path}_{self.user_id}{ruleset_path}"
        
        try:
            response = requests.post(
                full_path,
                headers=headers,
                json=decision_inputs,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"An error occurred when invoking the Decision Service: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"An error occurred when invoking the Decision Service: {str(e)}"}

class DecisionServiceFactory:
    """Factory for creating decision services"""
    
    @staticmethod
    def get_decision_service(service_type):
        """
        Get a decision service by type
        
        Args:
            service_type (str): Type of decision service ('odm' or 'ads')
            
        Returns:
            DecisionService: Instance of the requested decision service
        """
        if service_type.lower() == 'odm':
            return ODMService()
        elif service_type.lower() == 'ads':
            return ADSService()
        else:
            raise ValueError(f"Unsupported decision service type: {service_type}")
    
    @staticmethod
    def get_available_services():
        """
        Get all available decision services
        
        Returns:
            dict: Dictionary of available decision services
        """
        services = {}
        
        odm_service = ODMService()
        if odm_service.is_connected:
            services['odm'] = odm_service
        
        ads_service = ADSService()
        if ads_service.is_connected:
            services['ads'] = ads_service
        
        return services
    
    @staticmethod
    def load_tools():
        """
        Load tool definitions from tool_descriptors directories
        
        Returns:
            list: List of tool definitions
        """
        tools = []
        base_path = config.DATADIR
        
        # Find tool descriptor directories
        descriptor_dirs = []
        for root, dirs, files in os.walk(base_path):
            for dir_name in dirs:
                if dir_name == 'tool_descriptors':
                    descriptor_dirs.append(os.path.join(root, dir_name))
        
        # Load tool definitions from each directory
        for directory in descriptor_dirs:
            if os.path.exists(directory):
                tool_files = [f for f in os.listdir(directory) if f.endswith('.json')]
                for tool_file in tool_files:
                    file_path = os.path.join(directory, tool_file)
                    with open(file_path, 'r') as f:
                        try:
                            tool_data = json.load(f)
                            tool = Tool(**tool_data)
                            tools.append(tool)
                        except Exception as e:
                            print(f"Error loading tool from {file_path}: {e}")
        
        return tools