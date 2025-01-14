
# Incrementally load data from a source data store to a destination data store

https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-overview


# method 1 - Incrementally load data from Azure SQL Database to Azure Blob Storage using change tracking information using PowerShell
https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-change-tracking-feature-powershell

Change Tracking technology is a lightweight solution in SQL Server and Azure SQL Database that provides an efficient change tracking mechanism for applications. It enables an application to easily identify data that was inserted, updated, or deleted.

1. Install Azure PowerShell on Linux 
https://learn.microsoft.com/en-us/powershell/azure/install-azps-linux?view=azps-13.0.0


zec@zec-HP-EliteBook-840-G3:~$ pwsh
PowerShell 7.4.6
PS /home/zec> Install-Module -Name Az -Repository PSGallery -Force
PS /home/zec> Update-Module -Name Az -Force                                                                             
PS /home/zec> Connect-AzAccount                                                                                         
Please select the account you want to login with.                                                                       

Retrieving subscriptions for the selection...

[Announcements]
With the new Azure PowerShell login experience, you can select the subscription you want to use more easily. Learn more about it and its configuration at https://go.microsoft.com/fwlink/?linkid=2271909.

If you encounter any problem, please open an issue at: https://aka.ms/azpsissue

Subscription name Tenant
----------------- ------
Pay-As-You-Go     Default Directory

PS /home/zec> 



2. Create an Azure storage account
https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal




3. Create a single database - Azure SQL Database
https://learn.microsoft.com/en-us/azure/azure-sql/database/single-database-create-quickstart?view=azuresql&tabs=azure-portal


https://portal.azure.com/#create/Microsoft.AzureSQL

username - azureuser
password - Vajay8679@



SELECT name 
FROM sys.databases;

one
SELECT name 
FROM sys.schemas;


----------------------------

create table data_source_table
(
    PersonID int NOT NULL,
    Name varchar(255),
    Age int
    PRIMARY KEY (PersonID)
);


INSERT INTO data_source_table
    (PersonID, Name, Age)
VALUES
    (1, 'aaaa', 21),
    (2, 'bbbb', 24),
    (3, 'cccc', 20),
    (4, 'dddd', 26),
    (5, 'eeee', 22);

SELECT TOP (1000) * FROM [dbo].[data_source_table]



4. Enable Change Tracking mechanism on your database and the source table (data_source_table) by running the following SQL query:

ALTER DATABASE mySampleDatabase
SET CHANGE_TRACKING = ON  
(CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON)  

ALTER TABLE data_source_table
ENABLE CHANGE_TRACKING  
WITH (TRACK_COLUMNS_UPDATED = ON)


5. Create a new table and store the ChangeTracking_version with a default value by running the following query:

create table table_store_ChangeTracking_version
(
    TableName varchar(255),
    SYS_CHANGE_VERSION BIGINT,
);

DECLARE @ChangeTracking_version BIGINT
SET @ChangeTracking_version = CHANGE_TRACKING_CURRENT_VERSION();  

INSERT INTO table_store_ChangeTracking_version
VALUES ('data_source_table', @ChangeTracking_version)


6. Run the following query to create a stored procedure in your database. The pipeline invokes this stored procedure to update the change tracking version in the table you created in the previous step.


CREATE PROCEDURE Update_ChangeTracking_Version @CurrentTrackingVersion BIGINT, @TableName varchar(50)
AS

BEGIN

UPDATE table_store_ChangeTracking_version
SET [SYS_CHANGE_VERSION] = @CurrentTrackingVersion
WHERE [TableName] = @TableName

END



7. Create a data factory with powershell

$resourceGroupName = "ADFTutorialResourceGroup";


to chek location - Get-AzLocation | Select-Object Location, DisplayName

$location = "Central India"


- To create the Azure resource group, run the following command: -> 
New-AzResourceGroup $resourceGroupName $location

- datafactory name->
PS /home/zec> $dataFactoryName = "ZecDataCopyChgTrackingDF";  

- To create the data factory, run the following Set-AzDataFactoryV2 cmdlet:
PS /home/zec> Set-AzDataFactoryV2 -ResourceGroupName $resourceGroupName -Location $location -Name $dataFactoryName



8. Create Azure Storage linked service



Create a JSON file named AzureStorageLinkedService.json in C:\ADFTutorials\IncCopyChangeTrackingTutorial folder with the following content: (Create the folder if it does not already exist.). Replace <accountName>, <accountKey> with name and key of your Azure storage account before saving the file.



9. In Azure PowerShell, switch to the C:\ADFTutorials\IncCopyChangeTrackingTutorial folder.

10. Create Azure Storage linked service

Run the Set-AzDataFactoryV2LinkedService cmdlet to create the linked service: AzureStorageLinkedService. In the following example, you pass values for the ResourceGroupName and DataFactoryName parameters.


Set-AzDataFactoryV2LinkedService -DataFactoryName $dataFactoryName -ResourceGroupName $resourceGroupName -Name "AzureStorageLinkedService" -File ".\AzureStorageLinkedService.json"


Set-AzDataFactoryV2LinkedService -DataFactoryName "ZecDataCopyChgTrackingDF" -ResourceGroupName "ADFTutorialResourceGroup" -Name "AzureStorageLinkedService" -File ".\AzureStorageLinkedService.json"


11. Create Azure SQL Database linked service.

Create a JSON file named AzureSQLDatabaseLinkedService.json in C:\ADFTutorials\IncCopyChangeTrackingTutorial folder with the following content: Replace <your-server-name> and <your-database-name> with the name of your server and database before you save the file. You must also configure your Azure SQL Server to grant access to your data factory's managed identity.

before below process go to azue sql -> mysqlserverajay -> setting -> microsoft entra id -> set admin -> select user and selcect and save

Set-AzDataFactoryV2LinkedService -DataFactoryName $dataFactoryName -ResourceGroupName $resourceGroupName -Name "AzureSQLDatabaseLinkedService" -File ".\AzureSQLDatabaseLinkedService.json"

Set-AzDataFactoryV2LinkedService -DataFactoryName "ZecDataCopyChgTrackingDF" -ResourceGroupName "ADFTutorialResourceGroup" -Name "AzureSQLDatabaseLinkedService" -File ".\AzureSQLDatabaseLinkedService.json"


12. Create a source dataset

Create a JSON file named SourceDataset.json in the same folder with the following content:

Set-AzDataFactoryV2Dataset -DataFactoryName $dataFactoryName -ResourceGroupName $resourceGroupName -Name "SourceDataset" -File ".\SourceDataset.json"


Set-AzDataFactoryV2Dataset -DataFactoryName "ZecDataCopyChgTrackingDF" -ResourceGroupName "ADFTutorialResourceGroup" -Name "SourceDataset" -File ".\SourceDataset.json"


13. Create a sink dataset


Create a JSON file named SinkDataset.json in the same folder with the following content:


Set-AzDataFactoryV2Dataset -DataFactoryName $dataFactoryName -ResourceGroupName $resourceGroupName -Name "SinkDataset" -File ".\SinkDataset.json"


Set-AzDataFactoryV2Dataset -DataFactoryName "ZecDataCopyChgTrackingDF" -ResourceGroupName "ADFTutorialResourceGroup" -Name "SinkDataset" -File ".\SinkDataset.json"


14. Create a change tracking dataset

Create a JSON file named ChangeTrackingDataset.json in the same folder with the following content:


Set-AzDataFactoryV2Dataset -DataFactoryName $dataFactoryName -ResourceGroupName $resourceGroupName -Name "ChangeTrackingDataset" -File ".\ChangeTrackingDataset.json"


Set-AzDataFactoryV2Dataset -DataFactoryName "ZecDataCopyChgTrackingDF" -ResourceGroupName "ADFTutorialResourceGroup" -Name "ChangeTrackingDataset" -File ".\ChangeTrackingDataset.json"

15. Create a pipeline for the full copy

Create a JSON file: FullCopyPipeline.json in same folder with the following content:

Set-AzDataFactoryV2Pipeline -DataFactoryName $dataFactoryName -ResourceGroupName $resourceGroupName -Name "FullCopyPipeline" -File ".\FullCopyPipeline.json"

Set-AzDataFactoryV2Pipeline -DataFactoryName "ZecDataCopyChgTrackingDF" -ResourceGroupName "ADFTutorialResourceGroup" -Name "FullCopyPipeline" -File ".\FullCopyPipeline.json"


16. Run the full copy pipeline

we have to add IP - azure sql ->security -> networking -> Firewall rules


Invoke-AzDataFactoryV2Pipeline -PipelineName "FullCopyPipeline" -ResourceGroup $resourceGroupName -dataFactoryName $dataFactoryName


Invoke-AzDataFactoryV2Pipeline -PipelineName "FullCopyPipeline" -ResourceGroup "ADFTutorialResourceGroup" -dataFactoryName "ZecDataCopyChgTrackingDF"

if getting error while checking adf monitor pipeline run

inlinked service 
AzureSQLDatabaseLinkedService use username and password



17. Review the results



18. Add more data to the source table

INSERT INTO data_source_table
(PersonID, Name, Age)
VALUES
(6, 'new','50');


UPDATE data_source_table
SET [Age] = '10', [name]='update' where [PersonID] = 1


19. Create a pipeline for the delta copy

Create a JSON file: IncrementalCopyPipeline.json in same folder with the following content:


Set-AzDataFactoryV2Pipeline -DataFactoryName $dataFactoryName -ResourceGroupName $resourceGroupName -Name "IncrementalCopyPipeline" -File ".\IncrementalCopyPipeline.json"


Set-AzDataFactoryV2Pipeline -DataFactoryName "ZecDataCopyChgTrackingDF" -ResourceGroupName "ADFTutorialResourceGroup" -Name "IncrementalCopyPipeline" -File ".\IncrementalCopyPipeline.json"


20. Run the incremental copy pipeline

we have to add IP - azure sql ->security -> networking -> Firewall rules

this will run only when you go to azure sql ->security -> networking -> enabled (checked) allow azure services and resources to access this server.

Invoke-AzDataFactoryV2Pipeline -PipelineName "IncrementalCopyPipeline" -ResourceGroup $resourceGroupName -dataFactoryName $dataFactoryName


Invoke-AzDataFactoryV2Pipeline -PipelineName "IncrementalCopyPipeline" -ResourceGroup "ADFTutorialResourceGroup" -dataFactoryName "ZecDataCopyChgTrackingDF"





---------------------------------------------------



# method 2 - Incrementally copy new and changed files based on LastModifiedDate by using the Copy Data tool
https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-lastmodified-copy-data-tool


You can copy the new and changed files only by using LastModifiedDate to the destination store. ADF will scan all the files from the source store, apply the file filter by their LastModifiedDate, and only copy the new and updated file since last time to the destination store. Please be aware that if you let ADF scan huge amounts of files but you only copy a few files to the destination, this will still take a long time because of the file scanning process.






# method 3- Incrementally copy new files based on time partitioned folder or file name from Azure Blob storage to Azure Blob storage

https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-partitioned-file-name-copy-data-tool


You can copy new files only, where files or folders has already been time partitioned with timeslice information as part of the file or folder name (for example, /yyyy/mm/dd/file.csv). It is the most performant approach for incrementally loading new files.



# method 4 - Incrementally load data from Azure SQL Managed Instance to Azure Storage using change data capture (CDC)
https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-change-data-capture-feature-portal

You perform the following steps in this tutorial:

Prepare the source data store
Create a data factory.
Create linked services.
Create source and sink datasets.
Create, debug and run the pipeline to check for changed data
Modify data in the source table
Complete, run and monitor the full incremental copy pipeline


you create a pipeline that performs the following operations:

Create a lookup activity to count the number of changed records in the SQL Database CDC table and pass it to an IF Condition activity.
Create an If Condition to check whether there are changed records and if so, invoke the copy activity.
Create a copy activity to copy the inserted/updated/deleted data between the CDC table to Azure Blob Storage.




create table customers 
(
customer_id int, 
first_name varchar(50), 
last_name varchar(50), 
email varchar(100), 
city varchar(50), CONSTRAINT "PK_Customers" PRIMARY KEY CLUSTERED ("customer_id") 
 );


EXEC sys.sp_cdc_enable_db 

EXEC sys.sp_cdc_enable_table
@source_schema = 'dbo',
@source_name = 'customers', 
@role_name = NULL,
@supports_net_changes = 1



insert into customers 
     (customer_id, first_name, last_name, email, city) 
 values 
     (1, 'Chevy', 'Leward', 'cleward0@mapy.cz', 'Reading'),
     (2, 'Sayre', 'Ateggart', 'sateggart1@nih.gov', 'Portsmouth'),
    (3, 'Nathalia', 'Seckom', 'nseckom2@blogger.com', 'Portsmouth');
