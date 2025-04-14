import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import List

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError

from src.workflow.activities import MyActivities
from src.workflow.types import SystemPatchWorkflowInput, SendApprovalRequestActivityInput, VaultClientActivityInput, \
    GetClusterHostsActivityInput, CheckHostPreconditionsActivityInput, SendSuccessNotificationActivityInput, \
    SendFailureAlertActivityInput, RunPreDowntimeScriptsActivityInput, \
    SetMaintenanceModeActivityInput, StopServicesActivityInput, WaitForWorkloadDrainActivityInput, \
    RunPreUpdateScriptsActivityInput, PerformUpdateActivityInput, StartServicesActivityInput, \
    RunPostUpdateScriptsActivityInput, CheckServiceHealthActivityInput, SendFinalSuccessNotificationActivityInput


@workflow.defn
class SystemPatchWorkflow_V6:
    def __init__(self):
        self.wf_input: SystemPatchWorkflowInput = None
        self.approval_request_received = False
        self.completed_steps = []

    @workflow.run
    async def run(self, wf_input: SystemPatchWorkflowInput) -> str:
        self.wf_input = wf_input

        workflow.logger.info("Workflow starts ")

        # 2. Execute `SendApprovalRequestActivity`.

        await self.send_approval_request_activity()
        self.completed_steps.append("send_approval_request_activity")

        try:
            # wait for approval
            await workflow.wait_condition(
                lambda: self.approval_request_received,
                # 2.1 If not approved, terminate.
                # considered "not approved" if the signal is not received within x seconds
                timeout=timedelta(seconds=5)
            )
        except asyncio.TimeoutError as e:
            # If not approved, terminate.
            # https://github.com/temporalio/sdk-python/issues/798
            raise ApplicationError("Approval requested not received") from e

        self.completed_steps.append("approval_request_received")

        # 3. Execute `VaultClientActivity`.
        vault_client_response = await self.vault_client_activity()

        self.completed_steps.append("vault_client_activity")

        clusters = wf_input.targetClusters
        workflow.logger.info("target_clusters %s", clusters)

        # 4. For each `targetCluster`:
        # for target_cluster in clusters:
        #    await self._process_target_cluster(target_cluster)
        #    self.completed_steps.append("_process_target_cluster " +  target_cluster)
        tasks = [self._process_target_cluster(target_cluster) for target_cluster in clusters]
        await asyncio.gather(*tasks)

        await self.send_final_success_notification_activity()
        self.completed_steps.append("send_final_success_notification_activity")

        workflow.logger.info("About to complete workflow")

        return "your output"

    @workflow.signal
    def approve_request(self):
        self.approval_request_received = True

    @workflow.query
    def get_completed_steps(self) -> List[str]:
        return self.completed_steps

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
        return await workflow.execute_child_workflow(
            SystemPatchWorkflow_Cluster_V6.run,
            SystemPatchWorkflow_ClusterInput(
                targetCluster=target_cluster,
                pilotHostCount=self.wf_input.pilotHostCount
            ),
            id="SystemPatchWorkflow_Cluster_V6-target_cluster:" + target_cluster,
        )


@dataclass
class SystemPatchWorkflow_ClusterInput:
    targetCluster: str
    pilotHostCount: int


@workflow.defn
class SystemPatchWorkflow_Cluster_V6:

    def __init__(self):
        self.wf_input: SystemPatchWorkflowInput = None

    @workflow.run
    async def run(self, wf_input: SystemPatchWorkflow_ClusterInput) -> None:
        self.wf_input = wf_input

        #  Get cluster hosts using `GetClusterHostsActivity`.
        get_cluster_hosts_response = await workflow.execute_activity_method(
            activity=MyActivities.get_cluster_hosts_activity,
            arg=GetClusterHostsActivityInput(
                targetCluster=wf_input.targetCluster,
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

        await self._process_hosts(pilot_hosts)


    async def _process_remaining_hosts(self, remaining_hosts: List[str]):
        workflow.logger.debug("processing remaining hosts %s", remaining_hosts)


        await self._process_hosts(remaining_hosts)


    async def _process_hosts(self, hosts):
        tasks = [self._process_host(host) for host in hosts]
        await asyncio.gather(*tasks)


    async def _process_host(self, host):
        return await workflow.execute_child_workflow(
            SystemPatchWorkflow_Host_V6.run,
            SystemPatchWorkflow_HostInput(
                host=host,
            ),
            id="SystemPatchWorkflow_Host_V6-host:" + host,
        )


@dataclass
class SystemPatchWorkflow_HostInput:
    host: str


@workflow.defn
class SystemPatchWorkflow_Host_V6:

    def __init__(self):
        self.wf_input: SystemPatchWorkflow_HostInput = None

    @workflow.run
    async def run(self, wf_input: SystemPatchWorkflow_HostInput) -> None:
        self.wf_input = wf_input
        host = wf_input.host

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

            await workflow.execute_activity_method(
                activity=MyActivities.set_maintenance_mode_activity,
                arg=SetMaintenanceModeActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            await workflow.execute_activity_method(
                activity=MyActivities.stop_services_activity,
                arg=StopServicesActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            await workflow.execute_activity_method(
                activity=MyActivities.wait_for_workload_drain_activity,
                arg=WaitForWorkloadDrainActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            await workflow.execute_activity_method(
                activity=MyActivities.run_pre_update_scripts_activity,
                arg=RunPreUpdateScriptsActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            await workflow.execute_activity_method(
                activity=MyActivities.perform_update_activity,
                arg=PerformUpdateActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=10),
                heartbeat_timeout=timedelta(seconds=2),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            await workflow.execute_activity_method(
                activity=MyActivities.start_services_activity,
                arg=StartServicesActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            await workflow.execute_activity_method(
                activity=MyActivities.run_post_update_scripts_activity,
                arg=RunPostUpdateScriptsActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            await workflow.execute_activity_method(
                activity=MyActivities.run_post_update_scripts_activity,
                arg=RunPostUpdateScriptsActivityInput(
                    hostname=host,
                    # ...
                ),
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

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
