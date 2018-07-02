# encoding: UTF-8
require 'date'
require 'influxdb'
require 'fluent/output'
require 'fluent/mixin'

class Fluent::InfluxdbOutput < Fluent::BufferedOutput
  Fluent::Plugin.register_output('influxdb', self)

  include Fluent::HandleTagNameMixin

  config_param :host, :string,  :default => 'localhost',
               :desc => "The IP or domain of influxDB, separate with comma."
  config_param :port, :integer,  :default => 8086,
               :desc => "The HTTP port of influxDB."
  config_param :dbname, :string,  :default => 'fluentd',
               :desc => <<-DESC
The database name of influxDB.
You should create the database and grant permissions at first.
DESC
  config_param :measurement, :string, :default => nil,
               :desc => "The measurement name to insert events. If not specified, fluentd's tag is used"
  config_param :user, :string,  :default => 'root',
               :desc => "The DB user of influxDB, should be created manually."
  config_param :password, :string,  :default => 'root', :secret => true,
               :desc => "The password of the user."
  config_param :retry, :integer, :default => nil,
               :desc => 'The finite number of retry times. default is infinite'
  config_param :time_key, :string, :default => 'time',
               :desc => 'Use value of this tag if it exists in event instead of event timestamp'
  config_param :time_precision, :string, :default => 's',
               :desc => <<-DESC
The time precision of timestamp.
You should specify either hour (h), minutes (m), second (s),
millisecond (ms), microsecond (u), or nanosecond (ns).
DESC
  config_param :use_ssl, :bool, :default => false,
               :desc => "Use SSL when connecting to influxDB."
  config_param :verify_ssl, :bool, :default => true,
               :desc => "Enable/Disable SSL Certs verification when connecting to influxDB via SSL."
  config_param :auto_tags, :bool, :default => false,
               :desc => "Enable/Disable auto-tagging behaviour which makes strings tags."
  config_param :tag_keys, :array, :default => [],
               :desc => "The names of the keys to use as influxDB tags."
  config_param :tag_keys_field, :string, :default => nil,
               :desc => "The names of the fields where influxdb key names are stored"
  config_param :sequence_tag, :string, :default => nil,
               :desc => <<-DESC
The name of the tag whose value is incremented for the consecutive simultaneous
events and reset to zero for a new event with the different timestamp.
DESC
  config_param :retention_policy_key, :string, :default => nil,
               :desc => "The key of the key in the record that stores the retention policy name"
  config_param :default_retention_policy, :string, :default => nil,
               :desc => "The name of the default retention policy"


  def initialize
    super
    @seq = 0
    @prev_timestamp = nil
  end

  def configure(conf)
    super
    @time_precise = time_precise_lambda()
  end

  def start
    super

    $log.info "Connecting to database: #{@dbname}, host: #{@host}, port: #{@port}, username: #{@user}, use_ssl = #{@use_ssl}, verify_ssl = #{@verify_ssl}"

    # ||= for testing.
    @influxdb ||= InfluxDB::Client.new @dbname, hosts: @host.split(','),
                                                port: @port,
                                                username: @user,
                                                password: @password,
                                                async: false,
                                                retry: @retry,
                                                time_precision: @time_precision,
                                                use_ssl: @use_ssl,
                                                verify_ssl: @verify_ssl

    begin
      existing_databases = @influxdb.list_databases.map { |x| x['name'] }
      unless existing_databases.include? @dbname
        raise Fluent::ConfigError, 'Database ' + @dbname + ' doesn\'t exist. Create it first, please. Existing databases: ' + existing_databases.join(',')
      end
    rescue InfluxDB::AuthenticationError, InfluxDB::Error
      $log.info "skip database presence check because '#{@user}' user doesn't have admin privilege. Check '#{@dbname}' exists on influxdb"
    end
  end

  FORMATTED_RESULT_FOR_INVALID_RECORD = ''.freeze

  def format(tag, time, record)
    # TODO: Use tag based chunk separation for more reliability
    if record.empty? || record.has_value?(nil)
      FORMATTED_RESULT_FOR_INVALID_RECORD
    else
      [tag, precision_time(time), record].to_msgpack
    end
  end

  def shutdown
    super
    @influxdb.stop!
  end

  def write(chunk)
    points = []
    chunk.msgpack_each do |tag, time, record|
      timestamp = record.delete(@time_key) || time
      if tag_keys.empty? && !@auto_tags
        values = record
        tags = {}
      else
        values = {}
        tags = {}
        record.each_pair do |k, v|
          if (@auto_tags && v.is_a?(String)) || @tag_keys.include?(k)
            # If the tag value is not nil, empty, or a space, add the tag
            if v.to_s.strip != ''
              tags[k] = v
            end
          else
            values[k] = v
          end
        end
      end
      if !@tag_keys_field.nil? && record.include?(tag_keys_field)
        tags.update(record[tag_keys_field])
        values.delete(tag_keys_field)
      end
      if @sequence_tag
        if @prev_timestamp == timestamp
          @seq += 1
        else
          @seq = 0
        end
        tags[@sequence_tag] = @seq
        @prev_timestamp = timestamp
      end

      if values.empty?
          log.warn "Skip record '#{record}', because InfluxDB requires at least one value in raw"
          next
      end

      point = {
        :timestamp => timestamp,
        :series    => @measurement || tag,
        :values    => values,
        :tags      => tags,
      }
      retention_policy = @default_retention_policy
      unless @retention_policy_key.nil?
        retention_policy = record.delete(@retention_policy_key) || @default_retention_policy
        unless points.nil?
          if retention_policy != @default_retention_policy
            # flush the retention policy first
            @influxdb.write_points(points, nil, @default_retention_policy)
            points = nil
          end
        end
      end
      if points.nil?
        @influxdb.write_points([point], nil, retention_policy)
      else
        points << point
      end
    end

    unless points.nil?
      if @default_retention_policy.nil?
        @influxdb.write_points(points)
      else
        @influxdb.write_points(points, nil, @default_retention_policy)
      end
    end
  end

  def time_precise_lambda()
    case @time_precision.to_sym
    when :h then
      lambda{|nstime| nstime / (10 ** 9) / (60 ** 2) }
    when :m then
      lambda{|nstime| nstime / (10 ** 9) / 60 }
    when :s then
      lambda{|nstime| nstime / (10 ** 9) }
    when :ms then
      lambda{|nstime| nstime / (10 ** 6) }
    when :u then
      lambda{|nstime| nstime / (10 ** 3) }
    when :ns then
      lambda{|nstime| nstime }
    else
      raise Fluent::ConfigError, 'time_precision ' + @time_precision + ' is invalid.' +
        'should specify either either hour (h), minutes (m), second (s), millisecond (ms), microsecond (u), or nanosecond (ns)'
    end
  end

  def precision_time(time)
    # nsec is supported from v0.14
    nstime = time * (10 ** 9) + (defined?(Fluent::EventTime) ? time.nsec : 0)
    @time_precise.call(nstime)
  end
end
