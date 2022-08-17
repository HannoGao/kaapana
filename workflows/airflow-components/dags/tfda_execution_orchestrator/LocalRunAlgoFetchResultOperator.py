import os
import glob
import zipfile
import logging
import subprocess
from subprocess import PIPE
from kaapana.operators.KaapanaPythonBaseOperator import KaapanaPythonBaseOperator
from kaapana.blueprints.kaapana_global_variables import BATCH_NAME, WORKFLOW_DIR


class LocalRunAlgoFetchResultOperator(KaapanaPythonBaseOperator):
    def start(self, ds, ti, **kwargs):
        print("Run algorithm in isolated environment and fetch the results...")
        operator_dir = os.path.dirname(os.path.abspath(__file__))
        results_path = os.path.join(operator_dir, "results")
        playbooks_dir = os.path.join(operator_dir, "ansible_playbooks")        
        playbook_path = os.path.join(playbooks_dir, "run_algo_fetch_result.yaml")
        
        if not os.path.isfile(playbook_path):
            raise AirflowFailException("Playbook yaml file not found!")
        
        iso_env_ip = ti.xcom_pull(key="iso_env_ip", task_ids="create-iso-inst")

        playbook_args = f"target_host={iso_env_ip} remote_username=ubuntu results_path={results_path}"
        command = ["ansible-playbook", playbook_path, "--extra-vars", playbook_args]
        process = subprocess.Popen(command, stdout=PIPE, stderr=PIPE, encoding="Utf-8")
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        if rc == 0:
            logging.info(f"Algorithm ran successfully and results were fetched!!")
        else:
            raise AirflowFailException("Playbook FAILED! Cannot proceed further...")


    def __init__(self,
                 dag,
                 **kwargs):

        super().__init__(
            dag=dag,
            name="run-algo-fetch-results",
            python_callable=self.start,
            **kwargs
        )
