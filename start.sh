#!/bin/bash

ovn-nbctl ls-add s1
ovn-nbctl lsp-add s1 s1-port1
#ovn-nbctl lsp-set-addresses s1-port1 00:00:00:00:00:01

ovn-nbctl lsp-add s1 s1-port2
#ovn-nbctl lsp-set-addresses s1-port2 00:00:00:00:00:02

ovn-nbctl lsp-add s1 s1-port3
#ovn-nbctl lsp-set-addresses s1-port3 00:00:00:00:00:03
ovn-nbctl lsp-add s1 s1-port4
ovn-nbctl lsp-add s1 s1-port5

ovs-vsctl add-port br-int p1 -- set Interface p1 external_ids:iface-id=s1-port1
ovs-vsctl add-port br-int p2 -- set Interface p2 external_ids:iface-id=s1-port2
ovs-vsctl add-port br-int p3 -- set Interface p3 external_ids:iface-id=s1-port3
ovs-vsctl add-port br-int p4 -- set Interface p4 external_ids:iface-id=s1-port4
ovs-vsctl add-port br-int p5 -- set Interface p5 external_ids:iface-id=s1-port5

#ovs-vsctl add-port br-int port1
#ovs-vsctl add-port br-int port2
#ovs-vsctl add-port br-int port3

ovs-ofctl mod-port br-int p1 up
ovs-ofctl mod-port br-int p2 up
ovs-ofctl mod-port br-int p3 up
ovs-ofctl mod-port br-int p4 up
ovs-ofctl mod-port br-int p5 up

ovs-vsctl set-controller br-int tcp:127.0.0.1

echo "------------------------------"
ovs-vsctl show
echo "------------------------------"
ovn-nbctl show
echo "------------------------------"

#sleep 1

ovs-appctl ofproto/trace br-int in_port=2,dl_src=00:00:00:00:00:02,dl_dst=ff:ff:ff:ff:ff:ff -generate
ovs-appctl ofproto/trace br-int in_port=3,dl_src=00:00:00:00:00:03,dl_dst=ff:ff:ff:ff:ff:ff -generate
ovs-appctl ofproto/trace br-int in_port=4,dl_src=00:00:00:00:00:04,dl_dst=ff:ff:ff:ff:ff:ff -generate

#ovs-appctl ofproto/trace br-int in_port=1,tcp,nw_src=10.0.0.1,nw_dst=10.0.0.2,tp_dst=80,dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02 -generate
#ovs-appctl ofproto/trace br-int in_port=1,dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:01 -generate
#ovs-appctl ofproto/trace br-int in_port=1,dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02 -generate
#ovs-appctl ofproto/trace br-int in_port=1,dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:03 -generate

#ovs-appctl ofproto/trace br-int in_port=2,dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01 -generate
#ovs-appctl ofproto/trace br-int in_port=2,dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:02 -generate
#ovs-appctl ofproto/trace br-int in_port=2,dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:03 -generate

#ovs-appctl ofproto/trace br-int in_port=3,dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:01 -generate
#ovs-appctl ofproto/trace br-int in_port=3,dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:02 -generate
#ovs-appctl ofproto/trace br-int in_port=3,dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:03 -generate
