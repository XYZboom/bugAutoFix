import os
import subprocess


def run_psi_ref_extract(_input, _output):
    _out = subprocess.Popen([
        r"java",
        "-Xms4g", "-Xmx4g",
        "-jar",
        r"/home/xyzboom/Shared/Temp/cli-runner-1.0.0-SNAPSHOT-all.jar",
        _input,
        "-o", _output,
        "-ff", "json",
        "-eu",
        "-g", "all",
        "-ef", "leaf-text-and-qualified-name"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _out.stdout.read()

defects4j = "/home/xyzboom/Shared/Code/Java/BugAutoFix/GrowingBugRepository/framework/bin/defects4j"

def exec_command(_cmd: str) -> subprocess.Popen:
    return subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def run_command(_cmd: str):
    return subprocess.run(_cmd, shell=True)

out_dir = "/home/xyzboom/Shared/Temp"

too_long_project = [
    'Appformer_uberfire_commons_editor_backend',
    'Appformer_uberfire_security_management_client',
    'Appformer_uberfire_workbench_client'
]

if __name__ == '__main__':
    processed = set([i.replace("-all.json", "") for i in os.listdir("/home/xyzboom/Shared/Temp/psi_data")])
    out = exec_command(f"{defects4j} pids", )
    all_project = out.stdout.read().decode().strip().splitlines()
    print(all_project)
    for project in all_project:
        if project in too_long_project:
            continue
        out = exec_command(f"{defects4j} bids -p {project}")
        all_bids = out.stdout.read().decode().strip().splitlines()
        for bid in all_bids:
            for bf in ['b', 'f']:
                pbid = f"{project}_{bid}{bf}"
                if pbid in processed:
                    print(f"processed {pbid}, passing")
                    continue
                print(f"check out {pbid}")
                out = run_command(f"{defects4j} checkout -p {project} -v {bid}{bf} -w {out_dir}/{pbid}")
                # out = exec_command(f"{defects4j} checkout -p {project} -v {bid}{bf} -w {out_dir}/{pbid}")
                # result = out.stdout.read().decode()
                # result1 = out.stdout.read().decode()
                # if "FAIL" in result or "FAIL" in result1:
                #     print(result, result1)
                #     continue
                print("run psi on project")
                run_psi_ref_extract(f"{out_dir}/{pbid}", f"{out_dir}/psi_data/{pbid}")
                print("delete temp files")
                run_command(f"rm -rf {out_dir}/{pbid}")