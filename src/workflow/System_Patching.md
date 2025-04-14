# Temporal Workflow: System Patching

The idea here is to automate applying software patches/update OS packages on VMs and bare-metal hosts, while taking care
of:

- Requests/Approvals.
- Gracefully stopping/draining workloads.
- Notifications.
- Pilot updates on a limited number of hosts.

## Workflow Name

`SystemPatchWorkflow`

## Workflow Input

* `targetClusters`: List of Strings (e.g., `["cluster-a", "cluster-b"]`)
* `pilotHostCount`: Integer (number of pilot hosts)
* `approverEmails`: List of Strings (e.g., `["foo@example.com", "bar@example.com"]`)
* `requesterEmail`: String (e.g., "baz@example.com")
* `vaultAddress`: String (e.g., "[https://vault.example.com:8200](https://vault.example.com:8200)")
* `vaultToken`: String (Vault access token)
* `secretPathPrefix`: String (e.g., "patch-deploy")
* `updateCommand`: String (e.g., "apt-get update && apt-get upgrade -y")
* `serviceList`: List of strings (example: `["postgresql", "nginx"]`)

## Workflow Steps (Activities)

1. **`SendApprovalRequestActivity`**:
    * Input: `targetClusters`, `approverEmails`, `requesterEmail`.
    * Logic: Sends an approval request notification.
    * Return: `Boolean` (true if approved).

2. **`GetClusterHostsActivity`**:
    * Input: `targetCluster`.
    * Logic: Retrieves the list of hosts belonging to a cluster.
    * Return: `List` of Strings (hostnames).

3. **`CheckHostPreconditionsActivity`**:
    * Input: `hostname`.
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Checks host health.
        * Verifies maintenance mode status.
    * Return: `Boolean` (true if preconditions met), `String` (SSH private key).

4. **`SendStartNotificationActivity`**:
    * Input: `hostname`, `requesterEmail`.
    * Logic: Sends a notification that the update is starting.
    * Return: `Boolean` (true if notification sent).

5. **`RunPreDowntimeScriptsActivity`**:
    * Input: `hostname`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Executes pre-downtime scripts (if applicable).
    * Return: `Boolean` (true if successful).

6. **`SetMaintenanceModeActivity`**:
    * Input: `hostname`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Puts the host into maintenance mode.
    * Return: `Boolean` (true if successful).

7. **`StopServicesActivity`**:
    * Input: `hostname`, `serviceList`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Stops specified services on the host.
    * Return: `Boolean` (true if successful).

8. **`WaitForWorkloadDrainActivity`**:
    * Input: `hostname`
    * Logic: Waits for workloads to drain.
    * Return: `Boolean` (true if drain successful).

9. **`RunPreUpdateScriptsActivity (optional)`**:
    * Input: `hostname`, `preUpdateScripts`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Executes pre-update scripts (if applicable).
    * Return: `Boolean` (true if successful).

10. **`PerformUpdateActivity`**:
    * Input: `hostname`, `updateCommand`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Executes the update command.
    * Return: `Boolean` (true if successful).

11. **`StartServicesActivity`**:
    * Input: `hostname`, `serviceList`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Starts specified services.
    * Return: `Boolean` (true if successful).

12. **`RunPostUpdateScriptsActivity (optional)`**:
    * Input: `hostname`, `postUpdateScripts`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Executes post-update scripts (if applicable).
    * Return: `Boolean` (true if successful).

13. **`CheckServiceHealthActivity`**:
    * Input: `hostname`, `serviceList`
    * Logic:
        * Retrieves SSH key from Vault using `VaultClient`.
        * Checks if services have become healthy (with timeout).
            * If timeout reached, bail out.
    * Return: `Boolean` (true if healthy).
   
14. **`SendSuccessNotificationActivity`**:
    * Input: `hostname`, `requesterEmail`.
    * Logic: Sends a success notification.
    * Return: `Boolean` (true if notification sent).

15. **`SendFailureAlertActivity`**:
    * Input: `hostname`, `failureDetails`, `requesterEmail`.
    * Logic: Sends a failure alert.
    * Return: `Boolean` (true if alert sent).

## Workflow Logic

1. Start workflow and receive input.
2. Execute `SendApprovalRequestActivity`. If not approved, terminate.
3. Execute `VaultClientActivity`.
4. For each `targetCluster`:
    * Get cluster hosts using `GetClusterHostsActivity`.
    * Process **pilot hosts**:
        * For each pilot host (up to `pilotHostCount`):
            * Execute `CheckHostPreconditionsActivity`. If false, execute `SendFailureAlertActivity` and terminate.
            * If any patching activity fails, execute `SendFailureAlertActivity` and terminate.
            * Execute `SendSuccessNotificationActivity`.
   
    * Process remaining hosts:
        * For each remaining host:
            * Execute `CheckHostPreconditionsActivity`. If false, execute `SendFailureAlertActivity` and terminate.
            * Execute host patching activities, passing the retrieved SSH key.
            * If any patching activity fails, execute `SendFailureAlertActivity` and terminate.
            * Execute `SendSuccessNotificationActivity`.
              
5. Send a final success notification.
6. Complete the workflow.

## Error Handling

* Each activity has retry policies.
* `SendFailureAlertActivity` stops the rollout on any host failure.
* Vault cleanup is attempted during failures, though this might be limited in scope.
* Temporal cancellation scopes are used where applicable.
* Local activities are used where applicable.