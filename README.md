# Fast App

This application is an aggregator of [FastQC`](https://github.com/s-andrews/FastQC), [Fastp](https://github.com/OpenGene/fastp) and [HybPiper](https://github.com/mossmatters/HybPiper). It abstract those CLI applications to a simple easy to use interface to streamline research efforts.

## Installation

TODO

## Local Development

In case you want to contribute to the project, you can follow the steps below:

* Install [Git](https://git-scm.com/downloads).

* Clone the repository: `git clone git@github.com:danielmapar/fast.git`

* For **Windows users only**:
    * Disable Hyper-V by running `bcdedit /set hypervisorlaunchtype off` as administrator.
    * Reboot your machine.

* Install [Virtual Box](https://download.virtualbox.org/virtualbox/7.0.22/) version `7.0.22`.
  * Be mindful with version `7.1.x` as it presenting many networking issues. More [here](https://forums.virtualbox.org/viewtopic.php?t=112405).
  
* Install [Vagrant](https://developer.hashicorp.com/vagrant/downloads).

* Install the `vagrant-vbguest` plugin:
  * `vagrant plugin install vagrant-vbguest`
    * This plugin is used to install the correct version of VirtualBox Guest Additions. Otherwise, you may encounter issues with the shared folder, latency, and other issues.

* Run `vagrant up --provision`.

* Run `vagrant ssh` to get inside the VM afterwards.
