require 'json'
require 'net/http'
require 'uri'

# Wait for Elasticsearch
class WaitForEs
  def self.call(uri)
    WaitForEs.new(uri).wait
  end

  def initialize(uri)
    safe_uri = uri || ES_BASE_URI
    @uri = URI.parse("#{safe_uri}/_cluster/health")
  end

  def wait
    status = cluster_status
    puts 'Waiting for Elasticsearch to come up...'
    until VALID_STATUS.include? status
      puts "Waiting #{INTERVAL} seconds..."
      sleep INTERVAL
      status = cluster_status
      puts "Status: #{status}."
    end
  end

  private

  attr_reader :uri

  ES_BASE_URI = ENV.fetch('ES_BASE_URI') { 'http://localhost:9200' }.freeze
  HEADER = { 'Content-Type' => 'application/json' }.freeze
  INTERVAL = 5
  VALID_STATUS = %w[yellow green].freeze

  def cluster_status
    http = Net::HTTP.new(uri.host, uri.port)
    request = Net::HTTP::Get.new(uri.request_uri, HEADER)
    begin
      response = http.request(request)
    rescue Errno::ECONNREFUSED
      return 'red'
    end

    return 'red' unless response.code.to_i == 200

    result = JSON.parse(response.body)
    result['status']
  end
end

WaitForEs.call ARGV[0]
