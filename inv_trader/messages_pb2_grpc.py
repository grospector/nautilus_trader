# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import messages_pb2 as messages__pb2


class DataServerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.OnSubscribeTickData = channel.unary_unary(
        '/invariance_proto.DataServer/OnSubscribeTickData',
        request_serializer=messages__pb2.SubscribeTickData.SerializeToString,
        response_deserializer=messages__pb2.SubscribeTickDataResponse.FromString,
        )
    self.OnSubscribeBarData = channel.unary_unary(
        '/invariance_proto.DataServer/OnSubscribeBarData',
        request_serializer=messages__pb2.SubscribeBarData.SerializeToString,
        response_deserializer=messages__pb2.SubscribeBarDataResponse.FromString,
        )
    self.OnUnsubscribeTickData = channel.unary_unary(
        '/invariance_proto.DataServer/OnUnsubscribeTickData',
        request_serializer=messages__pb2.UnsubscribeTickData.SerializeToString,
        response_deserializer=messages__pb2.UnsubscribeTickDataResponse.FromString,
        )
    self.OnUnsubscribeBarData = channel.unary_unary(
        '/invariance_proto.DataServer/OnUnsubscribeBarData',
        request_serializer=messages__pb2.UnsubscribeBarData.SerializeToString,
        response_deserializer=messages__pb2.UnsubscribeBarDataResponse.FromString,
        )


class DataServerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def OnSubscribeTickData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def OnSubscribeBarData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def OnUnsubscribeTickData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def OnUnsubscribeBarData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DataServerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'OnSubscribeTickData': grpc.unary_unary_rpc_method_handler(
          servicer.OnSubscribeTickData,
          request_deserializer=messages__pb2.SubscribeTickData.FromString,
          response_serializer=messages__pb2.SubscribeTickDataResponse.SerializeToString,
      ),
      'OnSubscribeBarData': grpc.unary_unary_rpc_method_handler(
          servicer.OnSubscribeBarData,
          request_deserializer=messages__pb2.SubscribeBarData.FromString,
          response_serializer=messages__pb2.SubscribeBarDataResponse.SerializeToString,
      ),
      'OnUnsubscribeTickData': grpc.unary_unary_rpc_method_handler(
          servicer.OnUnsubscribeTickData,
          request_deserializer=messages__pb2.UnsubscribeTickData.FromString,
          response_serializer=messages__pb2.UnsubscribeTickDataResponse.SerializeToString,
      ),
      'OnUnsubscribeBarData': grpc.unary_unary_rpc_method_handler(
          servicer.OnUnsubscribeBarData,
          request_deserializer=messages__pb2.UnsubscribeBarData.FromString,
          response_serializer=messages__pb2.UnsubscribeBarDataResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'invariance_proto.DataServer', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class DataClientStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.OnHeartBeatRequest = channel.unary_unary(
        '/invariance_proto.DataClient/OnHeartBeatRequest',
        request_serializer=messages__pb2.HeartBeat.SerializeToString,
        response_deserializer=messages__pb2.HeartBeat.FromString,
        )
    self.OnTickData = channel.unary_unary(
        '/invariance_proto.DataClient/OnTickData',
        request_serializer=messages__pb2.Tick.SerializeToString,
        response_deserializer=messages__pb2.Empty.FromString,
        )
    self.OnBarData = channel.unary_unary(
        '/invariance_proto.DataClient/OnBarData',
        request_serializer=messages__pb2.BarData.SerializeToString,
        response_deserializer=messages__pb2.Empty.FromString,
        )


class DataClientServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def OnHeartBeatRequest(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def OnTickData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def OnBarData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DataClientServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'OnHeartBeatRequest': grpc.unary_unary_rpc_method_handler(
          servicer.OnHeartBeatRequest,
          request_deserializer=messages__pb2.HeartBeat.FromString,
          response_serializer=messages__pb2.HeartBeat.SerializeToString,
      ),
      'OnTickData': grpc.unary_unary_rpc_method_handler(
          servicer.OnTickData,
          request_deserializer=messages__pb2.Tick.FromString,
          response_serializer=messages__pb2.Empty.SerializeToString,
      ),
      'OnBarData': grpc.unary_unary_rpc_method_handler(
          servicer.OnBarData,
          request_deserializer=messages__pb2.BarData.FromString,
          response_serializer=messages__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'invariance_proto.DataClient', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
