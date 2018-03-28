require 'json'
require 'net/http'
require 'uri'

# Upload files in a folder to Elasticsearch using http PUT 
class Provision
  def self.call(input)
    Provision.new(input).provision
  end

  def initialize(input)
    @input = input
  end

  def provision
    $stdout.puts "Provisioning '#{es_base_uri}'..."
    files = Dir.glob("#{input}/**/*.json", File::FNM_DOTMATCH).sort
    files.each { |file| import file }
    $stdout.puts 'Provisioning done.'
  end

  private

  attr_reader :input

  def import(file)
    content = File.read file
    path = to_path(file)
    response = upload(content, path)
    log response, path
  end

  HEADER = { 'Content-Type' => 'application/json' }.freeze

  def es_base_uri
    ENV['ES_BASE_URI'] || 'http://localhost:9200'
  end

  def upload(content, path)
    uri = URI.parse "#{es_base_uri}/#{path}"
    http = Net::HTTP.new(uri.host, uri.port)
    request = Net::HTTP::Put.new(uri.request_uri, HEADER)
    request.body = content
    http.request(request)
  end

  FILE_TO_URI = {
    '_x_' => '*',
    '_;_' => ':'
  }.freeze

  def to_path(file_name)
    path = file_name
    path.slice!("#{input}/")
    path.slice!('.json')
    FILE_TO_URI.each { |k, v| path.sub!(k, v) }
    path
  end

  def log(response, path)
    http_status = response.code.to_i
    if http_status < 200 || http_status > 299
      $stdout.puts "Could not upload '#{path}'", response.to_s, response.body
      raise Net::HTTPBadResponse
    else
      $stdout.puts "Uploaded '#{path}'."
    end
  end
end

Provision.call(ARGV[0] || 'import')

