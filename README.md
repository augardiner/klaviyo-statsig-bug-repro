### Overview
This repository contains two scripts that demonstrate different initialization patterns with Statsig in a forking environment. The `init-pre-fork.py` script initializes Statsig in the parent process before forking, while `init-post-fork.py` initializes Statsig in the child process after forking. Both scripts use a dummy API key and disable network connections to avoid external dependencies. 

The scripts create a parent and child process, with the child process sleeping for 3 seconds before exiting, and the parent process waiting for the child to complete. These scripts help illustrate potential issues that may arise when using Statsig with process forking.


### Setup
1. Install pyenv if necessary
```
brew install pyenv pyenv-virtualenv

eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
```
2. Activate new virtual environment
```
pyenv install 3.10.9
pyenv virtualenv 3.10.9 klaviyo-bug-repro
pyenv local klaviyo-bug-repro
```
3. Install statsig SDK
```
pip install \
"git+https://github.com/statsig-io/statsig-server-core.git@<commit-hash>#subdirectory=statsig-pyo3"
```
4. Run repro scripts
```
python init-pre-fork.py
python init-post-fork.py
```

### Findings
- `init-post-fork.py` will always run successfully
- `init-pre-fork.py` will hang, depending on SDK commit/version

In chronological order by commit:

1. [a86dc97](https://github.com/statsig-io/statsig-server-core/commit/a86dc976f561118aeb81b620a830127a149469be) - Success
```
pip install \
"git+https://github.com/statsig-io/statsig-server-core.git@a86dc97#subdirectory=statsig-pyo3" \
--force-reinstall
```
```
python init-pre-fork.py

out:
Initializing Statsig in parent...
Forking...
In parent process, waiting for child...
In child process, sleeping...
Child done.
Parent done.

Script complete.
```
```
python init-post-fork.py

out:
Forking...
In parent process, waiting for child...
Initializing Statsig in child...
In child process, sleeping...
Child done.
Parent done.

Script complete.
```
2. [e0e0ac55](https://github.com/statsig-io/statsig-server-core/commit/e0e0ac55ca6e51d3672fa40feed0493285d379c7) - Failure
```
pip install \
"git+https://github.com/statsig-io/statsig-server-core.git@e0e0ac55#subdirectory=statsig-pyo3" \
--force-reinstall
```
```
python init-pre-fork.py

out (while hung):
Initializing Statsig in parent...
Forking...
In parent process, waiting for child...
In child process, sleeping...
Child done.

thread '<unnamed>' panicked at /Users/alex.gardiner/Library/Caches/puccinialin/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/tokio-1.43.0/src/runtime/io/driver.rs:208:27:
failed to wake I/O driver: Os { code: 9, kind: Uncategorized, message: "Bad file descriptor" }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```
```
python init-post-fork.py

out:
Forking...
In parent process, waiting for child...
Initializing Statsig in child...
In child process, sleeping...
Child done.
Parent done.

Script complete.
```
3. [dfcc6426](https://github.com/statsig-io/statsig-server-core/commit/dfcc6426420f44ec3780a8ddd635995424d15f90) - Success
```
pip install \
"git+https://github.com/statsig-io/statsig-server-core.git@dfcc6426#subdirectory=statsig-pyo3" \
--force-reinstall
```
```
python init-pre-fork.py

out:
Initializing Statsig in parent...
Forking...
In parent process, waiting for child...
In child process, sleeping...
Child done.
Parent done.

Script complete.
```
```
python init-post-fork.py

out:
Forking...
In parent process, waiting for child...
Initializing Statsig in child...
In child process, sleeping...
Child done.
Parent done.

Script complete.
```

Here we see that the SDK was fork-safe at `a86dc97`, it lost fork-safety `e0e0ac55`, then was fork-safe again at `dfcc6426`.

Note the console output while hung on `e0e0ac55`:
```
thread '<unnamed>' panicked at /Users/alex.gardiner/Library/Caches/puccinialin/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/tokio-1.43.0/src/runtime/io/driver.rs:208:27:
failed to wake I/O driver: Os { code: 9, kind: Uncategorized, message: "Bad file descriptor" }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```
