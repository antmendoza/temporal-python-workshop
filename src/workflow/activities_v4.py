import asyncio
from datetime import datetime
from random import uniform

from temporalio import activity

from src.workflow.types import CheckPreconditionsActivityInput, VaultResponse, \
    VaultClientActivityInput, SendSuccessNotificationActivityInput, SendFailureAlertActivityInput, \
    CheckServiceHealthActivityInput, RunPostUpdateScriptsActivityInput, StartServicesActivityInput, \
    PerformUpdateActivityInput, RunPreUpdateScriptsActivityInput, WaitForWorkloadDrainActivityInput, \
    StopServicesActivityInput, SetMaintenanceModeActivityInput, RunPreDowntimeScriptsActivityInput, \
    SendStartNotificationActivityInput, CheckHostPreconditionsActivityInput, GetClusterHostsActivityInput, \
    SendApprovalRequestActivityInput, SendFinalSuccessNotificationActivityInput, GetClusterHostsActivityOutput, \
    CheckHostPreconditionsActivityOutput, MyVaultClient


def activities(vault_client):
    my_activities = MyActivities(vault_client)

    return [
        my_activities.send_approval_request_activity,
        my_activities.vault_client_activity,
        my_activities.get_cluster_hosts_activity,
        my_activities.check_host_preconditions_activity,
        my_activities.run_post_update_scripts_activity,
        my_activities.run_pre_downtime_scripts_activity,
        my_activities.run_pre_update_scripts_activity,
        my_activities.perform_update_activity,
        my_activities.send_failure_alert_activity,
        my_activities.send_final_success_notification_activity,
        my_activities.send_start_notification_activity,
        my_activities.send_success_notification_activity,
        my_activities.check_service_health_activity,
        my_activities.set_maintenance_mode_activity,
        my_activities.stop_services_activity,
        my_activities.start_services_activity,
        my_activities.wait_for_workload_drain_activity,
    ]


class MyActivities:
    def __init__(self, client: MyVaultClient) -> None:
        self.client = client

    @activity.defn
    async def check_preconditions_activity(self, activity_input: CheckPreconditionsActivityInput) -> bool:
        await self.simulate_activity_execution()

        # Simulate a failure for the first attempt
        if activity.info().attempt == 1 and activity_input.clusterName == "cluster2":
            raise Exception("Simulated failure in check_preconditions_activity")

        return True

    @activity.defn
    async def vault_client_activity(self, activity_input: VaultClientActivityInput) -> VaultResponse:
        await self.simulate_activity_execution()

        return VaultResponse()

    @activity.defn
    async def send_approval_request_activity(self, activity_input: SendApprovalRequestActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def get_cluster_hosts_activity(self,
                                         activity_input: GetClusterHostsActivityInput) -> GetClusterHostsActivityOutput:
        await self.simulate_activity_execution()

        cluster = activity_input.targetCluster

        # Simulate a failure for the first attempt
        if activity.info().attempt == 1 and cluster == "cluster1":
            raise Exception("Simulated failure in get_cluster_hosts_activity")

        return GetClusterHostsActivityOutput([cluster + "_host1",
                                              cluster + "_host2",
                                              cluster + "_host3",
                                              cluster + "_host4",
                                              cluster + "_host5"])

    @activity.defn
    async def check_host_preconditions_activity(self,
                                                activity_input: CheckHostPreconditionsActivityInput) -> CheckHostPreconditionsActivityOutput:
        await self.simulate_activity_execution()
        return CheckHostPreconditionsActivityOutput(True, "ssh-private-key")

    @activity.defn
    async def send_start_notification_activity(self, activity_input: SendStartNotificationActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def run_pre_downtime_scripts_activity(self, activity_input: RunPreDowntimeScriptsActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def set_maintenance_mode_activity(self, activity_input: SetMaintenanceModeActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def stop_services_activity(self, activity_input: StopServicesActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def wait_for_workload_drain_activity(self, activity_input: WaitForWorkloadDrainActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def run_pre_update_scripts_activity(self, activity_input: RunPreUpdateScriptsActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def perform_update_activity(self, activity_input: PerformUpdateActivityInput) -> bool:

        #activity.logger.info("***Starting perform_update_activity***")


        # Exersice 3.1 Start to close timeout
        #await asyncio.sleep(11)


        # Init Exersice 3.2 Heartbeat
        # details = activity.info().heartbeat_details
        # init = 1
        # if details:
        #     init = int(details[0])
        # for i in range(init, 9):
        #     heartbeat_info = str(i)
        #     activity.logger.info("****about to heartbeat :" + heartbeat_info)
        #     activity.heartbeat(heartbeat_info)
        #     await asyncio.sleep(1)
        # End Exersice 3.2 Heartbeat



        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def start_services_activity(self, activity_input: StartServicesActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def run_post_update_scripts_activity(self, activity_input: RunPostUpdateScriptsActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def check_service_health_activity(self, activity_input: CheckServiceHealthActivityInput) -> bool:
        await self.simulate_activity_execution()

        # Simulate a health check failure
        if activity_input.hostname == "cluster1_host1" and activity.info().attempt == 1:
            raise Exception("Service health check failed: " + str(activity_input))

        return True

    @activity.defn
    async def send_success_notification_activity(self, activity_input: SendSuccessNotificationActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def send_failure_alert_activity(self, activity_input: SendFailureAlertActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    @activity.defn
    async def send_final_success_notification_activity(self,
                                                       activity_input: SendFinalSuccessNotificationActivityInput) -> bool:
        await self.simulate_activity_execution()
        return True

    async def simulate_activity_execution(self, min_execution_time_seconds: float = 0.1,
                                          max_execution_time_seconds: float = 0.5):
        # randon sleep to simulate activity execution
        await asyncio.sleep(uniform(min_execution_time_seconds, max_execution_time_seconds))
