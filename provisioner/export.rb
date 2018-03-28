require 'json'
require 'net/http'
require 'uri'
require 'fileutils'

# Export Elasticsearch index as a folder
class Export
  def self.call(index, output)
    Export.new(index, output).export
  end

  def initialize(index, output)
    @index = index
    @output = output
  end

  def export
    $stdout.puts "Exporting '#{es_base_uri}/#{index}' to #{output}..."
    fetch_docs.each { |doc| save doc }
    $stdout.puts 'Exporting done.'
  end

  private

  attr_reader :index, :output

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
    docs.sort_by { |hit| hit.dig('_id') }
  end

  def save(doc)
    id = doc['_id']
    URI_TO_FILE.each { |k, v| id.sub!(k, v) }
    path = "#{output}/#{doc['_index']}/#{doc['_type']}"
    FileUtils.mkdir_p path
    file_name = "#{path}/#{id}.json"
    File.write file_name, JSON.pretty_generate(doc['_source'])
    puts "Saved #{file_name}."
  end

  URI_TO_FILE = {
    '*' => '_x_',
    ':' => '_;_'
  }.freeze

  def to_file_name(doc)
    file_name = doc['_id']
    URI_TO_FILE.each { |k, v| file_name.sub!(k, v) }
    "#{path}/#{doc['_index']}/#{doc['_type']}/#{file_name}}"
  end
end

Export.call(ARGV[0] || '.kibana', ARGV[1] || 'export')
