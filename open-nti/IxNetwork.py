#!/usr/bin/env python

#
# Copyright (c) Juniper Networks, Inc., 2015-2016.
# All rights reserved.
#

import os
import socket
import sys
import time
import select
import getpass

try:
    unicode = unicode
except NameError:
    unicode = str

class IxNetError(Exception):
	"""Default IxNet error"""

class IxNet:
	def __init__(self):
		self._root = str('::ixNet::OBJ-/')
		self._null = str('::ixNet::OBJ-null')
		self._socket = None
		self._proxySocket = None
		self._connectTokens = str()
		self._evalError = '1'
		self._evalSuccess = '0'
		self._evalResult = '0'
		self._addContentSeparator = 0
		self._firstItem = True
		self._sendContent = list()
		self._buffer = False
		self._sendBuffer = list()
		self._decoratedResult = list()
		self._filename = None
		self._debug = False
		self._async = False
		self._timeout = None
		self._OK = '::ixNet::OK'
		self._version = '7.12.860.56'

	def setDebug(self, debug):
		self._debug = debug
		return self

	def getRoot(self):
		return self._root

	def getNull(self):
		return self._null

	def setAsync(self):
		self._async = True;
		return self

	def setTimeout(self, timeout):
		self._timeout = timeout
		return self

	def __initialConnect(self, address, port, options):
		# make an initial socket connection
		# this will keep trying as it could be connecting to the proxy
		# which may not have an available application instance at that time
		attempts = 0
		while True:
			try:
				self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self._socket.connect((address, port))
				break
			except (socket.error,):
				if self._proxySocket is not None and attempts < 120:
					time.sleep(2)
					attempts += 1
				else:
					self.__Close()
					raise IxNetError(str(sys.exc_info()[1]))

		# a socket connection has been made now read the type of connection
		# setup to timeout if the remote endpoint is not valid
		self._socket.setblocking(0)
		read, write, error = select.select([self._socket], [], [], 30)
		if len(read) == 0 and len(write) == 0 and len(error) == 0:
			self.__Close()
			raise IxNetError('Connection handshake timed out after 30 seconds')
		self._socket.setblocking(1)

		# process the results from the endpoint
		connectString = self.__Recv()
		if connectString == 'proxy':
			self._socket.sendall(options)
			self._connectTokens = str(self.__Recv())
			connectTokens = dict(zip(self._connectTokens.split()[::2], self._connectTokens.split()[1::2]))
			self._proxySocket = self._socket
			self._socket = None
			self.__initialConnect(address, int(connectTokens['-port']), '')

	def connect(self, address, *args):
		try:
			nameValuePairs = {}
			name = None
			for arg in args:
				if str(arg).startswith('-'):
					if name is None:
						name = str(arg)
					else:
						nameValuePairs[name] = ''
				elif name != None:
					nameValuePairs[name] = str(arg)
					name = None
			if '-port' not in nameValuePairs:
				nameValuePairs['-port'] = 8009

			options = '-clientusername ' + getpass.getuser()
			if '-serverusername' in nameValuePairs:
				options += ' -serverusername ' + nameValuePairs['-serverusername']
			if '-closeServerOnDisconnect' in nameValuePairs:
				options += ' -closeServerOnDisconnect ' + nameValuePairs[-closeServerOnDisconnect]
			else:
				options += ' -closeServerOnDisconnect true'

			if self._socket is None:
				self.__initialConnect(address, int(nameValuePairs['-port']), options)
				return self.__SendRecv('ixNet', 'connect', address,
					'-clientType', 'python', *args)
			else:
				sockInfo = self._socket.getpeername()
				return "Cannot connect to {0}:{1} as a connection is already established to {2}:{3}. Please execute disconnect before trying this command again.".format(address, int(nameValuePairs['-port']), sockInfo[0], int(sockInfo[1]))
		except (socket.error,):
			e = sys.exc_info()[1]
			self.__Close()
			raise IxNetError("Unable to connect to host:"
				+str(address)+" port:"+str(nameValuePairs['-port'])
				+". Error:"+str(e))

	def disconnect(self):
		response = self.__SendRecv('ixNet', 'disconnect')
		self.__Close()
		return response

	def help(self, *args):
		return self.__SendRecv('ixNet', 'help', *args)

	def setSessionParameter(self, *args):
		if len(args) % 2 == 0:
			return self.__SendRecv('ixNet', 'setSessionParameter', *args)
		else:
			raise IxNetError("setSessionParameter requires an even number of name/value pairs");

	def getVersion(self):
		if self._socket is None:
			return self._version
		else:
			return self.__SendRecv('ixNet', 'getVersion')

	def getParent(self, objRef):
		return self.__SendRecv('ixNet', 'getParent', objRef)

	def exists(self, objRef):
		return self.__SendRecv('ixNet', 'exists', self.__CheckObjRef(objRef))

	def commit(self):
		return self.__SendRecv('ixNet', 'commit')

	def rollback(self):
		return self.__SendRecv('ixNet', 'rollback')

	def execute(self, *args):
		return self.__SendRecv('ixNet', 'exec', *args)

	def add(self, objRef, child, *args):
		return self.__SendRecv('ixNet', 'add', self.__CheckObjRef(objRef), child, *args)

	def remove(self, objRef):
		return self.__SendRecv('ixNet', 'remove', self.__CheckObjRef(objRef))

	def setAttribute(self, objRef, name, value):
		self._buffer = True
		return self.__SendRecv('ixNet', 'setAttribute', self.__CheckObjRef(objRef), name, value)

	def setMultiAttribute(self, objRef, *args):
		self._buffer = True
		return self.__SendRecv('ixNet', 'setMultiAttribute', self.__CheckObjRef(objRef), *args)

	def getAttribute(self, objRef, name):
		return self.__SendRecv('ixNet', 'getAttribute', self.__CheckObjRef(objRef), name)

	def getList(self, objRef, child):
		return self.__SendRecv('ixNet', 'getList', self.__CheckObjRef(objRef), child)

	def getFilteredList(self, objRef, child, name, value):
		return self.__SendRecv('ixNet', 'getFilteredList', self.__CheckObjRef(objRef), child, name, value)

	def adjustIndexes(self, objRef, object):
		return self.__SendRecv('ixNet', 'adjustIndexes', self.__CheckObjRef(objRef), object)

	def remapIds(self, localIdList):
		if type(localIdList) is tuple:
			localIdList = list(localIdList)
		return self.__SendRecv('ixNet', 'remapIds', localIdList)

	def getResult(self, resultId):
		return self.__SendRecv('ixNet', 'getResult', resultId)

	def wait(self, resultId):
		return self.__SendRecv('ixNet', 'wait', resultId)

	def isDone(self, resultId):
		return self.__SendRecv('ixNet', 'isDone', resultId)

	def isSuccess(self, resultId):
		return self.__SendRecv('ixNet', 'isSuccess', resultId)

	def writeTo(self, filename, *args):
		if any(arg == '-ixNetRelative' for arg in args):
			return self.__SendRecv('ixNet', 'writeTo', filename,
				'\02'.join(args))
		else:
			return self.__CreateFileOnServer(filename)

	def readFrom(self, filename, *args):
		if any(arg == '-ixNetRelative' for arg in args):
			return self.__SendRecv('ixNet', 'readFrom', filename,
				'\02'.join(args))
		else:
			return self.__PutFileOnServer(filename)

	def __CheckObjRef(self, objRef):
		if (type(objRef) in (str,unicode)) == False:
			raise IxNetError('The objRef parameter must be ' + str(str) + ' instead of ' + str(type(objRef)))
		else:
			return objRef

	def __PutFileOnServer(self, filename):
		truncatedFilename = os.path.basename(filename)
		fid = open(filename, 'rb')
		self.__Send("<001><005><007{0}>{1}<009{2}>".format(len(filename), filename,os.path.getsize(filename)))
		self.__SendBinary(fid.read())
		fid.close()
		remoteFilename = self.__Recv()

		return self.__SendRecv('ixNet', 'readFrom', remoteFilename,
			'-ixNetRelative')

	def __CreateFileOnServer(self, filename):
		self.__Send("<001><006><007{0}>{1}<009>".format(len(filename), filename))
		remoteFilename = self.__Recv()

		return self.__SendRecv('ixNet', 'writeTo', remoteFilename,
			'-ixNetRelative', '-overwrite')

	def __Close(self):
		try:
			if self._socket:
				self._socket.close()
		finally:
			self._socket = None

	def __Join(self, *args):
		for arg in args:
			if type(arg) is list or type(arg) is tuple:
				if self._addContentSeparator == 0:
					self._sendContent.append('\02')
				if self._addContentSeparator > 0:
					self._sendContent.append('{')
				self._addContentSeparator += 1
				self._firstItem = True
				if len(arg) == 0:
					self._sendContent.append('{}')
				else:
					for item in arg:
						self.__Join(item)
				if self._addContentSeparator > 1:
					self._sendContent.append('}')
				self._addContentSeparator -= 1
			else:
				if self._addContentSeparator == 0 and len(self._sendContent) > 0:
					self._sendContent.append('\02')
				elif self._addContentSeparator > 0:
					if self._firstItem == False:
						self._sendContent.append(' ')
					else:
						self._firstItem = False
				if arg is None:
					arg = ''
				elif type(arg) != str:
					arg = str(arg)
				if len(arg) == 0 and len(self._sendContent) > 0:
					self._sendContent.append('{}')
				elif arg.find(' ') != -1 and self._addContentSeparator > 0:
					self._sendContent.append('{'+arg+'}')
				else:
					self._sendContent.append(arg)

		return

	def __SendRecv(self, *args):
		if self._socket is None:
			raise IxNetError('not connected')

		self._addContentSeparator = 0
		self._firstItem = True

		argList = list(args)

		if self._async:
			argList.insert(1, '-async')

		if self._timeout != None:
			argList.insert(1, '-timeout')
			argList.insert(2, self._timeout)

		for item in argList:
			self.__Join(item)

		self._sendContent.append('\03')
		self._sendBuffer.append("".join(self._sendContent));
		if self._buffer == False:
			buffer = "".join(self._sendBuffer)
			if self._debug:
				print("Sending: ",buffer)
			self.__Send("<001><002><009{0}>{1}".format(len(buffer),
				buffer))
			self._sendBuffer = list()

		self._async = False
		self._timeout = None
		self._buffer = False
		self._sendContent = list()

		if len(self._sendBuffer) > 0:
			return self._OK
		else:
			return self.__Recv()

	def __Send(self, content):
		if self._socket is None:
			raise IxNetError('not connected')
		else:
			try:
				if type(content) is str:
					content = content.encode('ascii')
				self._socket.sendall(content)
			except (socket.error,):
				e = sys.exc_info()[1]
				self.__Close()
				raise IxNetError("Error:"+str(e))

	def __SendBinary(self, content):
		if self._socket is None:
			raise IxNetError('not connected')
		else:
			try:
				self._socket.sendall(content)
			except (socket.error,):
				e = sys.exc_info()[1]
				self.__Close()
				raise IxNetError("Error:"+str(e))

	def __Recv(self):
		self._decoratedResult = list()
		responseBuffer = str()
		try:
			while True:
				responseBuffer = str()
				commandId = None
				contentLength = int(0)

				while True:
					responseBuffer += self._socket.recv(1).decode('ascii')
					startIndex = int(responseBuffer.find('<'))
					stopIndex = int(responseBuffer.find('>'))
					if startIndex != -1 and stopIndex != -1:
						commandId = int(
							responseBuffer[startIndex + 1:startIndex + 4])
						if startIndex + 4 < stopIndex:
							contentLength = int(
								responseBuffer[startIndex + 4:stopIndex])
						break

				if commandId == 1:
					self._evalResult = self._evalError
					self._socket.recv(contentLength)
				elif commandId == 3:
					self._socket.recv(contentLength)
				elif commandId == 4:
					self._evalResult = self._socket.recv(contentLength).decode('ascii')
				elif commandId == 7:
					self._filename = self._socket.recv(contentLength).decode('ascii')
				elif commandId == 8:
					binaryFile = open(self._filename, 'w+b')
					chunk = bytearray()
					bytesToRead = 32767
					while contentLength > 0:
						if contentLength < bytesToRead:
							bytesToRead = contentLength
						chunk = self._socket.recv(bytesToRead)
						binaryFile.write(chunk)
						contentLength -= len(chunk)
					binaryFile.close()
				elif commandId == 9:
					self._decoratedResult = list()
					chunk = str()
					bytesToRead = 32767
					while contentLength > 0:
						if contentLength < bytesToRead:
							bytesToRead = contentLength
						chunk = self._socket.recv(bytesToRead).decode('ascii')
						self._decoratedResult.append(chunk)
						contentLength -= len(chunk)
					break

		except (socket.error,):
			e = sys.exc_info()[1]
			self.__Close()
			raise IxNetError("Recv failed. Error:"+str(e))

		if self._debug:
			print("Received: ", "".join(self._decoratedResult))

		if self._evalResult == self._evalError:
			raise IxNetError("".join(self._decoratedResult))

		if len(self._decoratedResult) > 0 and self._decoratedResult[0].startswith('['):
			return eval("".join(self._decoratedResult))
		else:
			return "".join(self._decoratedResult)
