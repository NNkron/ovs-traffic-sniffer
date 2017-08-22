from ryu.base import app_manager
from ryu.ofproto import ofproto_parser
from ryu.ofproto.ofproto_parser import ofp_instruction_from_jsondict
from ryu.lib.ofctl_string import ofp_instruction_from_str
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

class ExampleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    port_to_proto = {20: 'FTP', 21: 'FTP', 22: 'SSH', 23: 'Telnet', 80: 'HTTP'}

    def __init__(self, *args, **kwargs):
        super(ExampleSwitch13, self).__init__(*args, **kwargs)
        # initialize mac address table.
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        actions = ofproto_parser.ofp_instruction_from_jsondict(datapath, ofp_instruction_from_str(ofproto, 'drop'))
        match = parser.OFPMatch(eth_dst='00:00:00:00:00:00')
        self.add_flow(datapath, 4, match, actions, 0)

        actions = [parser.NXActionResubmitTable(table_id=1)]
        match = parser.OFPMatch(ip_proto=0x06, eth_type=0x0800)
        self.add_flow(datapath, 2, match, actions, 0)

        actions = [parser.NXActionResubmitTable(table_id=2)]
        match = parser.OFPMatch()
        self.add_flow(datapath, 1, match, actions, 0)

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions, 2)

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions, 1)

    def add_flow(self, datapath, priority, match, actions, id, time=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst, table_id=id,
                                hard_timeout=time)
        datapath.send_msg(mod)

    def send_out(self, parser, datapath, ofproto, in_port, actions, msg):
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
        datapath.send_msg(out)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        print self.mac_to_port
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # get Datapath ID to identify OpenFlow switches.
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # analyse the received packets using the packet library.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        # get the rece ived port number from packet_in message.
        in_port = msg.match['in_port']

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        pkt_tcp = pkt.get_protocols(tcp.tcp)
        if pkt_tcp:
            if pkt_tcp[0].dst_port in self.port_to_proto:
                actions = [parser.OFPActionOutput(1), parser.OFPActionOutput(5)]
                match = parser.OFPMatch(ip_proto=0x06, eth_type=0x0800, tcp_dst=pkt_tcp[0].dst_port)
                self.add_flow(datapath, 2, match, actions, 1)

                if dst not in self.mac_to_port[dpid]:
                    self.send_out(parser, datapath, ofproto, in_port, actions, msg)

                for i, y in self.mac_to_port[dpid].items():
                    actions = [parser.OFPActionOutput(y), parser.OFPActionOutput(5)]
                    match = parser.OFPMatch(eth_dst=i, ip_proto=0x06, eth_type=0x0800, tcp_dst=pkt_tcp[0].dst_port)
                    self.add_flow(datapath, 3, match, actions, 0)

                    if i == dst:
                        self.send_out(parser, datapath, ofproto, in_port, actions, msg)

            else:
                actions = [parser.OFPActionOutput(1), parser.OFPActionOutput(5)]
                match = parser.OFPMatch(ip_proto=0x06, eth_type=0x0800, tcp_dst=pkt_tcp[0].dst_port)
                self.add_flow(datapath, 1, match, actions, 1, 10)
                
                if dst not in self.mac_to_port[dpid]:
                    self.send_out(parser, datapath, ofproto, in_port, actions, msg)

                for i, y in self.mac_to_port[dpid].items():
                    actions = [parser.OFPActionOutput(y), parser.OFPActionOutput(5)]
                    match = parser.OFPMatch(eth_dst=i, ip_proto=0x06, eth_type=0x0800, tcp_dst=pkt_tcp[0].dst_port)
                    self.add_flow(datapath, 3, match, actions, 0)
                    
                    if i == dst:
                        self.send_out(parser, datapath, ofproto, in_port, actions, msg)

        elif dst != 'ff:ff:ff:ff:ff:ff':
            actions = [parser.OFPActionOutput(1)]
            match = parser.OFPMatch()
            self.add_flow(datapath, 1, match, actions, 2)
            
            if dst not in self.mac_to_port[dpid]:
                self.send_out(parser, datapath, ofproto, in_port, actions, msg)
            
            for i, y in self.mac_to_port[dpid].items():
                actions = [parser.OFPActionOutput(y)]
                match = parser.OFPMatch(eth_dst=i)
                self.add_flow(datapath, 2, match, actions, 2)
                
                if i == dst:
                    self.send_out(parser, datapath, ofproto, in_port, actions, msg)
