# encoding: UTF-8
require 'date'
require 'influxdb'

class Fluent::InfluxdbOutput < Fluent::BufferedOutput
    Fluent::Plugin.register_output('influxdb', self)

    include Fluent::HandleTagNameMixin

    config_param :host, :string,  :default => 'localhost'
    config_param :port, :integer,  :default => 8086
    config_param :dbname, :string,  :default => 'fluentd'
    config_param :user, :string,  :default => 'root'
    config_param :password, :string,  :default => 'root', :secret => true
    config_param :time_precision, :string, :default => 's'
    config_param :use_ssl, :bool, :default => false
    config_param :tag_keys, :array, :default => []
    config_param :value_keys, :array, :default => []

    def initialize
        super
    end

    def configure(conf)
        super
        @influxdb = InfluxDB::Client.new @dbname, host: @host,
                                                  port: @port,
                                                  username: @user,
                                                  password: @password,
                                                  async: false,
                                                  time_precision: @time_precision,
                                                  use_ssl: @use_ssl
    end

    def start
        super
    end

    FORMATTED_RESULT_FOR_INVALID_RECORD = ''.freeze

    def format(tag, time, record)
        # TODO: Use tag based chunk separation for more reliability
        if record.empty? || record.has_value?(nil)
            FORMATTED_RESULT_FOR_INVALID_RECORD
        else
            [tag, time, record].to_msgpack
        end
    end

    def shutdown
        super
    end

    def write(chunk)
        points = []
        chunk.msgpack_each do |tag, time, record|
            point = {}
            point[:timestamp] = record.delete('time') || time
            point[:series] = tag

            if ( tag_keys.empty? && value_keys.empty? )
                point[:values] = record
            elsif !tag_keys.empty?
                point[:tags] = record.select{|k,v| @tag_keys.include?(k)}
                point[:values] = record.select{|k,v| !@tag_keys.include?(k)}
            elsif !value_keys.empty?
                point[:values] = record.select{|k,v| @value_keys.include?(k)}
                point[:tags] = record.select{|k,v| !@value_keys.include?(k)}
            end
            points << point
        end

        @influxdb.write_points(points)
    end
end
