module Fluent
  class OutMqtt < BufferedOutput
    Plugin.register_output('mqtt', self)

    include Fluent::SetTagKeyMixin
    config_set_default :include_tag_key, false

    include Fluent::SetTimeKeyMixin
    config_set_default :include_time_key, true

    config_param :port, :integer, :default => 1883
    config_param :bind, :string, :default => '127.0.0.1'
    config_param :topic, :string, :default => 'td-agent'
    config_param :format, :string, :default => 'none'
    config_param :username, :string, :default => nil
    config_param :password, :string, :default => nil
    config_param :ssl, :bool, :default => nil
    config_param :ca, :string, :default => nil
    config_param :key, :string, :default => nil
    config_param :cert, :string, :default => nil

    require 'mqtt'

    unless method_defined?(:log)
      define_method(:log) { $log }
    end

    def initialize
      super
      require 'msgpack'

      @clients = {}
      @connection_options = {}
      @collection_options = {:capped => false}
    end

    def configure(conf)
      super
      @bind ||= conf['bind']
      @topic ||= conf['topic']
      @port ||= conf['port']

    end

    def start
      #check buffer_size
      # @buffer.buffer_chunk_limit = available_buffer_chunk_limit

      $log.debug "start mqtt #{@bind}"
      opts = {host: @bind,
              port: @port,
              username: @username,
              password: @password}
      opts[:ssl] = @ssl if @ssl
      opts[:ca_file] = @ca if @ca
      opts[:crt_file] = @crt if @crt
      opts[:key_file] = @key if @key
      @connect = MQTT::Client.connect(opts)
      super
    end

    def shutdown
      @connect.disconnect
      super
    end

    def format(tag, time, record)
      [tag, time, record].to_msgpack
    end

    def write(chunk)

      chunk.msgpack_each do |tag, time, record|
        @connect.publish(topic, record , retain=true)
      end
    end
    #
    # private
    # # Following limits are heuristic. BSON is sometimes bigger than MessagePack and JSON.
    # LIMIT_MQTT = 2 * 1024   # 2048kb
    #
    # def available_buffer_chunk_limit
    #   if @buffer.buffer_chunk_limit > LIMIT_MQTT
    #     log.warn ":buffer_chunk_limit(#{@buffer.buffer_chunk_limit}) is large. Reset :buffer_chunk_limit with #{LIMIT_MQTT}"
    #     LIMIT_MQTT
    #   else
    #     @buffer.buffer_chunk_limit
    #   end
    # end
  end
end
