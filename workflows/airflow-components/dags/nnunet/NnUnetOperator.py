from kaapana.kubetools.volume_mount import VolumeMount
from kaapana.kubetools.volume import Volume
from kaapana.kubetools.resources import Resources as PodResources
from kaapana.operators.KaapanaBaseOperator import KaapanaBaseOperator, default_registry, default_project
from datetime import timedelta
import os
import json


class NnUnetOperator(KaapanaBaseOperator):
    execution_timeout = timedelta(days=2)
    task_dict = {}

    def __init__(self,
                 dag,
                 mode,
                 processes_low=1,
                 processes_full=1,
                 folds=5,
                 nifti_input_operators=[],
                 dicom_input_operators=[],
                 label_operator=None,
                 train_config="nnUNetTrainerV2",
                 preprocess="true",
                 preparation="true",
                 check_integrity="true",
                 env_vars={},
                 execution_timeout=execution_timeout,
                 *args,
                 **kwargs
                 ):
        # Task042_LiverTest
        envs = {
            "INPUT_NIFTI_DIRS": ";".join(str(dir.operator_out_dir) for dir in nifti_input_operators),
            "INPUT_DICOM_DIRS": ";".join(str(dir.operator_out_dir) for dir in dicom_input_operators),
            "LABEL_DIR": str(label_operator.operator_out_dir) if label_operator is not None else "",
            "MODE": str(mode),
            "PL": str(processes_low),
            "PF": str(processes_full),
            "FOLDS": str(folds),
            "TRAIN_CONFIG": train_config,
            "CHECK_INTEGRITY": check_integrity,
            "PREPROCESS": preprocess,
            "PREPARATION": preparation,
            "TENSORBOARD_DIR": '/tensorboard',
        }
        env_vars.update(envs)

        data_dir = os.getenv('DATADIR', "")
        models_dir = os.path.join(os.path.dirname(data_dir), "models")

        volume_mounts = []
        volumes = []

        volume_mounts.append(VolumeMount(
            'models', mount_path='/models', sub_path=None, read_only=False))
        volume_config = {
            'hostPath':
            {
                'type': 'DirectoryOrCreate',
                'path': models_dir
            }
        }
        volumes.append(Volume(name='models', configs=volume_config))

        volume_mounts.append(VolumeMount(
            'dshm', mount_path='/dev/shm', sub_path=None, read_only=False))
        volume_config = {
            'emptyDir':
            {
                'medium': 'Memory',
            }
        }
        volumes.append(Volume(name='dshm', configs=volume_config))

        pod_resources = PodResources(request_memory=None, request_cpu=None, limit_memory=None, limit_cpu=None, limit_gpu=1) if mode == "training" or mode == "inference" else None
        gpu_mem_mb = 5000 if mode == "training" or mode == "inference" else None

        super().__init__(
            dag=dag,
            image="{}{}/nnunet:1.6.5-vdev".format(default_registry, default_project),
            name="nnunet",
            image_pull_secrets=["registry-secret"],
            volumes=volumes,
            volume_mounts=volume_mounts,
            execution_timeout=execution_timeout,
            ram_mem_mb=10000,
            ram_mem_mb_lmt=10000,
            gpu_mem_mb=gpu_mem_mb,
            pod_resources=pod_resources,
            training_operator=True if mode == "training" else False,
            env_vars=env_vars,
            *args,
            **kwargs
        )
