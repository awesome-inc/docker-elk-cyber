require 'json'
require 'net/http'
require 'uri'

# Export Elasticsearch index as a folder
class Export
  def self.call(index, path)
    Export.new(index, path).export
  end

  def initialize(index, path)
    @index = index || '.kibana'
    @path = path || 'export'
  end

  def export
    $stdout.puts "Exporting '#{es_base_uri}/#{index}' to #{path}..."
    docs = fetch_docs
    docs.each { |doc| save doc }
    $stdout.puts 'Exporting done.'
  end

  private

  attr_reader :index, :path

  HEADER = { 'Content-Type' => 'application/json' }.freeze

  def es_base_uri
    ENV['ES_BASE_URI'] || 'http://localhost:9200'
  end

  def fetch_docs
    uri = URI.parse "#{es_base_uri}/#{index}/_search?size=1000"
    http = Net::HTTP.new(uri.host, uri.port)
    request = Net::HTTP::Get.new(uri.request_uri, HEADER)
    res = http.request(request)
    body = JSON.parse(res.body)
    docs = body.dig('hits', 'hits')
    docs
  end

  def save(doc)
    puts "Saving #{doc}..."
  end

  FILE_TO_URI = {
    '_x_' => '*',
    '_;_' => ':'
  }.freeze

  def to_path(file_name)
    path = file_name
    path.slice!("#{PATH}/")
    path.slice!('.json')
    FILE_TO_URI.each { |k,v| path.sub!(k,v) }
    path
  end
end

Export.call(ARGV[0] || '.kibana', ARGV[1] || 'export')
