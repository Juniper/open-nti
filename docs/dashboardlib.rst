..  _dashboard_lib:

Dashboard Library
========================

Graphs
-------

.. raw:: html

    <table style="width:100%;white-space:normal;" border=1 class="docutils jnpr-table" >
      <thead>
        <tr>
           <th class="jnpr-name">Graph</th>
           <th class="jnpr-desc">File</th>
        </tr>
      <thead>
      <tbody>

        <tr>
          <td class="jnpr-name">BGP group-count</td>
          <td class="jnpr-desc">bgp-group-count.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">BGP peer-count</td>
          <td class="jnpr-desc">bgp-peer-count.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">BGP down-peer-count</td>
          <td class="jnpr-desc">bgp-peer-down-count.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">CPU Memory - Bytes allocated</td>
          <td class="jnpr-desc">cpumem-bytes.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">CPU Memory - Size</td>
          <td class="jnpr-desc">cpumem-size.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">CPU Memory - Utilization</td>
          <td class="jnpr-desc">cpumem-utilization.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Firewall Filter Counter - Bytes</td>
          <td class="jnpr-desc">fw-counter-bytes.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Firewall Filter Counter - Packets</td>
          <td class="jnpr-desc">fw-counter-packets.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Firewall Filter Memory Usage</td>
          <td class="jnpr-desc">fw-memory.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Traffic Statistics (BPS)</td>
          <td class="jnpr-desc">int-bps.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Buffer Latency</td>
          <td class="jnpr-desc">int-buffer-latency.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Buffer Utilization</td>
          <td class="jnpr-desc">int-buffer-size.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interface Error Statistics</td>
          <td class="jnpr-desc">int-error.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Traffic Packet Count</td>
          <td class="jnpr-desc">int-packets.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Aggregated TX/RX (PPS)</td>
          <td class="jnpr-desc">int-pps-aggr.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Broadcast/Multicast/Unicast Interface Traffic</td>
          <td class="jnpr-desc">int-pps-ucast-bcast-mcast.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Traffic Statistics (PPS)</td>
          <td class="jnpr-desc">int-pps.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interface Queue Stats</td>
          <td class="jnpr-desc">int-queue-stat.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS fragments-rebuilt (delta)</td>
          <td class="jnpr-desc">isis-fragment-rebuilt.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS LSP regenerations (delta)</td>
          <td class="jnpr-desc">isis-lsp-regeneration-run.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS Total packets-dropped (delta)</td>
          <td class="jnpr-desc">isis-packet-total-dropped.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS Total packets-processed (delta)</td>
          <td class="jnpr-desc">isis-packet-total-processed.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS Total packets-received (delta)</td>
          <td class="jnpr-desc">isis-packet-total-received.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS Total packets-retransmitted (delta)</td>
          <td class="jnpr-desc">isis-packet-total-retransmit.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS Total packets-sent (delta)</td>
          <td class="jnpr-desc">isis-packet-total-sent.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS spf-runs (delta)</td>
          <td class="jnpr-desc">isis-spf-run.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Traffic Statistics (BPS)</td>
          <td class="jnpr-desc">jti-oc-int-bps.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Queue Traffic Statistics (BPS)</td>
          <td class="jnpr-desc">jti-oc-queue-bps.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">LSP Traffic Rate (BPS)</td>
          <td class="jnpr-desc">mpls-lsp-traffic-bps.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">LSP Traffic Rate (PPS)</td>
          <td class="jnpr-desc">mpls-lsp-traffic-pps.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">RE - CPU idle</td>
          <td class="jnpr-desc">re-cpu-idle.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">COSD SIZE</td>
          <td class="jnpr-desc">re-memory-cosd.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">DCD SIZE</td>
          <td class="jnpr-desc">re-memory-dcd.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">DFWD SIZE</td>
          <td class="jnpr-desc">re-memory-dfwd.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">MIB2D SIZE</td>
          <td class="jnpr-desc">re-memory-mib2d.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">RPD SIZE</td>
          <td class="jnpr-desc">re-memory-rpd.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">SAMPLED SIZE</td>
          <td class="jnpr-desc">re-memory-sampled.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">SMID SIZE</td>
          <td class="jnpr-desc">re-memory-smid.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">SMI-HELPER SIZE</td>
          <td class="jnpr-desc">re-memory-smihelperd.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">SNMPD SIZE</td>
          <td class="jnpr-desc">re-memory-snmpd.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">RE - CPU idle</td>
          <td class="jnpr-desc">re-memory-utilization.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">RPM Probes</td>
          <td class="jnpr-desc">rpm-probes.yaml</td>
        </tr>

      <tbody>
    </table>

Rows
-------

.. raw:: html

    <table style="width:100%;white-space:normal;" border=1 class="docutils jnpr-table" >
      <thead>
        <tr>
           <th class="jnpr-name">Rows</th>
           <th class="jnpr-desc">File</th>
        </tr>
      <thead>
      <tbody>

        <tr>
          <td class="jnpr-name">CPU / Memory</td>
          <td class="jnpr-desc">cpumem.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Firewall Filters</td>
          <td class="jnpr-desc">firewall.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interfaces Buffer</td>
          <td class="jnpr-desc">int-buffer.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interfaces Queue</td>
          <td class="jnpr-desc">int-queue.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interfaces Traffic Packets</td>
          <td class="jnpr-desc">int-traffic-packets.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interfaces statistics</td>
          <td class="jnpr-desc">int-traffic.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">MPLS LSP</td>
          <td class="jnpr-desc">mpls-lsp.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Disclaimer</td>
          <td class="jnpr-desc">opennti-disclaimer.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">BGP Statistics</td>
          <td class="jnpr-desc">protocol-bgp.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">ISIS Statistics</td>
          <td class="jnpr-desc">protocol-isis.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Queue Stats</td>
          <td class="jnpr-desc">qfx-queue.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">RE Processes</td>
          <td class="jnpr-desc">re-processes.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">RE Statistics</td>
          <td class="jnpr-desc">re-statistics.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">RPM Probes</td>
          <td class="jnpr-desc">rpm-probes.yaml</td>
        </tr>

      <tbody>
    </table>

Annotations
-----------

.. raw:: html

    <table style="width:100%;white-space:normal;" border=1 class="docutils jnpr-table" >
      <thead>
        <tr>
           <th class="jnpr-name">Annotations</th>
           <th class="jnpr-desc">File</th>
        </tr>
      <thead>
      <tbody>

        <tr>
          <td class="jnpr-name">BGP Flap</td>
          <td class="jnpr-desc">bgp_state.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Commit</td>
          <td class="jnpr-desc">commit.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interface Flap</td>
          <td class="jnpr-desc">interface_flap.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">LDP Down</td>
          <td class="jnpr-desc">ldp_down.yaml</td>
        </tr>

      <tbody>
    </table>

Templatings
-----------

.. raw:: html

    <table style="width:100%;white-space:normal;" border=1 class="docutils jnpr-table" >
      <thead>
        <tr>
           <th class="jnpr-name">Annotations</th>
           <th class="jnpr-desc">File</th>
        </tr>
      <thead>
      <tbody>

        <tr>
          <td class="jnpr-name">BGP Flap</td>
          <td class="jnpr-desc">bgp_state.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Commit</td>
          <td class="jnpr-desc">commit.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">Interface Flap</td>
          <td class="jnpr-desc">interface_flap.yaml</td>
        </tr>

        <tr>
          <td class="jnpr-name">LDP Down</td>
          <td class="jnpr-desc">ldp_down.yaml</td>
        </tr>

      <tbody>
    </table>