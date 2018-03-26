require 'json'
require 'net/http'
require 'uri'

HEADER = { 'Content-Type' => 'application/json' }.freeze
INTERVAL = 5
VALID_STATUS = %w[yellow green].freeze

def es_base_uri
  ENV['ES_BASE_URI'] || 'http://localhost:9200'
end

def cluster_status
  uri = URI.parse "#{es_base_uri}/_cluster/health"
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

status = cluster_status
puts 'Waiting for Elasticsearch to come up...'
until VALID_STATUS.include? status
  puts "Waiting #{INTERVAL} seconds..."
  sleep INTERVAL
  status = cluster_status
  puts "Status: #{status}."
end
