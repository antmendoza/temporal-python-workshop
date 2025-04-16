from datetime import timedelta
from typing import List

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import FailureError, ActivityError

from src.workflow.activities import MyActivities
from src.workflow.types import SystemPatchWorkflowInput, SendApprovalRequestActivityInput, VaultClientActivityInput, \
    GetClusterHostsActivityInput, CheckHostPreconditionsActivityInput, SendSuccessNotificationActivityInput, \
    SendFailureAlertActivityInput, RunPreDowntimeScriptsActivityInput, \
    SetMaintenanceModeActivityInput, StopServicesActivityInput, WaitForWorkloadDrainActivityInput, \
    RunPreUpdateScriptsActivityInput, PerformUpdateActivityInput, StartServicesActivityInput, \
    RunPostUpdateScriptsActivityInput, CheckServiceHealthActivityInput, SendFinalSuccessNotificationActivityInput


@workflow.defn
class SystemPatchWorkflow_V1:
    def __init__(self):
        self.wf_input: SystemPatchWorkflowInput = None

    @workflow.run
    async def run(self, wf_input: SystemPatchWorkflowInput) -> str:
        self.wf_input = wf_input

        workflow.logger.info("Workflow starts ")

        # TODO 2. Execute `SendApprovalRequestActivity`.

        # 3. Execute `VaultClientActivity`.
        vault_client_response = await self.vault_client_activity()

        workflow.logger.info("target_clusters %s", wf_input.targetClusters)

        # 4. For each `targetCluster`:
        for target_cluster in wf_input.targetClusters:
            await self._process_target_cluster(target_cluster)

        await self.send_final_success_notification_activity()


        workflow.logger.info("About to complete workflow")

        return "your output"

    async def send_final_success_notification_activity(self):
        await workflow.execute_activity_method(
            activity=MyActivities.send_final_success_notification_activity,
            arg=SendFinalSuccessNotificationActivityInput(
                # ...
            ),
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

    async def vault_client_activity(self):
        return await workflow.execute_activity_method(
            activity=MyActivities.vault_client_activity,
            arg=VaultClientActivityInput(
                # ...
            ),
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

    async def send_approval_request_activity(self):
        await workflow.execute_activity_method(
            activity=MyActivities.send_approval_request_activity,
            arg=SendApprovalRequestActivityInput(
                targetClusters=self.wf_input.targetClusters,
                approverEmails=self.wf_input.approverEmails,
                # ...
            ),
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

    async def _process_target_cluster(self, target_cluster):

        workflow.logger.debug("processing target_cluster %s", target_cluster)

        #  Get cluster hosts using `GetClusterHostsActivity`.
        get_cluster_hosts_response = await workflow.execute_activity_method(
            activity=MyActivities.get_cluster_hosts_activity,
            arg=GetClusterHostsActivityInput(
                targetCluster=target_cluster,
                # ...
            ),
            start_to_close_timeout=timedelta(seconds=2),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        # * Process **pilot hosts**:
        pilot_hosts = get_cluster_hosts_response.hostnames[:self.wf_input.pilotHostCount]
        await self._process_pilot_hosts(pilot_hosts)

        # * Process remaining hosts
        remaining_hosts = get_cluster_hosts_response.hostnames[self.wf_input.pilotHostCount:]
        await self._process_remaining_hosts(remaining_hosts)

    async def _process_pilot_hosts(self, pilot_hosts: List[str]):

        workflow.logger.debug("processing pilot hosts %s", pilot_hosts)

        # * Process **pilot hosts**:
        for host in pilot_hosts:
            await self._process_host(host)

        
        

    async def _process_remaining_hosts(self, remaining_hosts: List[str]):

        workflow.logger.debug("processing remaining hosts %s", remaining_hosts)

        for host in remaining_hosts:
            await self._process_host(host)

        

    

    async def _process_host(self, host):

        workflow.logger.debug("processing hosts %s", host)

        try:

            # Execute `CheckHostPreconditionsActivity`.
            check_host_preconditions_activity_result = await workflow.execute_activity_method(
                activity=MyActivities.check_host_preconditions_activity,
                arg=CheckHostPreconditionsActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            if not check_host_preconditions_activity_result.preconditionsMet:
                # If false, execute `SendFailureAlertActivity` and terminate.
                await workflow.execute_activity_method(
                    activity=MyActivities.send_failure_alert_activity,
                    arg=SendFailureAlertActivityInput(
                        hostname=host,
                        # ...
                    ),
                    start_to_close_timeout=timedelta(seconds=5),
                    retry_policy=RetryPolicy(maximum_attempts=3)
                )

                return

            ## execute patching activities
            await workflow.execute_activity_method(
                activity=MyActivities.run_pre_downtime_scripts_activity,
                arg=RunPreDowntimeScriptsActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            #skip set_maintenance_mode_activity

            #skip stop_services_activity

            #skip wait_for_workload_drain_activity

            #skip run_pre_update_scripts_activity

            await workflow.execute_activity_method(
                activity=MyActivities.perform_update_activity,
                arg=PerformUpdateActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            #skip start_services_activity


            # skip run_post_update_scripts_activity

            await workflow.execute_activity_method(
                activity=MyActivities.check_service_health_activity,
                arg=CheckServiceHealthActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=10,
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=1
                )
            )

        except ActivityError as e:
            # * If any patching activity fails, execute `SendFailureAlertActivity` and terminate.
            await workflow.execute_activity_method(
                activity=MyActivities.send_failure_alert_activity,
                arg=SendFailureAlertActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            raise e

        try:
            await workflow.execute_activity_method(
                activity=MyActivities.send_success_notification_activity,
                arg=SendSuccessNotificationActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
        except ActivityError:
            # TODO ignore ?
            pass
