#!/usr/bin/env python
#
# Copyright (c) Juniper Networks, Inc., 2015-2016.
# All rights reserved.
#
# coding: utf-8
# Authors: psagrera@juniper.net
# Version: 1.0 20150122

import IxNetwork
import os
from time import sleep
import sys
from pprint import pprint

class ContinuableError(RuntimeError):
    ROBOT_CONTINUE_ON_FAILURE = True

class FatalError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True

class pybot_jixia (object):

    # -----------------------------------------------------------------------
    # CONSTRUCTOR
    # -----------------------------------------------------------------------

        def __init__(self,**kvargs):

            self.server = kvargs['ixia_server'] # ixia server currently available 172.30.153.72
            self.ixia_port = kvargs['ixia_port']
            self.ixNet = IxNetwork.IxNet ()
            self.ixNet.setTimeout = 20

    # -----------------------------------------------------------------------
    # METHODS
    # -----------------------------------------------------------------------

        # Function to open a connection to ixia server

        def ixia_connect (self):

            """
                Opens a connection to the device (ixia) using existing server/port
            """
            getVersion = self.ixNet.getVersion()

            try:

               #print "Establishing connection to ixia.......,please be patient"
               #print "Connection established properly"
               return  self.ixNet.connect(self.server,'-port',self.ixia_port,'-version',getVersion, '-clientusername')

            except IxNetwork.IxNetError as ix_conn_err:
                #print " Problems establishing connection to IXIA: %s" % (ix_conn_err)
                raise FatalError("Expected result is True but was False,test will be stopped at this point")
                return False

        # Function to close a connection to the ixia server

        def ixia_disconnect (self):

            """
                Close a connection to the device
            """
            try:

                #print "Closing connection to ixia.......,bye"
                #print self.ixNet.execute('ClearOwnershipForAllPorts')
                return self.ixNet.disconnect ()

            except IxNetwork.IxNetError as ix_conn_err:

                #print "Problems found closing connection to IXIA: %s" % (ix_conn_err)
                raise FatalError("Expected result is True but was False,test will go on")

        # Function to initialize IxNetwork

        def ixia_initialize (self):

            try:
                if self.ixia_return(self.ixNet.execute('newConfig')) is False:
                    print '---- Could not initialize IxNetwork: [NOK]'
                    raise FatalError("Expected result is True but was False,test will stopped")
            except:
                raise FatalError("Expected result is True but was False,test will stopped")

            print '---- IxNetwork initialization: [OK]'

        # Specific function to convert socket return values in boolean

        def ixia_return (self,tclreturn):

            if tclreturn == '::ixNet::OK':
                return True
            else:
                return False

        # Function to start all protocols from ixia

        def start_protocols (self):

            print "Starting protocols......."

            try:
                self.ixNet.execute('startAllProtocols')

            except IxNetwork.IxNetError as ix_start_err:
                print '---- Could not start protocols %s' % (ix_start_err)
                raise FatalError("Expected result is True but was False,test will stopped")

        # Function to running traffic from ixia

        def running_traffic (self):


            traffic = self.ixNet.getList(self.ixNet.getRoot(),'traffic')

            try:
                if self.ixia_return(self.ixNet.execute('apply', traffic[0])) is False:
                    print '---- Could not create stats gathering at IxNetwork: [NOK] %s ' % (ix_run_err)
                    raise FatalError("Expected result is True but was False,test will stopped")

            except IxNetwork.IxNetError as ix_run_err:
                  # Terminate protocols and abort existing connections
                print '---- Could not create stats gathering at IxNetwork: [NOK] %s ' % (ix_run_err)
                raise FatalError("Expected result is True but was False,test will stopped")

            print '---- IxNetwork traffic data gathering infra created: [OK]'

            # Sending stateless traffic
            try:
                if self.ixia_return(self.ixNet.execute('startStatelessTraffic', traffic[0])) is False:
                    print '---- Could not start stateless traffic at IxNetwork: [NOK]'
                    raise FatalError("Expected result is True but was False,test will stopped")

            except IxNetwork.IxNetError as ix_run_err:
                # Terminate protocols and abort existing connections
                print '---- Could not start stateless traffic at IxNetwork: [NOK] %s' % (ix_run_err)
                raise FatalError("Expected result is True but was False,test will stopped")


            print '---- IxNetwork sending stateless traffic started: [OK]'

        # Function to stopping traffic from ixia

        def stopping_traffic (self):

            # Stop sending traffic at IxNetwork

            traffic = self.ixNet.getList(self.ixNet.getRoot(),'traffic')
            print 'Stopping sending 60s traffic at IxNetwork for 2nd test'

            # Stop sending stateless traffic

            try:
                if self.ixia_return(self.ixNet.execute('stopStatelessTraffic', traffic[0])) is False:
                    print '---- Could not stop stateless traffic at IxNetwork: [NOK]'
                    raise FatalError("Expected result is True but was False,test will stopped")
            except IxNetwork.IxNetError as ix_stop_err:
                # Terminate protocols and abort existing connections
                print '---- Could not stop stateless traffic at IxNetwork: [NOK] %s' %(ix_stop_err)
                raise FatalError("Expected result is True but was False,test will stopped")
            print '---- IxNetwork stopping 60s stateless traffic: [OK]'

        # Function to load ixia config file

        def load_config (self,**kvargs):

            print "Loading configuration......."

            file_path = kvargs['ixia_file']

            try:

                if self.ixia_return (self.ixNet.execute('loadConfig',self.ixNet.readFrom(file_path))) is False:
                    sys.exit('---- Could not load IxNetwork config: [NOK]')

            except IxNetwork.IxNetError as ix_conn_err:

                print "Problems loading configuration into IXIA: %s" % (ix_conn_err)
                raise FatalError("Expected result is True but was False,test will go on")

            print '---- IxNetwork config loading: [OK]'


        def stopping_protocols (self):

            print '!!! Stopping protocols'

            try:
                self.ixNet.execute('stopAllProtocols')
            except IxNetwork.IxNetError as ix_stoppro_err:
                print '!!! Could not stop protocols and close existing connections'
                raise FatalError("Expected result is True but was False,test will stopped")

        # Function to gather stats from ixia

        def gather_stats (self, **kwargs):
            view = kwargs['view']
            verbose = True
            if 'verbose' in kwargs.keys():
                verbose = kwargs['verbose']

            try:

                Stats = self.ixNet.getFilteredList(self.ixNet.getRoot()+'statistics', 'view', '-caption', view)
                #print '---- Retrieved IxNetwork loss percentage stats: [OK]'

            except IxNetwork.IxNetError as ix_gather_err:
                #print "Problems gathering stats from IXIA: %s" % (ix_gather_err)
                raise FatalError("Expected result is True but was False,test will go on")

            result = []
            for Stat in Stats:
                tmp = {}
                tmp['columnCaption'] = self.ixNet.getAttribute(Stat+'/page', '-columnCaptions')
                tmp['RowVal'] = self.ixNet.getAttribute(Stat+'/page', '-rowValues')
                result.append(tmp)

            if verbose:
                for tmp in result:
                    print tmp['columnCaption']
                    for tmp2 in tmp['RowVal']:
                        print tmp2
                return True
            else:
                return result


        def clear_stats (self):

            print "Clearing statistics......."

            try:
                self.ixNet.execute('clearStats')

            except IxNetwork.IxNetError as ix_clear_stats_err:
                print '---- Could not clear statistics %s' % (ix_clear_stats_err)
                raise FatalError("Expected result is True but was False,test will stopped")


#kk = pybot_jixia (ixia_server="172.30.153.72",ixia_port=8009)
#kk.ixia_connect ()
#pprint(kk.gather_stats(view='Traffic Item Statistics',verbose=False))
#pprint(kk.gather_stats(view='BGP Aggregated Statistics',verbose=False))
#kk.ixia_disconnect ()#
