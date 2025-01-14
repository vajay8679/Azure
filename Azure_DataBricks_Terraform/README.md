terraform init
terraform validate
terraform fmt
terraform plan
terraform apply -auto-approve
terraform destroy


[
  {
    "cloudName": "AzureCloud",
    "id": "95d06dc2-ec1c-4960-98d5-4fcfd6ca129e",
    "isDefault": true,
    "name": "Pay-As-You-Go",
    "state": "Enabled",
    "tenantId": "68fb41d6-7f2e-48ee-96d3-fa588a2a44e7",
    "user": {
      "name": "abhishek1580051@outlook.com",
      "type": "user"
    }
  }
]
                                                            



[
  {
    "cloudName": "AzureCloud",
    "id": "95d06dc2-ec1c-4960-98d5-4fcfd6ca129e",
    "isDefault": true,
    "name": "Pay-As-You-Go",
    "state": "Enabled",
    "tenantId": "68fb41d6-7f2e-48ee-96d3-fa588a2a44e7",
    "user": {
      "name": "abhishek1580051_outlook.com#EXT#@abhishek1580051outlook.onmicrosoft.com",
      "type": "user"
    }
  }
]


# 1. lgoin

az login

# 2.  Run the following Azure CLI command to assign the role:

az role assignment create --assignee 6de2b41d-2c76-46ad-be8e-6f7fcf4da43f --role Contributor --scope /subscriptions/95d06dc2-ec1c-4960-98d5-4fcfd6ca129e

# 3. Run the following Azure CLI commands:

az provider register --namespace Microsoft.Resources
az provider register --namespace Microsoft.Databricks


# 4. If you're using Azure CLI to authenticate, use:
az login
az account set --subscription 95d06dc2-ec1c-4960-98d5-4fcfd6ca129e


# 5. If you're using Service Principal credentials, ensure they are correctly set in your environment:

export ARM_CLIENT_ID="6de2b41d-2c76-46ad-be8e-6f7fcf4da43f"
export ARM_CLIENT_SECRET="saJ8Q~Ie6wOkozGs-GccvJCDJaqfoq8tbp3GDcyp"
export ARM_TENANT_ID="68fb41d6-7f2e-48ee-96d3-fa588a2a44e7"
export ARM_SUBSCRIPTION_ID="95d06dc2-ec1c-4960-98d5-4fcfd6ca129e"




