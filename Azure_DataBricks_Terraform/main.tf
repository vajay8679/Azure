resource "azurerm_resource_group" "resourcegroup" {
  name     = "databricks-terraform-rg"
  location = "Central India"
}

resource "azurerm_databricks_workspace" "workspace" {
  location            = azurerm_resource_group.resourcegroup.location
  name                = "databricks-terraform-ws"
  resource_group_name = azurerm_resource_group.resourcegroup.name
  sku                 = "premium"
}


data "databricks_node_type" "smallest" {
  depends_on = [azurerm_databricks_workspace.workspace]
  local_disk = true
}

data "databricks_spark_version" "latest_lts" {
  depends_on        = [azurerm_databricks_workspace.workspace]
  long_term_support = true
}

resource "databricks_instance_pool" "pool" {
  instance_pool_name                    = "databricks-terraform-pool"
  min_idle_instances                    = 0
  max_capacity                          = 10
  node_type_id                          = data.databricks_node_type.smallest.id
  idle_instance_autotermination_minutes = 10

}

resource "databricks_cluster" "shared_autoscaling" {
  depends_on              = [azurerm_databricks_workspace.workspace]
  instance_pool_id        = databricks_instance_pool.pool.id
  cluster_name            = "Shared Autoscaling-Terraform"
  spark_version           = data.databricks_spark_version.latest_lts.id
  # node_type_id            = data.databricks_node_type.smallest.id
  autotermination_minutes = 20
  autoscale {
    min_workers = 1
    max_workers = 5
  }

  spark_conf = {
    "spark.databricks.io.cache.enabled" : true
  }

  custom_tags = {
    "createdby" = "InfraTeam"
  }
}