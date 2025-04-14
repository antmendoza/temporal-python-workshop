from dataclasses import dataclass, field
from typing import List, Optional


class MyVaultClient:
    async def do_something(self) -> None:
        print("doing something...")


@dataclass
class VaultResponse:
    address: str = "address"
    token: str = "default-token"


@dataclass
class DeployPostgresClusterWorkflowInput:
    clusterName: str = "default-cluster"
    version: str = "latest"
    nodeCount: int = 1
    cpuCoresPerNode: int = 2
    memoryGBPerNode: int = 4
    storageGBPerNode: int = 50
    openstackProject: str = "default-project"
    approverEmails: List[str] = field(default_factory=list)
    requesterEmail: str = "default@example.com"
    vaultAddress: str = "https://vault.example.com:8200"
    vaultToken: str = "default-token"
    secretPathPrefix: str = "default-prefix"


@dataclass
class CheckPreconditionsActivityInput:
    clusterName: str = "default-cluster"
    nodeCount: int = 1
    cpuCoresPerNode: int = 2
    memoryGBPerNode: int = 4
    storageGBPerNode: int = 50
    approverEmails: List[str] = field(default_factory=list)
    requesterEmail: str = "default@example.com"


@dataclass
class VaultClientActivityInput:
    vaultAddress: str = "https://vault.example.com:8200"


@dataclass
class ProvisionVirtualMachinesActivityInput:
    clusterName: str = "default-cluster"
    nodeCount: int = 1
    cpuCoresPerNode: int = 2
    memoryGBPerNode: int = 4
    storageGBPerNode: int = 50
    openstackProject: str = "default-project"


@dataclass
class InstallPostgresSoftwareActivityInput:
    vmAddresses: List[str] = field(default_factory=list)
    version: str = "latest"
    vaultClient: VaultResponse = field(default_factory=VaultResponse)
    sshKeyPaths: dict = field(default_factory=dict)


@dataclass
class ConfigurePostgresClusterActivityInput:
    vmAddresses: List[str] = field(default_factory=list)
    clusterName: str = "default-cluster"
    vaultClient: VaultResponse = field(default_factory=VaultResponse)
    adminPasswordPath: str = "default-admin-password-path"


@dataclass
class PerformInitialBackupActivityInput:
    vmAddresses: List[str] = field(default_factory=list)
    clusterName: str = "default-cluster"
    vaultClient: VaultResponse = field(default_factory=VaultResponse)


@dataclass
class NotifyDeploymentCompletionActivityInput:
    clusterName: str = "default-cluster"
    vmAddresses: List[str] = field(default_factory=list)
    requesterEmail: str = "default@example.com"
    vaultClient: VaultResponse = field(default_factory=VaultResponse)
    userCredentialsPaths: dict = field(default_factory=dict)
    adminPasswordPath: str = "default-admin-password-path"
    backupMetadataPath: str = "default-backup-metadata-path"


@dataclass
class HandleFailureActivityInput:
    clusterName: str = "default-cluster"
    requesterEmail: str = "default@example.com"
    failureDetails: str = "default-failure-details"
    vaultClient: VaultResponse = field(default_factory=VaultResponse)




# SystemPatchWorkflow

@dataclass
class SystemPatchWorkflowInput:
    targetClusters: List[str] = field(default_factory=list)
    pilotHostCount: int = 0
    approverEmails: List[str] = field(default_factory=list)
    requesterEmail: str = "default@example.com"
    vaultAddress: str = "https://vault.example.com:8200"
    vaultToken: str = "default-token"
    secretPathPrefix: str = "default-prefix"
    updateCommand: str = "default-update-command"
    serviceList: List[str] = field(default_factory=list)

@dataclass
class SendApprovalRequestActivityInput:
    targetClusters: List[str] = field(default_factory=list)
    approverEmails: List[str] = field(default_factory=list)
    requesterEmail: str = "default@example.com"



@dataclass
class GetClusterHostsActivityInput:
    targetCluster: str = "default-cluster"



@dataclass
class GetClusterHostsActivityOutput:
    hostnames: List[str] = field(default_factory=list)



@dataclass
class CheckHostPreconditionsActivityInput:
    hostname: str = "default-hostname"



@dataclass
class CheckHostPreconditionsActivityOutput:
    preconditionsMet: bool = False
    sshPrivateKey: str = "default-ssh-key"



@dataclass
class SendStartNotificationActivityInput:
    hostname: str = "default-hostname"
    requesterEmail: str = "default@example.com"



@dataclass
class RunPreDowntimeScriptsActivityInput:
    hostname: str = "default-hostname"



@dataclass
class SetMaintenanceModeActivityInput:
    hostname: str = "default-hostname"



@dataclass
class StopServicesActivityInput:
    hostname: str = "default-hostname"
    serviceList: List[str] = field(default_factory=list)



@dataclass
class WaitForWorkloadDrainActivityInput:
    hostname: str = "default-hostname"



@dataclass
class RunPreUpdateScriptsActivityInput:
    hostname: str = "default-hostname"
    preUpdateScripts: Optional[List[str]] = None



@dataclass
class PerformUpdateActivityInput:
    hostname: str = "default-hostname"
    updateCommand: str = "default-update-command"



@dataclass
class StartServicesActivityInput:
    hostname: str = "default-hostname"
    serviceList: List[str] = field(default_factory=list)



@dataclass
class RunPostUpdateScriptsActivityInput:
    hostname: str = "default-hostname"
    postUpdateScripts: Optional[List[str]] = None



@dataclass
class CheckServiceHealthActivityInput:
    hostname: str = "default-hostname"
    serviceList: List[str] = field(default_factory=list)






@dataclass
class SendSuccessNotificationActivityInput:
    hostname: str = "default-hostname"
    requesterEmail: str = "default@example.com"



@dataclass
class SendFinalSuccessNotificationActivityInput:
    pass

@dataclass
class SendFailureAlertActivityInput:
    hostname: str = "default-hostname"
    failureDetails: str = "default-failure-details"
    requesterEmail: str = "default@example.com"
