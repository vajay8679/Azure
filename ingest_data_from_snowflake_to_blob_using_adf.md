
# ingest data from on-premsies to adlg2 using adf

1. create integration runtime 
    1. Azure, self-hosted - perform data flow,data movement and dispatch activities to external compute 
        1.1 Azure -> Use this for running data flows, data movement, external and pipeline activities in a fully managed, serverless compute in Azure.
        1.2 Self-Hosted -> Use this for running data movement, external and pipeline activities in an on-premises / private network by installing the integration runtime. 

        Note: Data flows are only supported on Azure integration runtime. You can use self-hosted integration runtime to stage the data on cloud storage and then use data flows to transform it. 

        we have to install integration runtime -> and paste key inside it 


    2. Azure SSIS - Lift-and-shift existing SSIS packages to execute in azure

    
    ![alt text](integration_runtime.png)


2. Create Linked Services inside azure data factory - Manage
   Snowflake1 - 
            select data source -> snowflake
            attached integration runtime
            account='jhpmgzi-xt72971',
            database='TEST_DB',
            warehouse='COMPUTE_WH',
            user='Vajay8679',
            password='Vajay8679@',
            Role='ACCOUNTADMIN'
            HOST - https://jhpmgzi-xt7271.snowflakecomputing.com

    AzureBlobStorage2 -
            select data source -> azureblobstoarge
            attached integration runtime
            authentication type - SAS URI 
            SAS URL - SAS url - https://zecdatastorage.blob.core.windows.net/
            SAS Token - token
            Test connection - to linked service 

3. Inside Author create Pipelines 
        Inside activities -> Move and transform -> copy data
        source ->select new dataset -> snowflake
            import schema -> from connection/store
        Sink -> Azure Blob Storage
                select format - json/parquet
                linked service 
                import schema -> from connection/store
        setting -> enable staging
                    stageibg account linked service - AzureBlobStorage2  