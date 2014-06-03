crm_cluster
========

This role provides an automated creation/update/removal of Pacemaker clusters
for Debian (squeeze/wheeze) systems.

Requirements
------------

The role was tested using Ansible 1.5 and higher.

Role Variables
--------------

There are some mandatory variables:
- *crm_lsb_service_name* - name of the LSB service that is going to be managed
    by Pacemaker
- *crm_vip_prefix* - /24 IP network assigned for VIP assignement to particular
    market or role
- *crm_vip_range.begin, crm_vip_range.end* - role-specific range of indexes
    for the service translated directly to 4th octet of the VIP
- *crm_vip_index* - role-specific index of the service translated directly
    to 4th octet of the VIP
- *crm_preffered_location* - preffered location where the VIP should run.

    Whether one or more of theese variables are required or not varies greatly
on the the cluster template used. I.E. a *multi_vip_multi_service* cluster does
not require *crm_vip_index* variable but *crm_vip_range.begin, crm_vip_range.end*.
OTOH a plain single-service per market cluster requires *crm_vip_index* and
*crm_lsb_service_name*. All of them require *crm_vip_prefix*. Please check the
contents of files in *templates/* directory for more details.

Finally, there are variables which manage the role itself. Depending on the
templates used, it is possible to enable more that one at the same time and
achive a cluster that performs multiple functions:

- *single_vip_single_service* - configure a cluster where a single VIP is tied
    to a service. Service should not be active when VIP is not present on the
    host. This setup is preffered for i.e. for memcache clusters where the risk
    of stale data permits for only one active daemon at the time.
- *single_vip_multi_service* - configure a cluster where a single VIP is tied
    to a service. Service should be active on all hosts. This role is suited
    for i.e. mail gateways. All postfix instances should be up, whereas the
    VIP address, which clients use for connecting, is floating betwean them.
- *multi_vip_multi_service* - a cluster where each instance of the service has
    it's own VIP. In case of a failure, VIP is migrated away to other host, and
    the service there starts handling two VIPs.

By default they are all set to *False*.

Dependencies
------------

This role requires a Corosync&Pacemaker stack provided *crm_base* role.

It is also important to remember that some of the templates are using other
templates as a base/dependency in order to avoid code duplication. Please see
template headers for more information.

Example Playbook
-------------------------

Applying the role is straightforward:

```
- hosts: front
  roles:
    - crm_base
    - { role: crm_cluster, single_vip_single_service_cluster: True}
```

Monitoring
-------------------------
The *single_vip_single_service* cluster by design stops all other services where
the VIP is not running. It poses some difficulties with monitoring, so a quick
fix is provided. In *files/* direcotry there is a plugin wrapper
*resource_locate.py* which returns OK status if the service is active on other
host. Usage is as follows:

```
resource_locate.py <resource name> <nagios check executable> <nagios check args>

command[check_memcache_socket]=/opt/resource_locate.py  crm_memcache_vip /usr/lib/nagios/plugins/check_tcp -H localhost -p 11211

```

Adding new cluster types
-------------------------
Clusters provided are generic and their use is limited. In real life
scenarios more personalized clusters may be required (inc. custom resource
agents).

It should be easy to add new cluster types by adding new variables which in turn
control specialized tasks. These tasks will simply assemble required configuration
reusing some of the existing cluster configuration snippets and introducing new
ones.

I.E. In case of custom Master-Slave setup with dedicated OCF agent, one can:
- reuse single VIP per service config snippet
- add additionall snippet which sets up master-slave resource
- add location constraint that will bind VIP and master-slave resource together

License
-------

Copyright 2014 Zadane.pl sp. z o.o.

Copyright 2014 Pawel Rozlach

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this role except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Author Information
------------------

This role has been created by Pawel Rozlach during the work time and spare time
at Zadane.pl and then opensourced by the company.
